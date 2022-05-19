from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, DecimalField, FileField
from wtforms.validators import DataRequired, ValidationError
from app.models import Auto


class AutoDetailForm(FlaskForm):
    submit_free = SubmitField("Арендовать")
    submit_borrow = SubmitField("Закончить аренду")


class CreateAutoForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    price = DecimalField('price', validators=[DataRequired()], places=2)
    transmission = RadioField('transmission', validators=[DataRequired()], coerce=int,
                              choices=[(1, 'ДА'), (0, 'НЕТ')])
    main_image = FileField('main_image', validators=[DataRequired()])

    def validate_name(self, field):
        if Auto.query.filter_by(name=field.data).first():
            raise ValidationError(
                f"Название {self.name.data} уже использовано, введите другое")


class UpdateAutoForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    price = DecimalField('price', validators=[DataRequired()], places=2)
    transmission = RadioField('transmission', coerce=int,
                              choices=[(1, 'ДА'), (0, 'НЕТ')])
    main_image = FileField('main_image')

    def validate_name(self, field):
        if Auto.query.filter_by(name=field.data).first():
            if field.data != field.object_data:
                raise ValidationError(
                    f"Название {self.name.data} {field.object_data}уже использовано, введите другое")


class AddImageForm(FlaskForm):
    main_image = FileField('main_image', validators=[DataRequired()])
