from app import app
from app import login_manager
from forms import LoginForm
from flask import flash, redirect, render_template, request, url_for
from flask.ext.login import login_user, logout_user

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out!', 'success')
    return redirect(request.args.get('next') or url_for('homepage'))
@app.route('/login/', methods=['GET', 'POST'])
def login():
    print(request.form)
    form = LoginForm(request.form)
    if request.method == 'POST':
        print(form.validate())
        if form.validate():
            login_user(form.user, remember=form.remember_me.data)
            flash('Successfully logged in as {}.'.format(form.user.email), 'success')
            return redirect(request.args.get('next') or url_for('homepage'))
        form = LoginForm()
    return render_template('login.html', form=form)
