from flask import Blueprint, redirect, render_template

hm = Blueprint('hm', __name__)



@hm.route("/")
def home():
    return redirect("/people/login")


@hm.route('/index')
def index():
    # return "index..."
    return render_template("index.html")

