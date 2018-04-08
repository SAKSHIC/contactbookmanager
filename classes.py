from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SubmitField

class AddContact(FlaskForm):
    number = TextField('Contact Number')
    name = TextField('Contact Name')
    add = SubmitField('Add')

class DeleteContact(FlaskForm):
    name = TextField('Contact Name')
    delete = SubmitField('Delete')

class UpdateContact(FlaskForm):
    number = TextField('Contact Number')
    name = TextField('Contact Name')
    update = SubmitField('Update')

class SearchContact(FlaskForm):
    number = TextField('Contact Number')
    name = TextField('Contact Name')
    search = SubmitField('Search')

class ResetTask(FlaskForm):
    reset = SubmitField('Reset')
