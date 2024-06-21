import datetime

from fastapi_admin.models import AbstractAdmin

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class User(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True)
    created_at = fields.DatetimeField(auto_now_add=True)


class Transaction(models.Model):
    id = fields.IntField(pk=True)
    amount = fields.FloatField()
    type = fields.CharField(max_length=50)
    user = fields.ForeignKeyField('models.User', related_name='transactions')
    created_at = fields.DatetimeField(auto_now_add=True)


class Admin(AbstractAdmin):
    last_login = fields.DatetimeField(description="Last Login", default=datetime.datetime.now)
    email = fields.CharField(max_length=200, default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"


User_Pydantic = pydantic_model_creator(User, name="User")
UserIn_Pydantic = pydantic_model_creator(
    User, name="UserIn",
    exclude_readonly=True,
    exclude=('id', 'created_at')
)

Transaction_Pydantic = pydantic_model_creator(Transaction, name="Transaction")
TransactionIn_Pydantic = pydantic_model_creator(
    Transaction, name="TransactionIn",
    exclude_readonly=True,
    exclude=('id', 'created_at')
)
