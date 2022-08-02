from flask import Flask, jsonify, render_template, request, url_for, redirect, make_response
from pymongo import MongoClient

app = Flask(__name__)


client = MongoClient('mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority')
db = client.Glampedia


# 메인 페이지 라우팅.
@app.route('/')
def main():
    return render_template('main.html')

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
    photo = request.files["photo"]
    nickname = request.form["nickname"]
    introduction = request.form["introduction"]
    name = username.replace("@", ".")
    extension = photo.filename.split(".")[-1]
    photo.save(f"static/photos/{name}.{extension}")
    user = {
        "username": username,
        "password": password,
        "nickname": nickname,
        "introduction": introduction
    }
    userDB.insert_one(user)
    return redirect(url_for("login"))

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
        return render_template("login.html", no_user = True)

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

# 디테일 페이지 라우팅
@app.route('/detail')
def detail():
    return render_template('detail2.html')

# 별점 코멘트 등록하기 라우팅
@app.route("/reviews", methods=["POST"])
def web_reviews_post():
    comment_recevie = request.form['comment_give']
    star_recevie = request.form['star_give']

    doc = {
        'comment': comment_recevie,
        'star': star_recevie
    }
    db.reviews.insert_one(doc)

    return jsonify({'msg':'등록 완료'})

# 별점 코멘트 보여주기 라우팅
@app.route("/reviews", methods=["GET"])
def web_reviews_get():
    review_list = list(db.reviews.find({}, {'_id': False}))
    return jsonify({'reviews':review_list})


@app.route("/Glamping", methods=["GET"])
def glamping_get():
    g_list = list(db.Glamping_info.find({}, {'_id': False}))
    return jsonify({'g_list': g_list})



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
