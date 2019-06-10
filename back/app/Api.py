import json
from urllib.request import urlopen

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

from py2neo import Graph

app = Flask(__name__)
api = Api(app)

graph = Graph('bolt://neo4j:7687/db/data')


class Search(Resource):

    def searchData(self, search):

        query = """
MATCH (pub:Publication)-[]-(rel), (from:Publication {id: {pub}})
WITH {item: id(pub), categories: collect(id(rel))} as pubData, [id(from)] as sourceIds
WITH collect(pubData) as data, sourceIds

CALL algo.similarity.overlap.stream(data, {sourceIds: sourceIds, concurrency:1, similarityCutoff: 0.6})
YIELD item1, item2, similarity
WITH algo.getNodeById(item1) AS from, algo.getNodeById(item2) AS to, similarity

RETURN to.id AS id, to.title as title, to.summary as summary, to.pdf_link as pdf_link, similarity
ORDER BY similarity DESC
LIMIT 50
"""

        results = graph.run(query, pub=search)
        return [
            {
                'id': row['id'],
                'title': row['title'],
                'summary': row['summary'],
                'authors': [],
                'affiliations': [],
                'pdf_link': row['pdf_link'],
                'primary_category': [],
                'categories': '',
            }
            for row in results
        ]


    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=str)
        parser.add_argument('page', type=int)
        parser.add_argument('pageSize', type=int)
        args = parser.parse_args()
        search = args["id"]
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
        if category == "AllCat":
            result = stat_categories
        else:
            result = {
                'Year': stat_categories["Year"],
                'Month': stat_categories["Month"],
                'Values': stat_categories[category]
            }
        return {"idDocument": idDocument,
                "category": category,
                "result": result}, 200


def readStat():
    with open('arxiv_data_cs_all_stats_primary_cats_years_months.json') as json_file:
        return json.load(json_file)

stat_categories = readStat()
api.add_resource(Stat, "/api/stat/<string:idDocument>/<string:category>")
api.add_resource(Search, "/api/search")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.run(debug=False, host='0.0.0.0', port=5000)
