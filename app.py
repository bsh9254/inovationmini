from flask import Flask, jsonify, render_template, request, url_for, redirect, make_response
from pymongo import MongoClient
from flask_jwt_extended import *
import requests

app = Flask(__name__)

app.config.update(
    JWT_SECRET_KEY = "GLAMPEDIA",
    JWT_TOKEN_LOCATION = ["cookies"]
)

jwt = JWTManager(app)

client = MongoClient("mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority")
glampediaDB = client["Glampedia"]
userDB = glampediaDB["User"]

#메인 페이지 라우팅
@app.route("/", methods = ["GET"])
@jwt_required(optional = True)
def home():
    current_user = get_jwt_identity()
    user = userDB.find_one({"username": current_user})
    if user is not None:
        return render_template("mainpage.html", current_user = user["nickname"])
    else:
        return render_template("mainpage.html")

# 메인페이지 GET
@app.route("/mainpg", methods=["GET"])
@jwt_required(optional = True)
def main_get():
    mainpage=list(glampediaDB.Glamping_info.find({},{'_id':False}))

    #tops=list(db.Glamping.find({'star':{"$gte":4.5}},{'_id':False}))
    return jsonify({'mains':mainpage})

# 상세페이지 라우팅
@app.route("/detailpg")
def detailinto():
    return render_template("detail.html")

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
    found_user = userDB.find_one({"username": username})
    if found_user:
        return render_template("signup.html", already_taken = True)
    password = request.form["password"]
    password_repeat = request.form["password-repeat"]
    if not (password == password_repeat):
        return render_template("signup.html", invalid_password = True)
    photo = request.files["photo"]
    nickname = request.form["nickname"]
    introduction = request.form["introduction"]
    name = username.replace("@", ".")
    if photo.filename != "":
        extension = photo.filename.split(".")[-1]
        photo.save(f"static/photos/{name}.{extension}")
    user = {
        "username": username,
        "password": password,
        "nickname": nickname,
        "introduction": introduction
    }
    userDB.insert_one(user)
    access_token = create_access_token(identity = username)
    response = make_response(redirect("/"))
    response.set_cookie("access_token_cookie", access_token)
    return response

# 로그인 처리 라우팅.
@app.route("/login", methods = ["POST"])
def login_process():
    username = request.form["username"]
    password = request.form["password"]
    user = userDB.find_one({"username": username, "password": password})
    if user is not None:
        access_token = create_access_token(identity = username)
        response = make_response(redirect("/"))
        response.set_cookie("access_token_cookie", access_token)
        return response
    else:
        return render_template("login.html", no_user = True)

# 아이디 중복 확인 라우팅.
@app.route("/redundancy_check", methods = ["POST"])
def check_redundancy():
    username = request.form["username"]
    user = userDB.find_one({"username": username})
    if user:
        return jsonify({
            "message": "Already taken"
        })
    else:
        return jsonify({
            "message": "Good to go"
        })

# 로그아웃 처리 라우팅.
@app.route("/logout", methods = ["GET"])
def logout():
    response = make_response(redirect("/"))
    response.delete_cookie("access_token_cookie")
    return response

# Authorization 테스트 페이지.
@app.route("/protected", methods = ["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200

if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)
