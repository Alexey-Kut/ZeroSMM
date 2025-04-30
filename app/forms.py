from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    tone = StringField('Тон', validators=[DataRequired(), Length(min=3, max=50)])
    topic = StringField('Тема', validators=[DataRequired(), Length(min=3, max=100)])
    generate_image = BooleanField('Генерировать изображение')
    auto_post = BooleanField('Автоматическая публикация в VK')
    submit = SubmitField('Генерировать')
