from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal, InvalidOperation

budgets_bp = Blueprint('budgets', __name__)
from ..repositories.budget_repository import BudgetRepository
from ..services.budget_service import BudgetService

@budgets_bp.route('/')
@login_required
def list_budgets():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = BudgetService.list_for_user(current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('budgets/list.html', budgets=pagination.items, pagination=pagination)

@budgets_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    if request.method == 'POST':
        try:
            BudgetService.create_budget(current_user.id, request.form)
            flash('Budget created.', 'success')
            return redirect(url_for('budgets.list_budgets'))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), 'warning')
    return render_template('budgets/add.html')

@budgets_bp.route('/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    budget = BudgetRepository.get_by_id(budget_id, current_user.id)
    if request.method == 'POST':
        try:
            BudgetService.update_budget(budget, request.form)
            flash('Budget updated.', 'success')
            return redirect(url_for('budgets.list_budgets'))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), 'warning')
    return render_template('budgets/edit.html', budget=budget)

@budgets_bp.route('/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    budget = BudgetRepository.get_by_id(budget_id, current_user.id)
    BudgetService.delete_budget(budget)
    flash('Budget deleted.', 'info')
    return redirect(url_for('budgets.list_budgets'))
