from typing import List

from fastapi import Depends, HTTPException
from models import User, Transaction, User_Pydantic, UserIn_Pydantic, Transaction_Pydantic, TransactionIn_Pydantic
from tortoise.transactions import in_transaction
from starlette.requests import Request

from fastapi_admin.app import app as admin_app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates

from main import app_ as app


@admin_app.get("/admin")
async def home(
    request: Request,
    resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard",
        },
    )


@app.post("/add_user/", response_model=dict)
async def add_user(user: UserIn_Pydantic):
    try:
        user_obj = await User.create(**user.dict())
        return {"id": user_obj.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Username already exists")


@app.get("/get_user/{user_id}", response_model=User_Pydantic)
async def get_user(user_id: int):
    user = await User_Pydantic.from_queryset_single(User.get(id=user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_transactions = Transaction_Pydantic.from_queryset(user=user)
    return {**user, "transactions": user_transactions}


@app.get("/get_all_users/", response_model=List[User_Pydantic])
async def get_all_users():
    users = await User_Pydantic.from_queryset(User.all())

    result = []
    for user in users:
        user_transactions = Transaction_Pydantic.from_queryset(user=user)
        result.append({**user, "transactions": user_transactions})

    return result


@app.post("/add_transaction/", response_model=dict)
async def add_transaction(transaction: TransactionIn_Pydantic):
    async with in_transaction() as conn:
        transaction_obj = await Transaction.create(**transaction.dict(), using_db=conn)
        return {"id": transaction_obj.id}
