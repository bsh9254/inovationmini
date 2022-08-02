from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

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
    return redirect(url_for("main"))

# 로그인 처리 라우팅.
@app.route("/login", methods = ["POST"])
def login_process():
    username = request.form["username"]
    password = request.form["password"]
    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)