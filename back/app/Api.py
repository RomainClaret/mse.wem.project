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
    def readStat(self):
        with open('arxiv_data_cs_all_stats_years.json') as json_file:
            return json.load(json_file)

    def get(self, idDocument, category):
        result = {
            'Year': {'0': 2018, '1': 2018, '2': 2018, '3': 2019, '4': 2019, '5': 2019, '6': 2019, '7': 2019},
            'Month': {'0': '12', '1': '11', '2': '10', '3': '05', '4': '04', '5': '03', '6': '02', '7': '01'},
            'Papers': {'0': 1112, '1': 1310, '2': 483, '3': 345, '4': 1378, '5': 1071, '6': 1206, '7': 1095}
        }
        return {"idDocument": idDocument,
                "category": category,
                "result": result}, 200


api.add_resource(Stat, "/api/stat/<string:idDocument>/<string:category>")
api.add_resource(Search, "/api/search/<string:search>")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
inMemory = readCsv()

app.run(debug=False, host='0.0.0.0', port=5000)
