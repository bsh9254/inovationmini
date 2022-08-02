from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta_review


@app.route('/')
def home():
    return render_template('detail2.html')

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


@app.route("/reviews", methods=["GET"])
def web_reviews_get():
    review_list = list(db.reviews.find({}, {'_id': False}))
    return jsonify({'reviews':review_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
