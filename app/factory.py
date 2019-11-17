import json
from flask import Flask
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://epic-user:password@192.168.16.66:27017/epicuriousDB"
mongo = PyMongo(app, retryWrites=False)

@app.route('/')
def recipe_factory():
    with open('../data/full_format_recipes.json','r') as fp:
        recipes = json.load(fp)
    mongo.db.recipesCollection.insert_many(recipes)
    return 'RECIPE SUCCESSFULLY POPULATED'

if __name__ == '__main__':
    app.run(debug = True)