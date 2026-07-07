from __future__ import annotations

from statistics import mean, median, multimode, pstdev, pvariance

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

from .. import db
from ..models.budget import Budget
from ..models.expense import Expense
from ..models.income import Income


def _scalar(value):
    return float(value or 0)


def _numbers(rows):
    return [float(row.amount) for row in rows if row.amount is not None]


def _frame(rows, columns):
    if not rows:
        return pd.DataFrame(columns=columns)
    return pd.DataFrame(rows, columns=columns)


def _query_all(query):
    return query.all()


def _expense_summary_rows(user_id):
    return _query_all(
        db.session.query(
            Expense.id,
            Expense.entry_date,
            Expense.category,
            Expense.description,
            Expense.tags,
            Expense.amount,
            Expense.payment_method,
            Expense.location,
            Expense.notes,
        ).filter(Expense.user_id == user_id)
    )


def _income_summary_rows(user_id):
    return _query_all(
        db.session.query(
            Income.id,
            Income.entry_date,
            Income.source,
            Income.amount,
            Income.notes,
        ).filter(Income.user_id == user_id)
    )


def _budget_summary_rows(user_id):
    return _query_all(
        db.session.query(
            Budget.id,
            Budget.month,
            Budget.category,
            Budget.total_amount,
            Budget.used_amount,
        ).filter(Budget.user_id == user_id)
    )


def _expense_df(user_id):
    rows = _expense_summary_rows(user_id)
    data = [{
        'id': r.id,
        'entry_date': r.entry_date,
        'category': r.category,
        'description': r.description,
        'tags': r.tags,
        'amount': _scalar(r.amount),
        'payment_method': r.payment_method,
        'location': r.location,
        'notes': r.notes,
    } for r in rows]
    return pd.DataFrame(data)


def _income_df(user_id):
    rows = _income_summary_rows(user_id)
    data = [{
        'id': r.id,
        'entry_date': r.entry_date,
        'source': r.source,
        'amount': _scalar(r.amount),
        'notes': r.notes,
    } for r in rows]
    return pd.DataFrame(data)


def _budget_df(user_id):
    rows = _budget_summary_rows(user_id)
    data = [{
        'id': r.id,
        'month': r.month,
        'category': r.category,
        'total_amount': _scalar(r.total_amount),
        'used_amount': _scalar(r.used_amount),
    } for r in rows]
    return pd.DataFrame(data)


def _monthly_agg(user_id, model, date_col, value_col, group_cols=None):
    group_cols = group_cols or []
    if db.engine.dialect.name == 'sqlite':
        month_expr = db.func.strftime('%Y-%m-01', date_col).label('month')
    else:
        month_expr = db.func.date_trunc('month', date_col).label('month')
    query = db.session.query(month_expr, db.func.sum(value_col).label('total')).filter(model.user_id == user_id)
    if group_cols:
        query = db.session.query(month_expr, *group_cols, db.func.sum(value_col).label('total')).filter(model.user_id == user_id)
        query = query.group_by(month_expr, *group_cols).order_by(month_expr)
    else:
        query = query.group_by(month_expr).order_by(month_expr)
    return query.all()


def _month_label(date_col):
    if db.engine.dialect.name == 'sqlite':
        return db.func.strftime('%Y-%m-01', date_col).label('month')
    return db.func.date_trunc('month', date_col).label('month')


def dashboard_summary(user_id):
    expense_sum, expense_count = db.session.query(
        db.func.coalesce(db.func.sum(Expense.amount), 0),
        db.func.count(Expense.id),
    ).filter(Expense.user_id == user_id).one()
    income_sum, income_count = db.session.query(
        db.func.coalesce(db.func.sum(Income.amount), 0),
        db.func.count(Income.id),
    ).filter(Income.user_id == user_id).one()
    budget_sum, budget_used = db.session.query(
        db.func.coalesce(db.func.sum(Budget.total_amount), 0),
        db.func.coalesce(db.func.sum(Budget.used_amount), 0),
    ).filter(Budget.user_id == user_id).one()

    total_expense = _scalar(expense_sum)
    total_income = _scalar(income_sum)
    balance = total_income - total_expense
    savings_rate = round((balance / total_income) * 100, 2) if total_income else 0.0

    values = _numbers(db.session.query(Expense.amount).filter(Expense.user_id == user_id).all())
    std_dev = float(np.std(values, ddof=0)) if len(values) > 1 else 0.0
    median_expense = float(np.median(values)) if values else 0.0
    return {
        'total_expense': round(total_expense, 2),
        'total_income': round(total_income, 2),
        'balance': round(balance, 2),
        'savings_rate': savings_rate,
        'avg_expense': round(_scalar(db.session.query(db.func.avg(Expense.amount)).filter(Expense.user_id == user_id).scalar()), 2),
        'median_expense': round(median_expense, 2),
        'std_expense': round(std_dev, 2),
        'budget_total': round(_scalar(budget_sum), 2),
        'budget_used': round(_scalar(budget_used), 2),
        'expense_count': int(expense_count),
        'income_count': int(income_count),
        'budget_count': int(db.session.query(Budget.id).filter(Budget.user_id == user_id).count()),
    }


def category_distribution(user_id):
    rows = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount).label('amount'),
    ).filter(Expense.user_id == user_id).group_by(Expense.category).order_by(db.func.sum(Expense.amount).desc()).all()
    return [{'category': row.category, 'amount': round(_scalar(row.amount), 2)} for row in rows]


def category_trend(user_id):
    rows = db.session.query(
        _month_label(Expense.entry_date),
        Expense.category,
        db.func.sum(Expense.amount).label('amount'),
    ).filter(Expense.user_id == user_id).group_by('month', Expense.category).order_by('month').all()
    return [{'month': pd.to_datetime(row.month).strftime('%Y-%m'), 'category': row.category, 'amount': round(_scalar(row.amount), 2)} for row in rows]


def monthly_expense_trend(user_id, periods=12):
    rows = _monthly_agg(user_id, Expense, Expense.entry_date, Expense.amount)
    df = _frame(rows, ['month', 'total'])
    if df.empty:
        months = pd.date_range(end=pd.Timestamp.today(), periods=periods, freq='MS')
        return [{'month': month.strftime('%Y-%m'), 'total': 0.0} for month in months]
    df['month'] = pd.to_datetime(df['month']).dt.strftime('%Y-%m')
    return df.to_dict(orient='records')


def income_monthly_trend(user_id, periods=12):
    rows = _monthly_agg(user_id, Income, Income.entry_date, Income.amount)
    df = _frame(rows, ['month', 'total'])
    if df.empty:
        months = pd.date_range(end=pd.Timestamp.today(), periods=periods, freq='MS')
        return [{'month': month.strftime('%Y-%m'), 'total': 0.0} for month in months]
    df['month'] = pd.to_datetime(df['month']).dt.strftime('%Y-%m')
    return df.to_dict(orient='records')


def stack_by_category(user_id, periods=12):
    return category_trend(user_id)


def histogram_data(user_id):
    return _numbers(db.session.query(Expense.amount).filter(Expense.user_id == user_id).all())


def scatter_data(user_id):
    rows = db.session.query(Expense.entry_date, Expense.amount, Expense.category).filter(Expense.user_id == user_id).order_by(Expense.entry_date.asc()).all()
    return [{'index': idx + 1, 'amount': _scalar(row.amount), 'category': row.category} for idx, row in enumerate(rows)]


def boxplot_data(user_id):
    rows = db.session.query(Expense.category, Expense.amount).filter(Expense.user_id == user_id).all()
    grouped = {}
    for row in rows:
        grouped.setdefault(row.category, []).append(round(_scalar(row.amount), 2))
    return grouped


def radar_data(user_id):
    return category_distribution(user_id)[:6]


def statistics_summary(user_id):
    values = _numbers(db.session.query(Expense.amount).filter(Expense.user_id == user_id).all())
    if not values:
        return {
            'average': 0.0,
            'median': 0.0,
            'mode': 0.0,
            'variance': 0.0,
            'std_dev': 0.0,
            'quartiles': {'q1': 0.0, 'q2': 0.0, 'q3': 0.0},
            'percentiles': {'p10': 0.0, 'p25': 0.0, 'p50': 0.0, 'p75': 0.0, 'p90': 0.0},
            'minimum': 0.0,
            'maximum': 0.0,
            'range': 0.0,
            'count': 0,
        }
    q1 = float(np.percentile(values, 25))
    q2 = float(np.percentile(values, 50))
    q3 = float(np.percentile(values, 75))
    return {
        'average': round(float(mean(values)), 2),
        'median': round(float(median(values)), 2),
        'mode': round(float(multimode(values)[0]), 2) if multimode(values) else 0.0,
        'variance': round(float(pvariance(values)), 2) if len(values) > 1 else 0.0,
        'std_dev': round(float(pstdev(values)), 2) if len(values) > 1 else 0.0,
        'quartiles': {'q1': round(q1, 2), 'q2': round(q2, 2), 'q3': round(q3, 2)},
        'percentiles': {'p10': round(float(np.percentile(values, 10)), 2), 'p25': round(q1, 2), 'p50': round(q2, 2), 'p75': round(q3, 2), 'p90': round(float(np.percentile(values, 90)), 2)},
        'minimum': round(float(min(values)), 2),
        'maximum': round(float(max(values)), 2),
        'range': round(float(max(values) - min(values)), 2),
        'count': len(values),
    }


def correlation_matrix(user_id):
    rows = db.session.query(Expense.entry_date, Expense.amount).filter(Expense.user_id == user_id).all()
    if not rows:
        return []
    df = pd.DataFrame([{'entry_date': row.entry_date, 'amount': round(_scalar(row.amount), 2)} for row in rows])
    df['day_of_week'] = pd.to_datetime(df['entry_date']).dt.dayofweek
    df['day_of_month'] = pd.to_datetime(df['entry_date']).dt.day
    df['month'] = pd.to_datetime(df['entry_date']).dt.month
    df['week_of_year'] = pd.to_datetime(df['entry_date']).dt.isocalendar().week.astype(int)
    return df[['amount', 'day_of_week', 'day_of_month', 'month', 'week_of_year']].corr().round(3).fillna(0).to_dict()


def _forecast_from_series(series, periods=3):
    if series.empty or len(series) < 2:
        return []
    x = np.arange(len(series)).reshape(-1, 1)
    model = LinearRegression().fit(x, series.values)
    future_x = np.arange(len(series), len(series) + periods).reshape(-1, 1)
    return model.predict(future_x).tolist()


def monthly_expense_prediction(user_id, periods=3):
    trend = monthly_expense_trend(user_id, max(periods, 6))
    series = pd.Series([float(row['total'] or 0) for row in trend], dtype=float)
    preds = _forecast_from_series(series, periods)
    months = pd.date_range(end=pd.Timestamp.today(), periods=len(series), freq='MS')
    future_months = pd.date_range(start=months.max() + pd.offsets.MonthBegin(1), periods=periods, freq='MS')
    return [{'month': m.strftime('%Y-%m'), 'predicted_expense': round(max(0, p), 2)} for m, p in zip(future_months, preds)]


def future_savings_prediction(user_id, periods=3):
    expense = monthly_expense_prediction(user_id, periods)
    income_series = pd.Series([float(row['total'] or 0) for row in income_monthly_trend(user_id, max(periods, 6))], dtype=float)
    income_preds = _forecast_from_series(income_series, periods)
    return [{'month': expense[idx]['month'], 'predicted_savings': round(max(0, income_preds[idx] - expense[idx]['predicted_expense']), 2)} for idx in range(min(len(expense), len(income_preds)))]


def budget_overrun_prediction(user_id):
    rows = db.session.query(
        _month_label(Expense.entry_date),
        Expense.category,
        db.func.sum(Expense.amount).label('amount'),
    ).filter(Expense.user_id == user_id).group_by('month', Expense.category).all()
    budgets = _budget_df(user_id)
    if budgets.empty or not rows:
        return []
    exp_df = pd.DataFrame([{'month': pd.to_datetime(row.month).strftime('%Y-%m'), 'category': row.category, 'amount': round(_scalar(row.amount), 2)} for row in rows])
    budgets['month'] = pd.to_datetime(budgets['month']).dt.strftime('%Y-%m')
    merged = exp_df.merge(budgets, on='month', how='left')
    merged['total_amount'] = pd.to_numeric(merged['total_amount'], errors='coerce').fillna(0.0)
    merged['overrun_risk'] = merged.apply(lambda r: (float(r['amount']) / max(float(r['total_amount']), 1.0)) * 100, axis=1)
    return merged[['month', 'category_x', 'amount', 'total_amount', 'overrun_risk']].rename(columns={'category_x': 'category'}).to_dict(orient='records')


def anomaly_detection(user_id):
    values = _numbers(db.session.query(Expense.amount).filter(Expense.user_id == user_id).all())
    if len(values) < 6:
        return []
    df = pd.DataFrame({'amount': values})
    preds = IsolationForest(contamination=0.15, random_state=42).fit_predict(df[['amount']])
    df['is_anomaly'] = preds == -1
    anomalies = df[df['is_anomaly']]
    return [{'amount': float(row.amount)} for row in anomalies.itertuples()]


def financial_health_score(user_id):
    summary = dashboard_summary(user_id)
    if summary['total_income'] <= 0:
        return {'score': 0, 'label': 'Insufficient data'}
    burn = summary['total_expense'] / max(summary['total_income'], 1)
    score = 50 + (summary['savings_rate'] * 0.5) + (max(0, 100 - summary['expense_count']) * 0.15) - (burn * 20)
    score = max(0, min(100, round(score, 2)))
    label = 'Excellent' if score >= 80 else 'Good' if score >= 65 else 'Watch' if score >= 45 else 'Risk'
    return {'score': score, 'label': label}


def generate_insights(user_id):
    df = _expense_df(user_id)
    if df.empty:
        return ['No expense data yet. Add records to unlock insights.']
    insights = []
    df['month'] = pd.to_datetime(df['entry_date']).dt.to_period('M').dt.to_timestamp()
    months = sorted(df['month'].unique())
    if len(months) >= 2:
        current = df[df['month'] == months[-1]]
        previous = df[df['month'] == months[-2]]
        curr_food = current[current['category'].str.lower() == 'food']['amount'].sum()
        prev_food = previous[previous['category'].str.lower() == 'food']['amount'].sum()
        if prev_food > 0:
            delta = ((curr_food - prev_food) / prev_food) * 100
            insights.append(f"You spent {abs(round(delta, 0))}% {'more' if delta >= 0 else 'less'} on Food than last month.")
    weekday = pd.to_datetime(df['entry_date']).dt.day_name().value_counts()
    if not weekday.empty:
        insights.append(f"Highest spending happens on {weekday.idxmax()}.")
    payment = df.groupby('payment_method', dropna=True)['amount'].sum().sort_values(ascending=False)
    if not payment.empty:
        insights.append(f"Most spending goes through {payment.index[0] or 'unspecified payment methods'}.")
    if not insights:
        insights.append('Your spending pattern looks relatively steady right now.')
    return insights[:6]


def search_all(user_id, term):
    term = (term or '').strip()
    if not term:
        return {'expenses': [], 'incomes': [], 'budgets': []}
    e = _expense_df(user_id)
    i = _income_df(user_id)
    b = _budget_df(user_id)
    def _contains(df):
        return df.fillna('').astype(str).apply(lambda row: row.str.contains(term, case=False, na=False).any(), axis=1) if not df.empty else pd.Series(dtype=bool)
    return {
        'expenses': e[_contains(e)].to_dict(orient='records') if not e.empty else [],
        'incomes': i[_contains(i)].to_dict(orient='records') if not i.empty else [],
        'budgets': b[_contains(b)].to_dict(orient='records') if not b.empty else [],
    }


def monthly_pdf_context(user_id, periods=12):
    return {
        'summary': dashboard_summary(user_id),
        'insights': generate_insights(user_id),
        'stats': statistics_summary(user_id),
        'health': financial_health_score(user_id),
        'expense_trend': monthly_expense_trend(user_id, periods),
        'income_trend': income_monthly_trend(user_id, periods),
        'categories': category_distribution(user_id),
        'category_trend': category_trend(user_id),
        'monthly_predictions': monthly_expense_prediction(user_id, 6),
        'savings_predictions': future_savings_prediction(user_id, 6),
        'overrun': budget_overrun_prediction(user_id),
        'anomalies': anomaly_detection(user_id),
        'correlation': correlation_matrix(user_id),
        'scatter': scatter_data(user_id),
        'histogram': histogram_data(user_id),
        'radar': radar_data(user_id),
        'stacked': stack_by_category(user_id, periods),
        'boxplot': boxplot_data(user_id),
    }
