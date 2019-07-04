from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField


class AddEventsForm(FlaskForm):
    use_event = BooleanField()
    submit = SubmitField("Toevoegen")
