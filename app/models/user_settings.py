from datetime import datetime

from .. import db


class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    currency = db.Column(db.String(10), default='INR', nullable=False)
    timezone = db.Column(db.String(64), default='Asia/Calcutta', nullable=False)
    theme = db.Column(db.String(32), default='system', nullable=False)
    email_notifications = db.Column(db.Boolean, default=True, nullable=False)
    weekly_reports = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id}>"
