from web_app import app, db
from web_app.forms import RegisterForm, LoginForm
from web_app.modules import User
import sqlalchemy
from flask_login import login_user, login_required, current_user, logout_user
from flask import render_template, url_for, redirect, flash, get_flashed_messages


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.name.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("You have been registrated!", category="success")
        
        return redirect(url_for('login_page'))        
        
    if form.errors:
        for err_msg in form.errors.values():
            flash(f"Error: {err_msg[0]}", category="danger")
            
    return render_template("auth/register.html", form=form)


@app.route('/login', methods=['POST', 'GET'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            flash("Logged in successfully.", category="success")
            
            return redirect(url_for("home_page"))
        else:
            flash("Password or Username are not match", category="danger")
    
    if form.errors:
        for err_msg in form.errors.values():
            flash(f"Error: {err_msg[0]}", category="danger")
    
    return render_template("auth/login.html", form=form)


@app.route('/login_view')
def login_view():
    return render_template('auth/login_view.html')

@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You have been logged out", category="success")
    return redirect(url_for('home_page'))

