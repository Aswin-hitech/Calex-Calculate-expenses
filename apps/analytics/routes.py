from __future__ import annotations

import io

import pandas as pd
from flask import Blueprint, Response, jsonify, render_template, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_login import current_user, login_required

from ..analytics.pdf_reports import render_pdf_report
from ..analytics.service import (
    anomaly_detection,
    budget_overrun_prediction,
    category_distribution,
    category_trend,
    correlation_matrix,
    generate_insights,
    histogram_data,
    income_monthly_trend,
    monthly_expense_prediction,
    monthly_expense_trend,
    monthly_pdf_context,
    radar_data,
    scatter_data,
    search_all,
    stack_by_category,
    statistics_summary,
    boxplot_data,
)

analytics_bp = Blueprint('analytics', __name__)


def _build_report_data(user_id, periods=12):
    return monthly_pdf_context(user_id, periods)


def _export_dataframe(fmt: str, df: pd.DataFrame, filename: str):
    if fmt == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}.csv'})
    if fmt == 'json':
        payload = df.to_json(orient='records')
        return Response(payload, mimetype='application/json', headers={'Content-Disposition': f'attachment; filename={filename}.json'})
    if fmt == 'excel':
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        return send_file(output, as_attachment=True, download_name=f'{filename}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    raise ValueError('Unsupported export format')


@analytics_bp.route('/')
@login_required
def dashboard():
    return render_template('analytics/dashboard.html', data=_build_report_data(current_user.id))


@analytics_bp.route('/search')
@login_required
def global_search():
    term = request.args.get('q', '')
    results = search_all(current_user.id, term)
    return render_template('analytics/search.html', query=term, results=results)


@analytics_bp.route('/reports/monthly')
@login_required
def monthly_report():
    return render_template('analytics/report.html', report_type='Monthly', data=_build_report_data(current_user.id, 12))


@analytics_bp.route('/reports/yearly')
@login_required
def yearly_report():
    return render_template('analytics/report.html', report_type='Yearly', data=_build_report_data(current_user.id, 12))


@analytics_bp.route('/reports/monthly.pdf')
@login_required
def download_monthly_pdf():
    return render_pdf_report('Monthly Report', 'Monthly', _build_report_data(current_user.id, 12), 'monthly_report.pdf')


@analytics_bp.route('/reports/yearly.pdf')
@login_required
def download_yearly_pdf():
    return render_pdf_report('Yearly Report', 'Yearly', _build_report_data(current_user.id, 12), 'yearly_report.pdf')


@analytics_bp.route('/export/report.pdf')
@login_required
def export_pdf_report():
    return render_pdf_report('Monthly Report', 'Monthly', _build_report_data(current_user.id, 12), 'expense_report.pdf')


@analytics_bp.route('/export/<string:dataset>.<string:fmt>')
@login_required
def export_dataset(dataset, fmt):
    user_id = current_user.id
    datasets = {
        'expenses': pd.DataFrame(category_trend(user_id)),
        'income': pd.DataFrame(income_monthly_trend(user_id, 12)),
        'predictions': pd.DataFrame(monthly_expense_prediction(user_id, 6)),
        'insights': pd.DataFrame({'insight': generate_insights(user_id)}),
        'stats': pd.DataFrame([statistics_summary(user_id)]),
        'search': pd.DataFrame(search_all(user_id, request.args.get('q', '')).get('expenses', [])),
    }
    if dataset not in datasets:
        return jsonify({'error': 'Unknown export dataset'}), 404
    return _export_dataframe(fmt, datasets[dataset], dataset)


@analytics_bp.route('/api/dashboard')
@jwt_required()
def dashboard_api():
    user_id = get_jwt_identity()
    return jsonify(_build_report_data(user_id))


@analytics_bp.route('/api/category_distribution')
@jwt_required()
def category_distribution_route():
    return jsonify(category_distribution(get_jwt_identity()))


@analytics_bp.route('/api/monthly_expense')
@jwt_required()
def monthly_expense_route():
    periods = request.args.get('periods', default=12, type=int)
    return jsonify(monthly_expense_trend(get_jwt_identity(), periods))


@analytics_bp.route('/api/income_monthly')
@jwt_required()
def income_monthly_route():
    periods = request.args.get('periods', default=12, type=int)
    return jsonify(income_monthly_trend(get_jwt_identity(), periods))
