from flask import render_template, redirect, flash, url_for, request, session
from . import auth
from .forms import LoginForm, RegisterForm, PasswordResetForm, PasswordResetRequestForm, \
    ChangePasswordForm, ChangeEmailRequestForm, ChangeEmailForm
from ..models import User
from manage import db
from flask_login import login_user, current_user, login_required, logout_user
from ..mail import send_email


@auth.before_app_request
def before_request():
    if not current_user.is_anonymous \
            and current_user.is_authenticated:
        if not current_user.authenticated \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint[:7] != 'static.':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    user = User.query.filter_by(username=form.username.data).first()
    if form.validate_on_submit():
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            token = current_user.generate_email_token()
            if not current_user.authenticated:
                send_email(to=current_user.email, subject='Confirm your account',
                           template='/auth/email/confirm',
                           user=current_user, token=token)
            return redirect(url_for('main.index'))
        flash('Invalid user or password')
    return render_template('auth/login.html', form=form)


@auth.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.generate_password_hash(form.password.data)
        db.session.add(user)
        db.session.commit()
        token = current_user.generate_email_token()
        send_email(to=current_user.email, subject='Confirm your account',
                   template='/auth/email/confirm',
                   user=user, token=token)
        return redirect(url_for("main.index"))
    return render_template('auth/register.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        token = user.generate_reset_token()
        send_email(to=user.email, subject='Reset your password',
                   template='auth/email/reset_password',
                   user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token=token, new_password=form.new_password.data):
            flash('Your password has reset.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.change_password(new_password=form.new_password.data)
            flash('Your password has updated.')
            return redirect(url_for('auth.login'))
    return render_template('auth/change_password.html', form=form)


@auth.route('/change-email-request', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailRequestForm()
    if form.validate_on_submit():
        token = current_user.generate_email_change_token()
        send_email(to=form.new_email.data, subject='Reset your password',
                   template='auth/email/reset_password',
                   token=token, user=current_user)
        flash('A email has send to your new email.')
        return redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.change_email(token, form.new_email.data):
            flash('Your email has changed.')
            return redirect(url_for('main.index'))
        flash('The link is invalid or has expired.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
@login_required
def unconfirmed():
    return render_template('unconfirmed.html')


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.authenticated:
        return redirect(url_for('main.index'))
    if not current_user.confirm(token):
        flash('This link is invalid or has expired.')
        return render_template('/auth/email/confirm.html', user=current_user, token=token)
    if current_user.confirm(token):
        flash('You have confirm your account.Wlecome to Flasky.')
        return redirect(url_for('main.index'))


@auth.route('/resend_confirmation')
@login_required
def resend_confirmation():
    token = current_user.generate_email_token()
    send_email(to=current_user.email, subject='Confirm your account',
               template='/auth/email/confirm',
               user=current_user, token=token)
    flash('A new email has sent to you...')
    return render_template('unconfirmed.html')





