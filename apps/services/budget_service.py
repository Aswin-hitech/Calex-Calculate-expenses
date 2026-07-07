from datetime import datetime
from decimal import Decimal

from .. import db
from ..models.budget import Budget
from ..repositories.budget_repository import BudgetRepository


class BudgetService:
    @staticmethod
    def list_for_user(user_id):
        return BudgetRepository.query_by_user(user_id).order_by(Budget.month.desc())

    @staticmethod
    def parse_month(value):
        return datetime.strptime(value, '%Y-%m').date().replace(day=1)

    @staticmethod
    def parse_amount(value):
        amount = Decimal(value)
        if amount < 0:
            raise ValueError('Total amount cannot be negative.')
        return amount

    @staticmethod
    def normalize_text(value):
        value = (value or '').strip()
        return value or None

    @staticmethod
    def create_budget(user_id, form):
        month_str = form.get('month')
        total_amount = form.get('total_amount')
        if not month_str or not total_amount:
            raise ValueError('Month and total amount are required.')
        budget = Budget(
            user_id=user_id,
            month=BudgetService.parse_month(month_str),
            total_amount=BudgetService.parse_amount(total_amount),
            category=BudgetService.normalize_text(form.get('category')),
            used_amount=0,
        )
        BudgetRepository.add(budget)
        db.session.commit()
        return budget

    @staticmethod
    def update_budget(budget, form):
        month_str = form.get('month')
        total_amount = form.get('total_amount')
        category = form.get('category')
        if month_str:
            budget.month = BudgetService.parse_month(month_str)
        if total_amount:
            budget.total_amount = BudgetService.parse_amount(total_amount)
        budget.category = BudgetService.normalize_text(category) or budget.category
        db.session.commit()
        return budget

    @staticmethod
    def delete_budget(budget):
        BudgetRepository.delete(budget)
        db.session.commit()
