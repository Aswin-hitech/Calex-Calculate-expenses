from datetime import datetime
from decimal import Decimal

from .. import db
from ..models.income import Income
from ..repositories.income_repository import IncomeRepository


class IncomeService:
    @staticmethod
    def list_for_user(user_id):
        return IncomeRepository.query_by_user(user_id).order_by(Income.entry_date.desc())

    @staticmethod
    def parse_date(value):
        if not value:
            return None
        return datetime.strptime(value, '%Y-%m-%d').date()

    @staticmethod
    def parse_amount(value):
        amount = Decimal(value)
        if amount < 0:
            raise ValueError('Amount cannot be negative.')
        return amount

    @staticmethod
    def normalize_text(value):
        value = (value or '').strip()
        return value or None

    @staticmethod
    def create_income(user_id, form):
        source = IncomeService.normalize_text(form.get('source'))
        if not source:
            raise ValueError('Source is required.')
        income = Income(
            user_id=user_id,
            entry_date=IncomeService.parse_date(form.get('entry_date')) or datetime.utcnow().date(),
            source=source,
            amount=IncomeService.parse_amount(form.get('amount')),
            notes=IncomeService.normalize_text(form.get('notes')),
        )
        IncomeRepository.add(income)
        db.session.commit()
        return income

    @staticmethod
    def update_income(income, form):
        source = IncomeService.normalize_text(form.get('source'))
        if not source:
            raise ValueError('Source is required.')
        income.entry_date = IncomeService.parse_date(form.get('entry_date')) or income.entry_date
        income.source = source
        income.amount = IncomeService.parse_amount(form.get('amount'))
        income.notes = IncomeService.normalize_text(form.get('notes'))
        db.session.commit()
        return income

    @staticmethod
    def delete_income(income):
        IncomeRepository.delete(income)
        db.session.commit()
