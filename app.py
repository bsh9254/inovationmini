from flask import Flask, render_template

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

if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)