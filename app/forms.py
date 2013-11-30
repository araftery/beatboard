from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length, URL

class LoginForm(Form):
    openid = TextField('openid', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

class EditForm(Form):
    nickname = TextField('nickname', validators = [Required()])
    about_me = TextAreaField('about_me', validators = [Length(min = 0, max = 140)])

class PostForm(Form):
    content = TextAreaField('content', validators = [Length(min = 0, max = 1000)])
    title = TextField('title', validators = [Required()])
    song_url = TextField('song_url', validators = [Required(), URL()])