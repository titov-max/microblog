from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, DateField
from wtforms.validators import Required, Length
from models import User

class EditForm(Form):
	nickname = TextField('nickname', validators = [Required()])

	def __init__(self, original_nickname, *args, **kwargs):
		Form.__init__(self, *args, **kwargs)
		self.original_nickname = original_nickname

	def validate(self):
		if not Form.validate(self):
			return False
		if self.nickname.data == self.original_nickname:
			return True
		user = User.query.filter_by(nickname = self.nickname.data).first()
		if user != None:
			self.nickname.errors.append('This nickname is already in use. Please choose another one.')
			return False
		return True