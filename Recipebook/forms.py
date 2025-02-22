from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    URLField,
    PasswordField
)
from wtforms.validators import (
    InputRequired,
    Email,
    Length,
    EqualTo
)

class RecipeForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    ingredients = StringField("Ingredients", validators=[InputRequired()])
    submit = SubmitField("Save Recipe")

class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []

class ExtendedRecipeForm(RecipeForm):
    cook_method = TextAreaField("Cook Method")
    tags = StringListField("Tags")
    video_link = URLField("Video Link")

    submit = SubmitField("Save")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField(
        "Password",
        validators=[InputRequired(),
                    Length(min=6, max=30,
                           message="Your password must be 6-30 characters long")
                    ])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo("password", message="Passwords not equal!")])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")












