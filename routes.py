from fastapi import Depends, HTTPException
from models import User, Transaction, User_Pydantic, UserIn_Pydantic, Transaction_Pydantic, TransactionIn_Pydantic
from tortoise.transactions import in_transaction
from starlette.requests import Request

from fastapi_admin.app import app as admin_app
from fastapi_admin.depends import get_resources, get_current_admin
from fastapi_admin.template import templates

from utils import get_statistics


@admin_app.get("/")
async def home(
  request: Request,
  resources=Depends(get_resources),
):
    total_transactions, total_amount, dates, amounts = await get_statistics()
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "total_transactions": total_transactions,
            "total_amount": total_amount,
            "dates": dates,
            "amounts": amounts,
            "resource_label": "Dashboard",
            "page_pre_title": "overview",
            "page_title": "Dashboard",
        },
    )


async def add_user(user: UserIn_Pydantic):
    async with in_transaction() as conn:
        try:
            user_obj = await User.create(**user.dict(), using_db=conn)
            return {"id": user_obj.id}
        except:
            raise HTTPException(status_code=400, detail="Username already exists")


async def get_user(user_id: int):
    try:
        user = await User_Pydantic.from_queryset_single(User.get(id=user_id))
    except:
        raise HTTPException(status_code=404, detail="User not found")

    user_dict = user.dict()
    user_transactions = await Transaction_Pydantic.from_queryset(Transaction.filter(user_id=user.id))
    return {**user_dict, "transactions": user_transactions}


async def get_all_users():
    users = await User_Pydantic.from_queryset(User.all())

    result = []
    for user in users:
        user_dict = user.dict()
        user_transactions = await Transaction_Pydantic.from_queryset(Transaction.filter(user_id=user.id))
        result.append({**user_dict, "transactions": user_transactions})

    return result


async def add_transaction(user_id: int, transaction: TransactionIn_Pydantic):
    transaction_dict = transaction.dict()
    async with in_transaction() as conn:
        try:
            transaction_obj = await Transaction.create(
                **transaction_dict,
                user_id=user_id,
                using_db=conn
            )
            return {"id": transaction_obj.id}
        except:
            raise HTTPException(status_code=404, detail="User not found")
