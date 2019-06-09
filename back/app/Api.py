import json

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

from reader import readCsv

app = Flask(__name__)
api = Api(app)


# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# pip install -U flask-cors
# pip install flask_restful

class Search(Resource):
    def searchData(self, search):
        return inMemory

    def get(self, search):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=int)
        parser.add_argument('pageSize', type=int)
        args = parser.parse_args()
        page_size = args["pageSize"]
        page = args["page"]
        result = self.searchData(search)
        total = len(result)
        print(str(page_size) + " " + search + " " + str(page))
        return {"total": total, "page": page,
                "pageSize": page_size,
                "search": search,
                "result": result[page_size * page:(page_size * (page + 1))]}, 200


class Stat(Resource):
    def get(self, idDocument, category):
        result = {
            'Year': stat_categories["Year"],
            'Month': stat_categories["Month"],
            'Values': stat_categories[category]
        }
        return {"idDocument": idDocument,
                "category": category,
                "result": result}, 200


def readStat():
    with open('arxiv_data_cs_all_cats_stats_years_months.json') as json_file:
        return json.load(json_file)


stat_categories = readStat()
api.add_resource(Stat, "/api/stat/<string:idDocument>/<string:category>")
api.add_resource(Search, "/api/search/<string:search>")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
inMemory = readCsv()

app.run(debug=False, host='0.0.0.0', port=5000)
