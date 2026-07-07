from .. import db
from ..models.income import Income


class IncomeRepository:
    @staticmethod
    def query_by_user(user_id):
        return Income.query.filter_by(user_id=user_id)

    @staticmethod
    def get_by_id(income_id, user_id):
        return Income.query.filter_by(id=income_id, user_id=user_id).first_or_404()

    @staticmethod
    def add(income):
        db.session.add(income)

    @staticmethod
    def delete(income):
        db.session.delete(income)
