from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import Binary, Code, json_util

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://epic-user:password@192.168.16.66:27017/epicuriousDB"
mongo = PyMongo(app, retryWrites=False)

@app.route('/catalogue', methods = ['GET'])
def dashboard():
    page = request.args.get('page', default = 1, type = int)

    cursor = mongo.db.recipesCollection.find({}).skip(page - 1).limit(20)
    documents = [document for document in cursor]

    response = app.response_class(
        response=json_util.dumps(documents),
        status=200,
        mimetype='application/json'
    )

    return response

if __name__ == '__main__':
    app.run(debug = True)
