from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SelectMultipleField, SelectField,StringField, FloatField, IntegerField, PasswordField
from wtforms.validators import InputRequired, Optional, DataRequired, Email, Length

class RecipeByIngredients(FlaskForm):
    ingredient1 = StringField("First Ingredient")
    ingredient2 = StringField("Second Ingredient")
    ingredient3 = StringField("Third Ingredient")
    ingredient4 = StringField("Fourth Ingredient", validators=[Optional()])
    ingredient5 = StringField("Fifth Ingredient", validators=[Optional()])

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
