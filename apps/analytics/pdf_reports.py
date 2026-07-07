from __future__ import annotations

from tempfile import NamedTemporaryFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
from flask import send_file


def _as_float_list(values):
    return [float(v or 0) for v in values]


def render_pdf_report(title: str, period_label: str, data: dict, filename: str):
    def _chart_page(pdf, page_title, fig):
        fig.suptitle(page_title, fontsize=18)
        pdf.savefig(fig)
        plt.close(fig)

    def _table_page(pdf, page_title, rows, columns):
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        ax.set_title(page_title, fontsize=18, pad=20)
        if not rows:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', fontsize=14)
        else:
            table = ax.table(cellText=rows, colLabels=columns, loc='center', cellLoc='left')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
        pdf.savefig(fig)
        plt.close(fig)

    with NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        pdf_path = tmp.name

    with PdfPages(pdf_path) as pdf:
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        summary = data['summary']
        health = data['health']
        lines = [
            f'Calex - Calculate Your Expense {title}',
            f'Period: {period_label}',
            '',
            f"Total Expense: Rs {summary['total_expense']}",
            f"Total Income: Rs {summary['total_income']}",
            f"Balance: Rs {summary['balance']}",
            f"Savings Rate: {summary['savings_rate']}%",
            f"Financial Health: {health['score']} / 100 ({health['label']})",
            '',
            'Top insights:',
        ] + [f"- {item}" for item in data['insights']]
        ax.text(0.04, 0.96, '\n'.join(lines), va='top', fontsize=14, family='monospace')
        pdf.savefig(fig)
        plt.close(fig)

        expense_trend = data['expense_trend']
        income_trend = data['income_trend']
        categories = data['categories']
        correlation = data['correlation']

        if expense_trend:
            months = [r['month'] for r in expense_trend]
            values = _as_float_list([r['total'] for r in expense_trend])
            fig, ax = plt.subplots(figsize=(11, 6))
            ax.plot(months, values, marker='o', color='#7dd3fc', linewidth=2)
            ax.set_title(f'{period_label} Expense Trend')
            ax.grid(alpha=0.18)
            ax.tick_params(axis='x', rotation=35)
            _chart_page(pdf, f'{period_label} Expense Trend', fig)

            fig, ax = plt.subplots(figsize=(11, 6))
            ax.hist(values, bins=max(3, min(10, len(values))), color='#34d399', alpha=0.85)
            ax.set_title('Expense Histogram')
            _chart_page(pdf, 'Expense Histogram', fig)

        if income_trend:
            values = _as_float_list([r['total'] for r in income_trend])
            fig, ax = plt.subplots(figsize=(11, 6))
            ax.fill_between(range(len(values)), values, color='#34d399', alpha=0.4)
            ax.plot(range(len(values)), values, color='#34d399', linewidth=2)
            ax.set_title(f'{period_label} Income Trend')
            _chart_page(pdf, f'{period_label} Income Trend', fig)

        if categories:
            fig, ax = plt.subplots(figsize=(11, 6))
            ax.pie(
                _as_float_list([r['amount'] for r in categories]),
                labels=[r['category'] for r in categories],
                autopct='%1.1f%%',
                startangle=90,
            )
            ax.set_title('Category Distribution')
            _chart_page(pdf, 'Category Distribution', fig)

        if expense_trend and income_trend:
            months = [r['month'] for r in expense_trend]
            exp_values = _as_float_list([r['total'] for r in expense_trend])
            inc_values = _as_float_list([r['total'] for r in income_trend[:len(expense_trend)]])
            if len(inc_values) < len(exp_values):
                inc_values += [0.0] * (len(exp_values) - len(inc_values))
            fig, ax = plt.subplots(figsize=(11, 6))
            ax.bar(months, exp_values, label='Expense', color='#f97316')
            ax.bar(months, inc_values, bottom=exp_values, label='Income', color='#60a5fa', alpha=0.7)
            ax.set_title('Stacked Bar Chart')
            ax.tick_params(axis='x', rotation=35)
            ax.legend()
            _chart_page(pdf, 'Stacked Bar Chart', fig)

        if correlation:
            corr_df = pd.DataFrame(correlation).apply(pd.to_numeric, errors='coerce').fillna(0)
            fig, ax = plt.subplots(figsize=(11, 6))
            cax = ax.imshow(corr_df.values, cmap='viridis')
            ax.set_xticks(range(len(corr_df.columns)))
            ax.set_xticklabels(corr_df.columns, rotation=35, ha='right')
            ax.set_yticks(range(len(corr_df.index)))
            ax.set_yticklabels(corr_df.index)
            ax.set_title('Heatmap')
            fig.colorbar(cax, ax=ax)
            _chart_page(pdf, 'Heatmap', fig)

        insight_rows = [[idx + 1, insight] for idx, insight in enumerate(data['insights'])]
        _table_page(pdf, 'Summary Tables: Insights', insight_rows, ['#', 'Insight'])

        stat = data['stats']
        stat_rows = [
            ['Average', f"Rs {stat.get('average')}"],
            ['Median', f"Rs {stat.get('median')}"],
            ['Mode', f"Rs {stat.get('mode')}"],
            ['Variance', stat.get('variance')],
            ['Std Dev', stat.get('std_dev')],
            ['Min', f"Rs {stat.get('minimum')}"],
            ['Max', f"Rs {stat.get('maximum')}"],
            ['Range', f"Rs {stat.get('range')}"],
        ]
        _table_page(pdf, 'Summary Tables: Statistics', stat_rows, ['Metric', 'Value'])

        anomaly_rows = [[str(item.get('entry_date')), item.get('category'), f"Rs {item.get('amount')}"] for item in data['anomalies'][:15]]
        _table_page(pdf, 'Summary Tables: Anomalies', anomaly_rows, ['Date', 'Category', 'Amount'])

        overrun_rows = [
            [
                item.get('month'),
                item.get('category'),
                f"Rs {item.get('amount')}",
                f"Rs {item.get('total_amount')}",
                f"{round(float(item.get('overrun_risk', 0) or 0), 1)}%",
            ]
            for item in data['overrun'][:15]
        ]
        _table_page(pdf, 'Summary Tables: Budget Overrun', overrun_rows, ['Month', 'Category', 'Expense', 'Budget', 'Risk'])

    return send_file(pdf_path, as_attachment=True, download_name=filename, mimetype='application/pdf')
