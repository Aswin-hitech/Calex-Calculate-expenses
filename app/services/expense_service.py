from datetime import datetime
from decimal import Decimal

from .. import db
from ..models.expense import Expense
from ..repositories.expense_repository import ExpenseRepository


class ExpenseService:
    @staticmethod
    def list_for_user(user_id, sort_by='entry_date', order='desc'):
        sort_map = {
            'entry_date': Expense.entry_date,
            'amount': Expense.amount,
            'category': Expense.category,
        }
        sort_column = sort_map.get(sort_by, Expense.entry_date)
        sort_column = sort_column.desc() if order != 'asc' else sort_column.asc()
        return ExpenseRepository.query_by_user(user_id).order_by(sort_column)

    @staticmethod
    def parse_date(value):
        if not value:
            return None
        return datetime.strptime(value, '%Y-%m-%d').date()

    @staticmethod
    def parse_amount(value):
        if value in (None, ''):
            raise ValueError('Amount is required.')
        amount = Decimal(value)
        if amount < 0:
            raise ValueError('Amount cannot be negative.')
        return amount

    @staticmethod
    def normalize_text(value):
        value = (value or '').strip()
        return value or None

    @staticmethod
    def normalize_tags(value):
        value = (value or '').strip()
        if not value:
            return None
        tags = [item.strip().lower() for item in value.split(',') if item.strip()]
        return ', '.join(tags) if tags else None

    @staticmethod
    def create_expense(user_id, form, attachment_path=None):
        expense = Expense(
            user_id=user_id,
            entry_date=ExpenseService.parse_date(form.get('entry_date')) or datetime.utcnow().date(),
            category=ExpenseService.normalize_text(form.get('category')),
            description=ExpenseService.normalize_text(form.get('description')),
            tags=ExpenseService.normalize_tags(form.get('tags')),
            amount=ExpenseService.parse_amount(form.get('amount')),
            payment_method=ExpenseService.normalize_text(form.get('payment_method')),
            location=ExpenseService.normalize_text(form.get('location')),
            notes=ExpenseService.normalize_text(form.get('notes')),
            attachment_path=attachment_path,
        )
        if not expense.category:
            raise ValueError('Category is required.')
        ExpenseRepository.add(expense)
        db.session.commit()
        return expense

    @staticmethod
    def update_expense(expense, form, attachment_path=None):
        expense.entry_date = ExpenseService.parse_date(form.get('entry_date')) or expense.entry_date
        expense.category = ExpenseService.normalize_text(form.get('category')) or expense.category
        expense.description = ExpenseService.normalize_text(form.get('description'))
        expense.tags = ExpenseService.normalize_tags(form.get('tags'))
        expense.amount = ExpenseService.parse_amount(form.get('amount'))
        expense.payment_method = ExpenseService.normalize_text(form.get('payment_method'))
        expense.location = ExpenseService.normalize_text(form.get('location'))
        expense.notes = ExpenseService.normalize_text(form.get('notes'))
        if attachment_path:
            expense.attachment_path = attachment_path
        db.session.commit()
        return expense

    @staticmethod
    def delete_expense(expense):
        ExpenseRepository.delete(expense)
        db.session.commit()

    @staticmethod
    def delete_all_for_user(user_id):
        ExpenseRepository.delete_all_for_user(user_id)
        db.session.commit()
