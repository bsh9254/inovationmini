from flask import Flask, render_template, request, url_for, redirect, jsonify, make_response
from pymongo import MongoClient
from flask_jwt_extended import *

app = Flask(__name__)

app.config.update(
    JWT_SECRET_KEY = "GLAMPEDIA"
)

jwt = JWTManager(app)

client = MongoClient("mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority")
glampediaDB = client["Glampedia"]
userDB = glampediaDB["User"]

# 메인 페이지 라우팅.
@app.route("/", methods = ["GET"])
def main():
    return "Hello World!!"

# 회원가입 페이지 라우팅.
@app.route("/signup", methods = ["GET"])
def signup():
    return render_template("signup.html")

# 로그인 페이지 라우팅.
@app.route("/login", methods = ["GET"])
def login():
    return render_template("login.html")

# 회원가입 처리 라우팅.
@app.route("/signup", methods = ["POST"])
def signup_process():
    username = request.form["username"]
    password = request.form["password"]
    photo = request.files["photo"]
    nickname = request.form["nickname"]
    introduction = request.form["introduction"]
    user = {
        "username": username,
        "password": password,
        "nickname": nickname,
        "introduction": introduction
    }
    userDB.insert_one(user)
    return redirect(url_for("main"))

# 로그인 처리 라우팅.
@app.route("/login", methods = ["POST"])
def login_process():
    username = request.form["username"]
    password = request.form["password"]
    user = userDB.find_one({"username": username, "password": password})
    if user is not None:
        access_token = create_access_token(identity = username)
        response = make_response(render_template("login.html"))
        response.set_cookie("access_token", access_token)
        return response
    else:
        print("No user")
    return redirect(url_for("main"))

@app.route("/protected", methods = ["GET"])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200

if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)