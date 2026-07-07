from .. import db
from ..models.user import User


class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def email_or_username_exists(email, username):
        return User.query.filter((User.email == email) | (User.username == username)).first() is not None

    @staticmethod
    def add(user):
        db.session.add(user)

    @staticmethod
    def delete(user):
        db.session.delete(user)
