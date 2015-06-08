from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, DateField
from wtforms.validators import Required, Length

class EditForm(Form):
	nickname = TextField('nickname', validators = [Required()])
	birthdate = DateField('birthdate')