from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal, InvalidOperation

income_bp = Blueprint('income', __name__)
from ..repositories.income_repository import IncomeRepository
from ..services.income_service import IncomeService

@income_bp.route('/')
@login_required
def list_income():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = IncomeService.list_for_user(current_user.id).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('income/list.html', incomes=pagination.items, pagination=pagination)

@income_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_income():
    if request.method == 'POST':
        try:
            IncomeService.create_income(current_user.id, request.form)
            flash('Income added successfully.', 'success')
            return redirect(url_for('income.list_income'))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), 'warning')
    return render_template('income/add.html')

@income_bp.route('/edit/<int:income_id>', methods=['GET', 'POST'])
@login_required
def edit_income(income_id):
    income = IncomeRepository.get_by_id(income_id, current_user.id)
    if request.method == 'POST':
        try:
            IncomeService.update_income(income, request.form)
            flash('Income updated.', 'success')
            return redirect(url_for('income.list_income'))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), 'warning')
    return render_template('income/edit.html', income=income)

@income_bp.route('/delete/<int:income_id>', methods=['POST'])
@login_required
def delete_income(income_id):
    income = IncomeRepository.get_by_id(income_id, current_user.id)
    IncomeService.delete_income(income)
    flash('Income deleted.', 'info')
    return redirect(url_for('income.list_income'))
