from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority')
db = client.Glampedia

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route("/Glamping", methods=["GET"])
def glamping_get():
    g_list = list(db.Glamping_info.find({}, {'_id': False}))
    return jsonify({'g_list': g_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5555, debug=True)