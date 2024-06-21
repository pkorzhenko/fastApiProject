from typing import List

from fastapi import FastAPI, HTTPException
from database import database
from models import users, transactions
from schemas import User, UserCreate, Transaction, TransactionCreate
from admin import admin_app

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.mount("/admin", admin_app)


@app.post("/add_user/", response_model=dict)
async def add_user(user: UserCreate):
    query = users.insert().values(username=user.username)
    try:
        last_record_id = await database.execute(query)
        return {"id": last_record_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Username already exists")


@app.get("/get_user/{user_id}", response_model=User)
async def get_user(user_id: int):
    query = users.select().where(users.c.id == user_id)
    user = await database.fetch_one(query)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    transaction_query = transactions.select().where(transactions.c.user_id == user_id)
    user_transactions = await database.fetch_all(transaction_query)
    return {**user, "transactions": user_transactions}


@app.get("/get_all_users/", response_model=List[User])
async def get_all_users():
    query = users.select()
    all_users = await database.fetch_all(query)

    result = []
    for user in all_users:
        transaction_query = transactions.select().where(transactions.c.user_id == user["id"])
        user_transactions = await database.fetch_all(transaction_query)
        result.append({**user, "transactions": user_transactions})

    return result


@app.post("/add_transaction/", response_model=dict)
async def add_transaction(transaction: TransactionCreate):
    query = transactions.insert().values(amount=transaction.amount, type=transaction.type, user_id=transaction.user_id)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}
