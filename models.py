from sqlalchemy import Table, Column, Integer, String, ForeignKey, Float
from database import metadata

users = Table(
  'users',
  metadata,
  Column('id', Integer, primary_key=True),
  Column('username', String, nullable=False, unique=True)
)

transactions = Table(
  'transactions',
  metadata,
  Column('id', Integer, primary_key=True),
  Column('amount', Float, nullable=False),
  Column('type', String, nullable=False),
  Column('user_id', Integer, ForeignKey('users.id'), nullable=False)
)
