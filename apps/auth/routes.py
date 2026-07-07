from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_login import current_user, login_required

from ..repositories.user_repository import UserRepository
from ..services.auth_service import AuthService
from ..services.security_service import SecurityService
from ..models.password_reset_token import PasswordResetToken
from ..models.email_verification_token import EmailVerificationToken

auth_bp = Blueprint('auth', __name__)


def _safe_profile_image(upload):
    if not upload or not upload.filename:
        return None
    if not upload.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        raise ValueError('Profile image must be PNG, JPG, JPEG, or WEBP.')
    return upload.filename


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        if not email or not username or not password:
            flash('All fields are required.', 'warning')
            return redirect(url_for('auth.register'))
        try:
            AuthService.register_user(email=email, username=username, password=password)
        except ValueError as exc:
            flash(str(exc), 'danger')
            return redirect(url_for('auth.register'))
        flash('Registration successful. Please verify your email and log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        user = AuthService.authenticate(email, password)
        if user:
            AuthService.login(user, remember='remember' in request.form)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid credentials.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    AuthService.logout()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        user = UserRepository.get_by_email(email)
        if user:
            token = SecurityService.create_password_reset_token(user.id)
            flash(f'Password reset token created. Use token: {token.token}', 'info')
        else:
            flash('If the email exists, a reset token has been generated.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<string:token>', methods=['GET', 'POST'])
def reset_password(token):
    token_obj = PasswordResetToken.query.filter_by(token=token).first_or_404()
    if token_obj.used_at or token_obj.expires_at < datetime.utcnow():
        flash('This reset token is invalid or expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password') or ''
        try:
            if not SecurityService.password_is_valid(password):
                raise ValueError('Password must be at least 8 characters and include upper, lower, and numeric characters.')
            user = UserRepository.get_by_id(token_obj.user_id)
            user.set_password(password)
            SecurityService.mark_password_reset_used(token_obj)
            flash('Password has been reset.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as exc:
            flash(str(exc), 'warning')
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/verify-email/<string:token>')
def verify_email(token):
    token_obj = EmailVerificationToken.query.filter_by(token=token).first_or_404()
    if token_obj.verified_at or token_obj.expires_at < datetime.utcnow():
        flash('This verification link is invalid or expired.', 'danger')
        return redirect(url_for('auth.login'))
    SecurityService.mark_email_verified(token_obj)
    flash('Email verified successfully.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password') or ''
        new_password = request.form.get('new_password') or ''
        try:
            AuthService.change_password(current_user, current_password, new_password)
            flash('Password changed successfully.', 'success')
            return redirect(url_for('index'))
        except ValueError as exc:
            flash(str(exc), 'warning')
    return render_template('auth/change_password.html')


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = (request.form.get('email') or '').strip().lower()
        username = (request.form.get('username') or '').strip()
        profile_image = _safe_profile_image(request.files.get('profile_image'))
        try:
            AuthService.update_profile(current_user, email=email or None, username=username or None, profile_image=profile_image)
            flash('Profile updated.', 'success')
            return redirect(url_for('auth.profile'))
        except ValueError as exc:
            flash(str(exc), 'warning')
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        user = current_user._get_current_object()
        AuthService.delete_account(user)
        AuthService.logout()
        flash('Your account has been deleted.', 'info')
        return redirect(url_for('auth.register'))
    return render_template('auth/delete_account.html')


@auth_bp.route('/sessions')
@login_required
def sessions():
    return render_template('auth/sessions.html')


@auth_bp.route('/api/token', methods=['POST'])
def token():
    payload = request.get_json(silent=True) or {}
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password') or ''
    user = AuthService.authenticate(email, password)
    if not user:
        return jsonify({'msg': 'Bad credentials'}), 401
    access = create_access_token(identity=user.id)
    refresh = create_refresh_token(identity=user.id)
    return jsonify(access_token=access, refresh_token=refresh)
