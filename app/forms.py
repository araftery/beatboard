from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, HiddenField
from wtforms.validators import Required, Length, URL

# WTForms declarations

class LoginForm(Form):
    openid = HiddenField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class PostForm(Form):
    content = TextAreaField('content', validators = [Length(min = 0, max = 1000)])
    title = TextField('title', validators = [Required()])
    song_url = TextField('song_url', validators = [Required(), URL()])
    submitted_field = HiddenField('submitted_field', default='true')

class SearchForm(Form):
	search = TextField('query', validators = [Required()])