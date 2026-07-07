import os
import unittest
from datetime import date

os.environ.setdefault('SECRET_KEY', 'test-secret')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret')

from app import create_app, db
from app.analytics.service import dashboard_summary, generate_insights, monthly_expense_trend
from app.models.expense import Expense
from app.models.income import Income
from app.models.user import User


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def seed_user(self):
        with self.app.app_context():
            user = User(email='ana@example.com', username='ana')
            user.set_password('Password123')
            db.session.add(user)
            db.session.flush()
            db.session.add_all([
                Expense(user_id=user.id, category='Food', amount=100, entry_date=date(2026, 7, 1)),
                Expense(user_id=user.id, category='Travel', amount=50, entry_date=date(2026, 7, 2)),
                Income(user_id=user.id, source='Salary', amount=1000, entry_date=date(2026, 7, 1)),
            ])
            db.session.commit()
            return user.id

    def test_register_and_login(self):
        rv = self.client.post('/auth/register', data={
            'email': 'tester@example.com',
            'username': 'tester',
            'password': 'Password123',
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)
        rv = self.client.post('/auth/login', data={
            'email': 'tester@example.com',
            'password': 'Password123',
        }, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

    def test_forgot_password_generates_message(self):
        with self.app.app_context():
            user = User(email='forgot@example.com', username='forgot')
            user.set_password('Password123')
            db.session.add(user)
            db.session.commit()
        rv = self.client.post('/auth/forgot-password', data={'email': 'forgot@example.com'}, follow_redirects=True)
        self.assertEqual(rv.status_code, 200)

    def test_analytics_summary(self):
        user_id = self.seed_user()
        with self.app.app_context():
            summary = dashboard_summary(user_id)
            self.assertEqual(summary['total_expense'], 150.0)
            self.assertEqual(summary['total_income'], 1000.0)

    def test_analytics_trend(self):
        user_id = self.seed_user()
        with self.app.app_context():
            trend = monthly_expense_trend(user_id, 12)
            self.assertTrue(trend)

    def test_analytics_insights(self):
        user_id = self.seed_user()
        with self.app.app_context():
            insights = generate_insights(user_id)
            self.assertTrue(insights)


if __name__ == '__main__':
    unittest.main()
