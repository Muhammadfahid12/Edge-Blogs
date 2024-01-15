import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required


# configuration application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///blog.db")

# starting...

# by default request method is GET
@app.route("/")
def index():
    # session.clear() this line to be reviewed so that when "/" is redirected it did not clear session
    return render_template("layout.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    session.clear()

    if request.method == "GET":
        return render_template("register.html")
    else:
        # getting data from front-end
        name = request.form.get("username").lower()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check that name should be present and password and confirmation shoudld be matched
        if not name:
            return apology("please enter username", 403)

        elif not password:
            return apology("please write password", 403)

        elif not confirmation:
            return apology("must write confirm password", 403)

        elif confirmation != password:
            return apology("passwords should match", 403)

        result = db.execute("SELECT * from users WHERE name = ?", name)

        if len(result) != 0:
            return apology("user already exists", 400)

        hash = generate_password_hash(password)

        db.execute("INSERT INTO users(name ,hash) VALUES(?,?)", name, hash)

        results = db.execute("SELECT * FROM users WHERE name = ?", name)

        # Remember which user has logged in
        session["user_id"] = results[0]["user_id"]
        return redirect("blog")


# login functionality


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")

        # check if name is empty
        if not name:
            return apology("Please Enter Name", 400)
        elif not password:
            return apology("Please Enter Password", 400)

        # getting data from database to ensure user is registered

        result = db.execute("SELECT * FROM users WHERE name = ?", name)

        if len(result) != 1 or not check_password_hash(
            result[0]["hash"], request.form.get("password")
        ):
            return apology("Incorrect username/password", 400)

        # remember which user has loggin in

        session["user_id"] = result[0]["user_id"]

        return redirect("/blog")


# logout


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# function for writing blog


@app.route("/blog")
@login_required
def blog():

        results = db.execute("SELECT * FROM blog_data")
        # user = db.execute("SELECT name FROM users WHERE user_id = ? ",user_id)
        for blog in results:
            user_id = blog["user_id"]
            blog_title = blog["blog_title"]
            blog_content = blog["blog_content"]
            timestamp = blog["timestamp"]
        return render_template("blog.html", result=results)

@app.route("/new-story", methods = ["GET","POST"])
@login_required
def write():

    if request.method == "GET":
        return render_template("write.html")

    else:
      title = request.form.get("title")
      content = request.form.get("content")

      if not title:
        return apology("Write title please", 400)
      elif not content:
            return apology("Please Write anyting in blog to submit", 400)

        # also check if title is already exist in our website,it is not good and return apology
      results = db.execute("SELECT * FROM blog_data")
      for blog in results:
            if title == blog["blog_title"]:
                return apology("This title blog is already written",400)
      db.execute(
            "INSERT INTO blog_data(user_id,blog_title,blog_content,timestamp) VALUES(?,?,?,CURRENT_TIMESTAMP)",
            session["user_id"],
            title,
            content,
        )
      return redirect("blog")




@app.route("/blog/<title>" )
def read_blog(title):
      results = db.execute("SELECT * FROM blog_data JOIN users ON blog_data.user_id = users.user_id WHERE blog_title = ?",title)
      return render_template("/blogread.html",results = results[0])


def delete(title):
    results = db.execute("delete FROM blog_data WHERE blog_title = ?",title)
    return redirect("/profile")


@app.route("/profile", methods = ["POST","GET"])
@login_required
def profile():
    # get data of the user in the session and represents his/her data in a seperate box
    if request.method == "GET":
        results = db.execute("SELECT * FROM blog_data WHERE user_id = ?",session["user_id"])
        # if not results:
        #     return apology("you have not written any story yet")
        for blog in results:
            blog_title = blog["blog_title"]
            blog_content = blog["blog_content"]
            # time = blog["timestamp"]
        return render_template("profile.html",result = results)

    else:
        title = request.form.get("title")
        return delete(title)
