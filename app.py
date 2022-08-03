from flask import Flask, jsonify, render_template, request, url_for, redirect, make_response
from pymongo import MongoClient
from flask_jwt_extended import *
from datetime import *

app = Flask(__name__)

# JWT Configurations.
app.config.update(
    JWT_SECRET_KEY = "GLAMPEDIA",
    JWT_TOKEN_LOCATION = ["cookies"],
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours = 1)
)

jwt = JWTManager(app)

# MongoDB Atlas 접속.
client = MongoClient("mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority")
glampediaDB = client["Glampedia"]
userDB = glampediaDB["User"]

@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_payload):
    response = make_response(redirect("/"))
    response.delete_cookie("access_token_cookie")
    return response

#메인 페이지 라우팅
@app.route("/", methods = ["GET"])
@jwt_required(optional = True)
def home():
    current_user = get_jwt_identity()
    print(current_user)
    if current_user is None:
        return render_template("mainpage.html")
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

# 상세 페이지 라우팅
@app.route("/detailpg")
@jwt_required(optional = True)
def detailinto():
    current_user = get_jwt_identity()
    user = userDB.find_one({"username": current_user})
    if user is not None:
        return render_template("detail.html",
                               current_user_name=user["nickname"],
                               current_user_img="photos/" + user["filename"],
                               current_user_intro=user["introduction"])
    else:
        return render_template("detail.html")

# 상세 페이지 GET
@app.route("/Glamping", methods=["GET"])
def glamping_get():
    g_list = list(glampediaDB.Glamping_info.find({}, {'_id': False}))
    return jsonify({'g_list': g_list})

# 별점 코멘트 등록하기 라우팅
@app.route("/reviews", methods=["POST"])
def web_reviews_post():
    comment_recevie = request.form['comment_give']
    star_recevie = request.form['star_give']

    doc = {
        'comment': comment_recevie,
        'star': star_recevie
    }
    userDB.reviews.insert_one(doc)

    return jsonify({'msg':'등록 완료'})

# 별점 코멘트 보여주기 라우팅
@app.route("/reviews", methods=["GET"])
def web_reviews_get():
    review_list = list(userDB.reviews.find({}, {'_id': False}))
    return jsonify({'reviews':review_list})

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
    filename = ""
    if photo.filename != "":
        extension = photo.filename.split(".")[-1]
        filename = f"{name}.{extension}"
        photo.save(f"static/photos/{filename}")
    user = {
        "username": username,
        "password": password,
        "nickname": nickname,
        "filename": filename,
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

# 마이 페이지 라우팅.
@app.route("/mypage", methods = ["GET"])
@jwt_required(optional = True)
def mypage():
    current_user = get_jwt_identity()
    if current_user is None:
        return redirect(url_for("login"))
    else:
        user = userDB.find_one({"username": current_user})
        return render_template("mypage.html", user = user)

# Authorization 테스트 페이지.
@app.route("/protected", methods = ["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200

# 서버 구동.
if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)

