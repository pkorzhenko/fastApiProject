from models import Transaction
from tortoise.functions import Sum
from tortoise.expressions import RawSQL

from datetime import datetime, timedelta


async def get_statistics():
  total_transactions = await Transaction.all().count()
  total_amount = await Transaction.annotate(total=Sum("amount")).values("total")
  total_amount_value = total_amount[0]["total"] if total_amount else 0

  # Get transactions for the last 7 days
  today = datetime.today()
  start_date = today - timedelta(days=6)
  transactions = await Transaction.filter(created_at__gte=start_date).annotate(day=RawSQL("DATE(created_at)")).group_by('day').annotate(total=Sum('amount')).values('day', 'total')

  dates = [(start_date + timedelta(days=i)).strftime("%d/%m") for i in range(7)]
  amounts = [0] * 7
  for transaction in transactions:
    day_index = (transaction['day'] - start_date.date()).days
    amounts[day_index] = transaction['total']

  return total_transactions, total_amount_value, dates, amounts
