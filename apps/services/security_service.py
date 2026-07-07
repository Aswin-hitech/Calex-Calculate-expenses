from __future__ import annotations

import secrets
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from .. import db
from ..models.email_verification_token import EmailVerificationToken
from ..models.password_reset_token import PasswordResetToken


class SecurityService:
    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(48)

    @staticmethod
    def create_password_reset_token(user_id, hours=2):
        token = PasswordResetToken(
            user_id=user_id,
            token=SecurityService.generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=hours),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @staticmethod
    def create_email_verification_token(user_id, hours=24):
        token = EmailVerificationToken(
            user_id=user_id,
            token=SecurityService.generate_token(),
            expires_at=datetime.utcnow() + timedelta(hours=hours),
        )
        db.session.add(token)
        db.session.commit()
        return token

    @staticmethod
    def mark_password_reset_used(token_obj):
        token_obj.used_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def mark_email_verified(token_obj):
        token_obj.verified_at = datetime.utcnow()
        db.session.commit()

    @staticmethod
    def password_is_valid(password: str) -> bool:
        if not password or len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_upper and has_lower and has_digit
