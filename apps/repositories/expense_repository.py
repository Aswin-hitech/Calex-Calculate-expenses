from .. import db
from ..models.expense import Expense


class ExpenseRepository:
    @staticmethod
    def query_by_user(user_id):
        return Expense.query.filter_by(user_id=user_id)

    @staticmethod
    def get_by_id(expense_id, user_id):
        return Expense.query.filter_by(id=expense_id, user_id=user_id).first_or_404()

    @staticmethod
    def add(expense):
        db.session.add(expense)

    @staticmethod
    def delete(expense):
        db.session.delete(expense)

    @staticmethod
    def delete_all_for_user(user_id):
        Expense.query.filter_by(user_id=user_id).delete()
