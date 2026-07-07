from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .. import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        db.Index('idx_users_email', 'email'),
        db.Index('idx_users_username', 'username'),
    )
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    expenses = db.relationship('Expense', backref='owner', lazy=True)
    incomes = db.relationship('Income', backref='owner', lazy=True)
    budgets = db.relationship('Budget', backref='owner', lazy=True)
    notifications = db.relationship('Notification', backref='owner', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='owner', uselist=False, cascade='all, delete-orphan')
    password_reset_tokens = db.relationship('PasswordResetToken', backref='owner', lazy=True, cascade='all, delete-orphan')
    email_verification_tokens = db.relationship('EmailVerificationToken', backref='owner', lazy=True, cascade='all, delete-orphan')
    # Additional relationships for predictions, reports, settings can be added

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_active(self) -> bool:
        """Return True if the user account is active."""
        return True

    def __repr__(self) -> str:
        return f"<User {self.username}>"
