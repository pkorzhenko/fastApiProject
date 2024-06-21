import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from dotenv import load_dotenv
from tortoise.contrib.fastapi import register_tortoise

from constants import BASE_DIR
from models import Admin
from providers import LoginProvider
from fastapi_admin.app import app as admin_app
from fastapi_admin.exceptions import (
    forbidden_error_exception,
    not_found_error_exception,
    server_error_exception,
    unauthorized_error_exception,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    r = redis.from_url(
        os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        decode_responses=True,
        encoding="utf8",
    )
    await admin_app.configure(
        logo_url="https://preview.tabler.io/static/logo-white.svg",
        template_folders=[os.path.join(BASE_DIR, "templates")],
        favicon_url="https://raw.githubusercontent.com/fastapi-admin/fastapi-admin/dev/images/favicon.png",
        providers=[
            LoginProvider(
                login_logo_url="https://preview.tabler.io/static/logo.svg",
                admin_model=Admin,
            )
        ],
        redis=r,
    )
    yield


def create_app():
    app = FastAPI(lifespan=lifespan)
    app.mount(
        "/static",
        StaticFiles(directory=os.path.join(BASE_DIR, "static")),
        name="static",
    )

    admin_app.add_exception_handler(HTTP_500_INTERNAL_SERVER_ERROR, server_error_exception)
    admin_app.add_exception_handler(HTTP_404_NOT_FOUND, not_found_error_exception)
    admin_app.add_exception_handler(HTTP_403_FORBIDDEN, forbidden_error_exception)
    admin_app.add_exception_handler(HTTP_401_UNAUTHORIZED, unauthorized_error_exception)

    app.mount("/admin", admin_app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )
    register_tortoise(
        app,
        db_url=os.getenv('DATABASE_URL'),
        modules={"models": ["models"]},
        generate_schemas=True,
    )
    return app


app_ = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app_", reload=True)
