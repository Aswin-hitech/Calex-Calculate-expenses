from flask import Blueprint, render_template, flash, current_app
from flask_login import login_required, current_user
from ..models import User, Expense, Income, Budget
from .. import db

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return render_template('admin/unauthorized.html'), 403
    # Site-wide statistics
    total_users = db.session.query(User).count()
    active_users = db.session.query(User).filter(User.is_admin == False).count()  # placeholder for real active check
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_income = db.session.query(db.func.sum(Income.amount)).scalar() or 0
    db_health = 'OK'  # In a real app, perform DB health checks here
    return render_template('admin/dashboard.html', total_users=total_users,
                           active_users=active_users, total_expenses=total_expenses,
                           total_income=total_income, db_health=db_health)
