from pydantic import BaseModel
from typing import List


class UserBase(BaseModel):
  username: str


class UserCreate(UserBase):
  pass


class TransactionBase(BaseModel):
  amount: float
  type: str
  user_id: int


class TransactionCreate(TransactionBase):
  pass


class Transaction(TransactionBase):
  id: int

  class Config:
    orm_mode = True


class User(UserBase):
  id: int
  transactions: List[Transaction] = []

  class Config:
    orm_mode = True
