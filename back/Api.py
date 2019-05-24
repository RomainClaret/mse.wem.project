from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)


# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# pip install -U flask-cors
# pip install flask_restful

class Search(Resource):
    def get(self, search):
        parser = reqparse.RequestParser()
        parser.add_argument('page', type=str)
        parser.add_argument('pageSize', type=int)
        args = parser.parse_args()
        pageSize = args["pageSize"]
        page = args["page"]
        total = 1
        result = [{"authors": ["aut1", "aut2", "aut3"],
                   "title": "title",
                   "idPage": 1905.00871,
                   "abstract": "Abstract",
                   "tags": [{"description": "tag1"}],
                   "documents": [{"type": "pdf"}, {"type": "ps"}, {"type": "format"}],
                   }]
        return {"total": total, "page": page,
                "pageSize": pageSize,
                "search": search,
                "result": result}, 200


class Stat(Resource):
    def get(self, idDocument, category):
        result = [{"authors": ["aut1", "aut2", "aut3"],
                   "title": "title",
                   "idPage": 1905.00871,
                   "abstract": "Abstract",
                   "tags": [{"description": "tag1"}],
                   "documents": [{"type": "pdf"}, {"type": "ps"}, {"type": "format"}],
                   }]
        return {"idDocument": idDocument,
                "category": category,
                "result": result}, 200


api.add_resource(Stat, "/api/stat/<string:idDocument>/<string:category>")
api.add_resource(Search, "/api/search/<string:search>")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.run(debug=True)
