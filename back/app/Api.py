import json
from urllib.request import urlopen

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

from py2neo import Graph

app = Flask(__name__)
api = Api(app)

graph = Graph('bolt://neo4j:7687/db/data')

query = """
MATCH (pub:Publication)-[]-(rel), (from:Publication {id: {pub}})
WITH {item: id(pub), categories: collect(id(rel))} as pubData, [id(from)] as sourceIds
WITH collect(pubData) as data, sourceIds

CALL algo.similarity.overlap.stream(data, {sourceIds: sourceIds, concurrency:1, similarityCutoff: 0.6})
YIELD item1, item2, similarity
WITH algo.getNodeById(item1) AS from, algo.getNodeById(item2) AS to, similarity

RETURN to.id AS id, to.title as title, to.summary as summary, to.pdf_link as pdf_link, to.categories as categories, to.authors as authors, similarity
ORDER BY similarity DESC
LIMIT 50
"""

def fetch_neo4j_articles(pub):
    return [
        {
            'id': row['id'],
            'title': row['title'],
            'summary': row['summary'],
            'authors': row['authors'].split(','),
            'affiliations': [],
            'pdf_link': row['pdf_link'],
            'primary_category': [],
            'categories': row['categories'].split(','),
            'documents': [{'type': 'pdf'}],
            'similarity': row['similarity'],
        }
        for row in graph.run(query, pub=pub)
    ]


def fetch_arxiv(search):
    arxiv_id_regex = "^\d{4}\."
    arxiv_id = re.search(arxiv_id_regex, search)
    
    #if arxiv_url:
    if arxiv_id:
        paper_id = search
        base_url = 'http://export.arxiv.org/api/query?search_query='
        data = urlopen(base_url + paper_id, None, timeout=120).read()
        parsed = ET.fromstring(data)
        parsed_list = parse_to_list(parsed)
        
        arxiv_link = parsed_list[0][0]
        arxiv_title = sanitize_str(parsed_list[0][3])
        arxiv_summary = sanitize_str(parsed_list[0][4])
        arxiv_author = parsed_list[0][5]
        arxiv_pdf = paper_id
        arxiv_primary_category = parsed_list[0][10]
        arxiv_categories = parsed_list[0][11]
        
        print("arxiv_link",arxiv_link)
        print("arxiv_title",arxiv_title)
        print("arxiv_summary",arxiv_summary)
        print("arxiv_author",arxiv_author)
        print("arxiv_pdf",arxiv_pdf)
        print("arxiv_primary_categories",arxiv_primary_category)
        print("arxiv_categories",arxiv_categories)

        return [{
            "id":arxiv_link,
            "idPage": paper_id,
            "updated": "updated",
            "published": "published",
            "title": arxiv_title,
            "summary": arxiv_summary,
            "authors": arxiv_author,
            "affiliations": "affiliations",
            "doi": "doi",
            "journal_ref": "journal_ref",
            "pdf_link": arxiv_pdf,
            "primary_category": arxiv_primary_category,
            "categories": arxiv_categories,
            "documents": [{"type": "pdf"}],
        }]
    
    return None


class Search(Resource):

    def searchData(self, search):
        return fetch_neo4j_articles(search)

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
