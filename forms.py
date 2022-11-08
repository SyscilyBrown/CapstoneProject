from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectMultipleField, SelectField,StringField, FloatField, IntegerField, PasswordField
from wtforms.validators import InputRequired, Optional, DataRequired, Email, Length

class RecipeByIngredients(FlaskForm):
    ingredient1 = StringField("Ingredient 1")
    ingredient2 = StringField("Ingredient 2")
    ingredient3 = StringField("Ingredient 3")
    ingredient4 = StringField("Ingredient 4", validators=[Optional()])
    ingredient5 = StringField("Ingredient 5", validators=[Optional()])

class RecipeByNutrients(FlaskForm):
    minProtein = IntegerField("Minimum Protein? (Required) ")
    minCalories = IntegerField("Minimum Calories?", validators=[Optional()])
    maxCalories = IntegerField("Maximum Calories? (Required)")
    minFat = IntegerField("Minimum Fat?", validators=[Optional()])
    maxFat = IntegerField("Maximum Fat?", validators=[Optional()])
    maxCarbs = IntegerField("Max Carbs?", validators=[Optional()])
    maxSugar = IntegerField("Max Sugar?", validators=[Optional()])

class UserForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
