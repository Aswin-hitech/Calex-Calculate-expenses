import os
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from .. import db
from ..models.expense import Expense
from ..repositories.expense_repository import ExpenseRepository
from ..services.expense_service import ExpenseService

expenses_bp = Blueprint('expenses', __name__)


def _parse_date(value):
    return ExpenseService.parse_date(value)


def _parse_amount(value):
    return ExpenseService.parse_amount(value)


def _normalize_text(value):
    return ExpenseService.normalize_text(value)


def _normalize_tags(value):
    return ExpenseService.normalize_tags(value)


def _save_attachment(file_storage):
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    stamped_name = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{filename}"
    file_storage.save(os.path.join(upload_dir, stamped_name))
    return f"static/uploads/{stamped_name}"


@expenses_bp.route('/')
@login_required
def list_expenses():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    sort_by = request.args.get('sort_by', 'entry_date')
    order = request.args.get('order', 'desc')

    pagination = ExpenseService.list_for_user(current_user.id, sort_by=sort_by, order=order).paginate(page=page, per_page=per_page, error_out=False)
    total_spend = sum((item.amount for item in pagination.items), Decimal('0.00'))
    return render_template(
        'expenses/list.html',
        expenses=pagination.items,
        pagination=pagination,
        sort_by=sort_by,
        order=order,
        total_spend=total_spend,
    )


@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        try:
            category = _normalize_text(request.form.get('category'))
            description = _normalize_text(request.form.get('description'))
            tags = _normalize_tags(request.form.get('tags'))
            payment_method = _normalize_text(request.form.get('payment_method'))
            location = _normalize_text(request.form.get('location'))
            notes = _normalize_text(request.form.get('notes'))
            ExpenseService.create_expense(current_user.id, request.form, attachment_path=_save_attachment(request.files.get('attachment')))
            flash('Expense added successfully.', 'success')
            return redirect(url_for('expenses.list_expenses'))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), 'warning')
        except Exception:
            flash('Could not save the expense right now.', 'danger')
    return render_template('expenses/add.html')


@expenses_bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    expense = ExpenseRepository.get_by_id(expense_id, current_user.id)
    if request.method == 'POST':
        try:
            ExpenseService.update_expense(expense, request.form, attachment_path=_save_attachment(request.files.get('attachment')))
            flash('Expense updated.', 'success')
            return redirect(url_for('expenses.list_expenses'))
        except (ValueError, InvalidOperation) as exc:
            flash(str(exc), 'warning')
        except Exception:
            flash('Could not update the expense right now.', 'danger')
    return render_template('expenses/edit.html', expense=expense)


@expenses_bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    expense = ExpenseRepository.get_by_id(expense_id, current_user.id)
    ExpenseService.delete_expense(expense)
    flash('Expense deleted.', 'info')
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/delete-all', methods=['POST'])
@login_required
def delete_all_expenses():
    ExpenseService.delete_all_for_user(current_user.id)
    flash('All of your expenses were deleted.', 'info')
    return redirect(url_for('expenses.list_expenses'))


@expenses_bp.route('/search')
@login_required
def search_expenses():
    query = request.args.get('q', '').strip()
    if not query:
        flash('Enter a search term.', 'warning')
        return redirect(url_for('expenses.list_expenses'))

    results = (
        Expense.query.filter(
            Expense.user_id == current_user.id,
            or_(
                Expense.category.ilike(f'%{query}%'),
                Expense.description.ilike(f'%{query}%'),
                Expense.tags.ilike(f'%{query}%'),
                Expense.location.ilike(f'%{query}%'),
                Expense.payment_method.ilike(f'%{query}%'),
                Expense.notes.ilike(f'%{query}%'),
            ),
        )
        .order_by(Expense.entry_date.desc())
        .all()
    )
    return render_template('expenses/search.html', expenses=results, query=query)


@expenses_bp.route('/search/category')
@login_required
def search_by_category():
    categories = [row[0] for row in db.session.query(Expense.category).filter(Expense.user_id == current_user.id).distinct().order_by(Expense.category.asc()).all()]
    category = request.args.get('category', '').strip()
    sort_by = request.args.get('sort_by', 'entry_date')
    order = request.args.get('order', 'desc')

    query = Expense.query.filter_by(user_id=current_user.id)
    if category:
        query = query.filter(Expense.category.ilike(f'%{category}%'))

    sort_map = {
        'entry_date': Expense.entry_date,
        'amount': Expense.amount,
        'category': Expense.category,
        'payment_method': Expense.payment_method,
    }
    sort_column = sort_map.get(sort_by, Expense.entry_date)
    sort_column = sort_column.desc() if order != 'asc' else sort_column.asc()
    expenses = query.order_by(sort_column).all()
    return render_template(
        'expenses/search_category.html',
        expenses=expenses,
        categories=categories,
        selected_category=category,
        sort_by=sort_by,
        order=order,
    )


@expenses_bp.route('/search/tags')
@login_required
def search_by_tags():
    tag = request.args.get('tag', '').strip().lower()
    sort_by = request.args.get('sort_by', 'entry_date')
    order = request.args.get('order', 'desc')

    query = Expense.query.filter_by(user_id=current_user.id)
    if tag:
        query = query.filter(Expense.tags.ilike(f'%{tag}%'))

    sort_map = {
        'entry_date': Expense.entry_date,
        'amount': Expense.amount,
        'category': Expense.category,
        'tags': Expense.tags,
    }
    sort_column = sort_map.get(sort_by, Expense.entry_date)
    sort_column = sort_column.desc() if order != 'asc' else sort_column.asc()
    expenses = query.order_by(sort_column).all()
    tags = [
        row[0]
        for row in db.session.query(Expense.tags)
        .filter(Expense.user_id == current_user.id, Expense.tags.isnot(None))
        .distinct()
        .all()
    ]
    return render_template(
        'expenses/search_tags.html',
        expenses=expenses,
        tags=tags,
        selected_tag=tag,
        sort_by=sort_by,
        order=order,
    )
