# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, DateField
from wtforms.validators import Required, Length
from models import User
from flask.ext.babel import gettext

class EditForm(Form):
	nickname = TextField('nickname', validators = [Required()])

	def __init__(self, original_nickname, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_nickname = original_nickname

	def validate(self):
		if not Form.validate(self):
			return False
		if self.nickname.data != User.make_valid_nickname(self.original_nickname):
			self.nickname.errors.append(gettext('This nickname has invalid characters.'))
			return False
		if self.nickname.data == self.original_nickname:
			return True
		user = User.query.filter_by(nickname = self.nickname.data).first()
		if user is not None:
			self.nickname.errors.append(gettext('This nickname is already in use. Please choose another one.'))
			return False
		return True

class PostForm(Form):
	post = TextField('post', validators = [Required()])

class SearchForm(Form):
	search = TextField('search', validators = [Required()])
