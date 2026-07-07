from datetime import datetime
from .. import db

class Income(db.Model):
    __tablename__ = 'incomes'
    __table_args__ = (
        db.Index('idx_incomes_user_id', 'user_id'),
        db.Index('idx_incomes_entry_date', 'entry_date'),
        db.Index('idx_incomes_source', 'source'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(80), nullable=False)  # Salary, Freelance, etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Income {self.id} - {self.source} - {self.amount}>"
