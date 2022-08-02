from pymongo import MongoClient
client = MongoClient('mongodb+srv://glampedia:1234@cluster0.uf0pxtj.mongodb.net/?retryWrites=true&w=majority')
db = client.dbsparta_review

doc = {
    'name' : 'bob',
    'age' : 27
}

db.reviews.insert_one(doc)