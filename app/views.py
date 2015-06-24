#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, session, url_for, request, g
from app import app, db, lm, babel
from flask.ext.login import login_user, logout_user, current_user, login_required
from models import User, ROLE_USER, ROLE_ADMIN, Post
from oauth import OAuthSignIn
from datetime import datetime
from forms import EditForm, PostForm, SearchForm
from config import LANGUAGES

@app.route('/', methods = ['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@app.route('/index/<int:page>', methods = ['GET', 'POST'])
@login_required
def index(page = 1):
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
		db.session.add(post)
		db.session.commit()
		flash('Ваше сообщение добавлено!')
		return redirect(url_for('index'))
	user = g.user
	posts = g.user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
	return render_template("index.html",
		title = u'Главная',
		user = user,
		posts = posts,
		form = form)

@app.route('/login')
def login():
	return render_template("login.html",
		title = u'Авторизация',
		providers = app.config['OAUTH_CREDENTIALS'].keys())

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

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
		nickname = username
		if nickname is None or nickname == "":
			nickname = email.split('@')[0]
		nickname = User.make_valid_nickname(nickname)
		nickname = User.make_unique_nickname(nickname)
		user = User(social_id=social_id, nickname=nickname, email=email, role=ROLE_USER)
		db.session.add(user)
		db.session.commit()
		# user follow himself
		db.session.add(user.follow(user))
		db.session.commit()
	login_user(user, True)
	return redirect(request.args.get('next') or url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
	user = User.query.filter_by(nickname = nickname).first()
	if user is None:
		flash('User ' + nickname + ' not found.')
		return redirect(url_for('index'))
	posts = user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
	return render_template('user.html',
		user = user,
		posts = posts)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
	form = EditForm(g.user.nickname)
	if form.validate_on_submit():
		g.user.nickname = form.nickname.data
		db.session.add(g.user)
		db.session.commit()
		flash('Ваши изменения были сохранены')
		return redirect(url_for('edit'))
	else:
		form.nickname.data = g.user.nickname
	return render_template('edit.html', form = form)

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user is None:
		flash('Пользователь {0} не найден'.format(nickname))
		return redirect(url_for('index'))
	if user == g.user:
		flash("Вы не можете подписаться на себя")
		return redirect(url_for('user', nickname = nickname))
	u = g.user.follow(user)
	if u is None:
		flash('Невозможно подписаться на {0}'.format(nickname))
		return redirect(url_for('user', nickname = nickname))
	db.session.add(u)
	db.session.commit()
	flash('Теперь Вы подписаны на {0}'.format(nickname))
	return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
	user = User.query.filter_by(nickname = nickname).first()
	if user is None:
		flash('Пользователь {0} не найден'.format(nickname))
		return redirect(url_for('index'))
	if user == g.user:
		flash("Вы не можете отписаться от себя")
		return redirect(url_for('user', nickname = nickname))
	u = g.user.unfollow(user)
	if u is None:
		flash('Невозможно отписаться от {0}'.format(nickname))
		return redirect(url_for('user', nickname = nickname))
	db.session.add(u)
	db.session.commit()
	flash('Вы отписались от обновлений {0}'.format(nickname))
	return redirect(url_for('user', nickname = nickname))

@app.route('/search', methods = ['POST'])
@login_required
def search():
	if not g.search_form.validate_on_submit():
		return redirect(url_for('index'))
	return redirect(url_for('search_results', query = g.search_form.search.data))

@app.route('/search_results/<query>')
@login_required
def search_results(query):
	results = Post.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS']).all()
	return render_template('search_results.html',
		query = query,
		results = results)

@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		g.search_form = SearchForm()

@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	return render_template('500.html'), 500

@babel.localeselector
def get_locale():
	return request.accept_languages.best_match(LANGUAGES.keys())
