from flask import Flask

app = Flask(__name__)

@app.route("/", methods = ["GET"])
def main():
    return "Hello World!!"

if __name__ == "__main__":
    app.run("0.0.0.0", port = 5000, debug = True)