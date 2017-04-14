from . import main
from flask import render_template, redirect, url_for
from flask_login import current_user, login_required


@main.route('/')
def index():
    if not current_user.is_anonymous and \
            not current_user.authenticated:
        return redirect(url_for('auth.unconfirmed'))
    return render_template('base.html')


@main.route('/user')
def user():
    pass



