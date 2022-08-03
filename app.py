from flask import Flask, jsonify, render_template, request, url_for, redirect, make_response
from pymongo import MongoClient
from flask_jwt_extended import *
from datetime import *
import os

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
    glampings = list(glampediaDB.Glamping_info.find({}, {'_id': False}))
    glampings_star=list(glampediaDB.reviews.find({}, {'_id': False}))
    star_list=list([0]*(len(glampings_star)))
    counting_list=list([0]*(len(glampings_star)))
    current_user = get_jwt_identity()


    for i in range(0,len(glampings_star)):
        num=int(glampings_star[i]['num'])+1
        star_list[num]+=int(glampings_star[i]['star'])
        counting_list[num]+=1

    for j in range(0,len(star_list)):
        if star_list[j]!=0:
            star_list[j]='⭐'*(int(star_list[j]//counting_list[j]))
    
    if current_user is None: # JWT 토큰 자체가 없을 때, 즉, 최초 접속 시.
        return render_template("mainpage.html",mainpage=glampings,mainstar=star_list)
    user = userDB.find_one({"username": current_user})
    return render_template("mainpage.html", current_user = user["nickname"], mainpage = glampings,mainstar=star_list)


# 상세 페이지 라우팅
@app.route("/detailpg/<num>")
@jwt_required(optional = True)
def detailinto(num):
    current_user = get_jwt_identity()
    user = userDB.find_one({"username": current_user})

    review_list = list(glampediaDB.reviews.find({'num': num}))

    sum = 0

    for i in range(0,len(review_list)):
        sum += int(review_list[i]['star'])

    if sum != 0:
        a_star = sum / len(review_list)
        avg_star = round(a_star, 1)
    else:
        avg_star =0

    print(avg_star)

    if user is not None:
        return render_template("detail.html",
                               current_user_name=user["nickname"],
                               current_user_img="photos/" + user["filename"],
                               current_user_intro=user["introduction"], dateilpg=review_list, detail_star = avg_star)
    else:
        return render_template("detail.html", dateilpg=review_list, detail_star = avg_star)

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
    name_receive = request.form['name_give']
    num_receive = request.form['num_give']

    doc = {
        'comment': comment_recevie,
        'star': star_recevie,
        'num': num_receive,
        'name':name_receive
    }
    glampediaDB.reviews.insert_one(doc)

    return jsonify({'msg':'등록 완료'})

# 별점 코멘트 보여주기 라우팅
@app.route("/reviews", methods=["GET"])
def web_reviews_get():
    review_list = list(glampediaDB.reviews.find({}, {'_id': False}))
    return  render_template("detail.html")

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
        try:
            original_umask = os.umask(0)
            os.makedirs("./static/photos", 0o0777, exist_ok=True)
        finally:
            os.umask(original_umask)
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
    if username == "":
        return jsonify({
            "message": "Empty"
        })
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
    user = userDB.find_one({"username": current_user})

    if current_user is None:
        return redirect(url_for("login"))
    else:
        return render_template("mypage.html",
                               current_user_name=user["nickname"],
                               current_user_img="photos/" + user["filename"],
                               current_user_intro=user["introduction"],
                               current_user_email=user["username"])

# 마이 페이지 GET
@app.route("/mypage_review", methods=["GET"])
def mypage_get():
    review_list = list(glampediaDB.reviews.find({}, {'_id': False}))
    return jsonify({'reviews': review_list})

# Authorization 테스트 페이지.
@app.route("/protected", methods = ["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as = current_user), 200

# 서버 구동.
if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)

