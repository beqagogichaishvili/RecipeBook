import uuid
import datetime
from dataclasses import asdict
import functools
from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request,
)
from Recipebook.forms import (
    RegisterForm,
    RecipeForm,
    ExtendedRecipeForm,
    LoginForm
)
from Recipebook.models import User, Recipe

from passlib.hash import pbkdf2_sha256
pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))

        return route(*args, **kwargs)

    return route_wrapper





@pages.route('/')
@login_required
def index():
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)

    recipe_data = current_app.db.recipe.find({"_id": {"$in": user.recipes}})
    recipes = [Recipe(**recipe) for recipe in recipe_data]

    return render_template(
        "index.html",
        title="Recipes",
        recipes_data=recipes
    )

@pages.route("/register", methods=["POST", "GET"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = RegisterForm()

    if form.validate_on_submit():
        user = User(
            _id=uuid.uuid4().hex,
            email=form.email.data,
            password=pbkdf2_sha256.hash(form.password.data),
        )

        current_app.db.user.insert_one(asdict(user))

        flash("User registered successfully", "success")

        return redirect(url_for(".login"))

    return render_template(
        "register.html", title="Recipes Watchlist - Register", form=form
    )

@pages.route("/login", methods=["GET", "POST"])
def login():
    if session.get("email"):
        return redirect(url_for(".index"))

    form = LoginForm()

    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            flash("Login credentials not correct", category="danger")
            return redirect(url_for(".login"))
        user = User(**user_data)

        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))

        flash("Login credentials not correct", category="danger")

    return render_template("login.html", title="Recipes Watchlist - Login", form=form)


@pages.route("/logout")
def logout():
    current_theme = session.get("theme")
    session.clear()
    session["theme"] = current_theme

    return redirect(url_for(".login"))


@pages.route("/add", methods=["GET", "POST"])
@login_required
def add_recipe():
    form = RecipeForm()

    if form.validate_on_submit():
        recipe = Recipe(
            _id=uuid.uuid4().hex,
            title=form.title.data,
            ingredients=form.ingredients.data
        )

        current_app.db.recipe.insert_one(asdict(recipe))
        current_app.db.user.update_one(
            {"_id": session["user_id"]}, {"$push": {"recipes": recipe._id}}
        )

        return redirect(url_for(".recipe", _id=recipe._id))

    return render_template(
        "new_recipe.html", title="Recipe Book - Add Recipe", form=form
    )


@pages.get("/recipe/<string:_id>")
def recipe(_id: str):
    recipe = Recipe(**current_app.db.recipe.find_one({"_id": _id}))
    return render_template("recipe_details.html", recipe=recipe)



@pages.route("/edit/<string:_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(_id: str):
    recipe = Recipe(**current_app.db.recipe.find_one({"_id": _id}))
    form = ExtendedRecipeForm(obj=recipe)
    if form.validate_on_submit():
        recipe.title = form.title.data
        recipe.ingredients = form.ingredients.data
        recipe.tags = form.tags.data
        recipe.cook_method = form.cook_method.data
        recipe.video_link = form.video_link.data

        current_app.db.recipe.update_one({"_id": recipe._id}, {"$set": asdict(recipe)})
        return redirect(url_for(".recipe", _id=recipe._id))
    return render_template("recipe_form.html", recipe=recipe, form=form)


@pages.get("/recipe/<string:_id>/watch")
@login_required
def watch_today(_id):
    current_app.db.recipe.update_one(
        {"_id": _id}, {"$set": {"last_watched": datetime.datetime.today()}}
    )

    return redirect(url_for(".recipe", _id=_id))


@pages.get("/recipe/<string:_id>/rate")
@login_required
def rate_recipe(_id):
    rating = int(request.args.get("rating"))
    current_app.db.recipe.update_one({"_id": _id}, {"$set": {"rating": rating}})

    return redirect(url_for(".recipe", _id=_id))



@pages.get("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"

    return redirect(request.args.get("current_page"))


