from datetime import datetime
from .. import db

class Budget(db.Model):
    __tablename__ = 'budgets'
    __table_args__ = (
        db.Index('idx_budgets_user_id', 'user_id'),
        db.Index('idx_budgets_month', 'month'),
        db.Index('idx_budgets_category', 'category'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Date, nullable=False)  # Store as first day of month
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(80), nullable=True)  # Optional category‑specific budget
    used_amount = db.Column(db.Numeric(10, 2), default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Budget {self.id} - {self.month.strftime('%Y-%m')} - {self.total_amount}>"
