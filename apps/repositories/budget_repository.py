from .. import db
from ..models.budget import Budget


class BudgetRepository:
    @staticmethod
    def query_by_user(user_id):
        return Budget.query.filter_by(user_id=user_id)

    @staticmethod
    def get_by_id(budget_id, user_id):
        return Budget.query.filter_by(id=budget_id, user_id=user_id).first_or_404()

    @staticmethod
    def add(budget):
        db.session.add(budget)

    @staticmethod
    def delete(budget):
        db.session.delete(budget)
