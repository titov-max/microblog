#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, ROLE_USER, ROLE_ADMIN
from oauth import OAuthSignIn

@app.route('/')
@app.route('/index')
@login_required
def index():
	user = g.user
	posts = [
		{ 
            'author': { 'nickname': 'John' }, 
            'body': 'Beautiful day in Portland!' 
        },
        { 
            'author': { 'nickname': 'Susan' }, 
            'body': 'The Avengers movie was so cool!' 
        }
    ]
	return render_template("index.html",
		title = u'Главная',
		user = user,
		posts = posts)

@app.route('/login')
def login():
	return render_template("login.html",
		title = u'Авторизация',
		providers = app.config['OAUTH_CREDENTIALS'].keys())

@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not g.user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@app.route('/callback/<provider>')
def oauth_callback(provider):
	if not current_user.is_anonymous():
		return redirect(url_for('index'))
	oauth = OAuthSignIn.get_provider(provider)
	social_id, username, email = oauth.callback()
	if social_id is None:
		flash('Authentication failed.')
		return redirect(url_for('login'))
	user = User.query.filter_by(social_id=social_id).first()
	if user is None:
		user = User(social_id=social_id, nickname=username, email=email, role=ROLE_USER)
		db.session.add(user)
		db.session.commit()
	login_user(user, True)
	return redirect(request.args.get('next') or url_for('index'))

@app.before_request
def before_request():
	g.user = current_user