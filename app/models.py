from app import db, lm, app
from flask.ext.login import LoginManager, UserMixin
from hashlib import md5
import flask.ext.whooshalchemy as whooshalchemy
import re

ROLE_USER = 0
ROLE_ADMIN = 1

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	nickname = db.Column(db.String(64), index = True, unique = True)
	email = db.Column(db.String(120), index = True, unique = True)
	role = db.Column(db.SmallInteger, default = ROLE_USER)
	posts = db.relationship('Post', backref = 'author', lazy = 'dynamic')
	followed = db.relationship('User', 
		secondary = followers, 
		primaryjoin = (followers.c.follower_id == id), 
		secondaryjoin = (followers.c.followed_id == id), 
		backref = db.backref('followers', lazy = 'dynamic'), 
		lazy = 'dynamic')
	social_id = db.Column(db.String(64), unique = True)
	last_seen = db.Column(db.DateTime)

	def __repr__(self):
		return '<User %r>' % (self.nickname)

	def avatar(self, size):
		return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			return self

	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			return self

	def is_following(self, user):
		return User.query.join(followers, (followers.c.follower_id == self.id)).filter(followers.c.followed_id == user.id).count() > 0

	def followed_posts(self):
		return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())

	@staticmethod
	def make_unique_nickname(nickname):
		if User.query.filter_by(nickname = nickname).first() is None:
			return nickname
		version = 2
		while True:
			new_nickname = nickname + str(version)
			if User.query.filter_by(nickname = new_nickname).first() is None:
				break
			version += 1
		return new_nickname

	@staticmethod
	def make_valid_nickname(nickname):
		return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

@lm.user_loader
def load_user(id):
	return User.query.get(int(id))

class Post(db.Model):
	__searchable__ = ['body']

	id = db.Column(db.Integer, primary_key = True)
	body = db.Column(db.String(4000))
	timestamp = db.Column(db.DateTime)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post %r>' % (self.body)

whooshalchemy.whoosh_index(app, Post)
