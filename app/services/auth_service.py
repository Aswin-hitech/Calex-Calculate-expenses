from dataclasses import dataclass

from flask_login import login_user, logout_user

from .. import db
from ..models.user import User
from ..repositories.user_repository import UserRepository
from .security_service import SecurityService


class AuthService:
    @staticmethod
    def register_user(email: str, username: str, password: str) -> User:
        if not SecurityService.password_is_valid(password):
            raise ValueError('Password must be at least 8 characters and include upper, lower, and numeric characters.')
        if UserRepository.email_or_username_exists(email, username):
            raise ValueError('User with that email or username already exists.')
        user = User(email=email, username=username)
        user.set_password(password)
        UserRepository.add(user)
        db.session.commit()
        SecurityService.create_email_verification_token(user.id)
        return user

    @staticmethod
    def authenticate(email: str, password: str):
        user = UserRepository.get_by_email(email)
        if not user or not user.check_password(password):
            return None
        return user

    @staticmethod
    def login(user, remember=False):
        login_user(user, remember=remember)

    @staticmethod
    def logout():
        logout_user()

    @staticmethod
    def update_profile(user, email=None, username=None, profile_image=None):
        if email:
            user.email = email
        if username:
            user.username = username
        if profile_image is not None:
            user.profile_image = profile_image
        db.session.commit()
        return user

    @staticmethod
    def change_password(user, current_password, new_password):
        if not user.check_password(current_password):
            raise ValueError('Current password is incorrect.')
        if not SecurityService.password_is_valid(new_password):
            raise ValueError('New password must be at least 8 characters and include upper, lower, and numeric characters.')
        user.set_password(new_password)
        db.session.commit()

    @staticmethod
    def delete_account(user):
        UserRepository.delete(user)
        db.session.commit()
