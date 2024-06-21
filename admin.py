import os
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Model
from fastapi_admin.widgets import displays, inputs
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from database import database, engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False, unique=True)


class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)


async def create_admin():
    app = FastAPI()
    admin_app.init(
        app,
        admin_secret=os.getenv("ADMIN_SECRET"),
        providers=[
            UsernamePasswordProvider(
                admin_model=User,
                login_logo_url="https://example.com/logo.png",
            )
        ],
    )
    admin_app.register(
        Model(User, icon="fa fa-users", label="Users"),
        Model(Transaction, icon="fa fa-money", label="Transactions"),
    )
    return app

admin_app = create_admin()
