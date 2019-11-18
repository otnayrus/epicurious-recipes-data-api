from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from bson import Binary, Code, json_util
from bson.objectid import ObjectId


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://epic-user:password@192.168.16.66:27017/epicuriousDB"
mongo = PyMongo(app, retryWrites=False)


# Read Documents from DB
@app.route('/catalogue', methods = ['GET'])
def dashboard():
    page = request.args.get('page', default = 1, type = int)
    title = request.args.get('title', default = 1, type = str)

    cursor = mongo.db.recipesCollection.find({"title":{"$regex" : ".*" + title + ".*"}}).skip(page - 1).limit(20)
    documents = [document for document in cursor]

    response = app.response_class(
        response=json_util.dumps(documents),
        status=200,
        mimetype='application/json'
    )

    return response


# Create a Document and Write to DB
@app.route('/create', methods = ['POST'])
def create_recipe():
    req = request.get_json(force=True)
    mongo.db.recipesCollection.insert(req)
    return jsonify({"success":"RECIPE HAS BEEN ADDED ON THE CATALOGUE"})


# Delete a Document from DB
@app.route('/delete', methods = ['POST'])
def delete_recipe():
    req = request.get_json(force=True)
    mongo.db.recipesCollection.delete_one({"_id":ObjectId(req['_id']['$oid'])})
    return jsonify({"success":"RECIPE HAS BEEN DELETED ON THE CATALOGUE"})


# Update a Document and Write to DB
@app.route('/update', methods = ['POST'])
def update_recipe():
    req = request.get_json(force=True)
    data = removekey(req, '_id')
    mongo.db.recipesCollection.update_one({
        '_id': ObjectId(req['_id']['$oid'])
    },{
        '$set': data
    }, upsert=False)
    return jsonify({"success":"RECIPE HAS BEEN UPDATED ON THE CATALOGUE"})


# DB Statistics Page
@app.route('/stats', methods = ['GET'])
def stats():
    data = {}
    data['count'] = mongo.db.recipesCollection.count_documents({})
    data['rating_dist'] = mongo.db.recipesCollection.aggregate([
        {
            "$group": {
                "_id":"$rating",
                "count":{"$sum":1}
            }
        }
    ])
    data['avg_calories_rating'] = mongo.db.recipesCollection.aggregate([
        {
            "$group": {
                "_id":"$rating",
                "avg_cal":{"$avg":"$calories"}
            }
        }
    ])

    response = app.response_class(
        response=json_util.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


def removekey(d, key):
    r = dict(d)
    del r[key]
    return r


if __name__ == '__main__':
    app.run(debug = True)
