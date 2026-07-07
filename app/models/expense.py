from datetime import datetime
from .. import db

class Expense(db.Model):
    __tablename__ = 'expenses'
    __table_args__ = (
        db.Index('idx_expenses_user_id', 'user_id'),
        db.Index('idx_expenses_entry_date', 'entry_date'),
        db.Index('idx_expenses_category', 'category'),
        db.Index('idx_expenses_payment_method', 'payment_method'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    attachment_path = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Expense {self.id} - {self.category} - {self.amount}>"
