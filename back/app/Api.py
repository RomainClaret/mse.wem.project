import json
import re
import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen
# import pandas as pd

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

from reader import readCsv

app = Flask(__name__)
api = Api(app)

#df = pd.read_pickle("arxiv_data_cs_all.pickle.bz2")


# https://codeburst.io/this-is-how-easy-it-is-to-create-a-rest-api-8a25122ab1f3
# pip install -U flask-cors
# pip install flask_restful

class Search(Resource):
    def searchData(self, search):
        
        
        #search = "https://arxiv.org/abs/1906.02642"
        #search = "1906.02642"
        print("searchData:", search)


        #arxiv_url_regex = '^(https|http):\/\/arxiv\.org\/(abs|pdf|ps|format)\/'
        #arxiv_url = re.search(arxiv_url_regex, search)
        
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
            
        else:
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

    
    
def sanitize_str(s):
    if s:
        s = re.sub('[\r\n]+', ' ', s)
        s = re.sub(' +', ' ', s)
        s = re.sub('\$(.|\n)+?\$', '', s)
        s = re.sub('\$\$(.|\n)+?\$\$', '', s)
        s = re.sub('\(', '', s)
        s = re.sub('\s\s+', ' ', s)
        
        return s.strip()
    return s

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

def parse_to_list(parsed):
    XML_ENTRIES = "{http://www.w3.org/2005/Atom}entry"
    XML_ID = "{http://www.w3.org/2005/Atom}id"
    XML_UPDATED = "{http://www.w3.org/2005/Atom}updated"
    XML_PUBLISHED = "{http://www.w3.org/2005/Atom}published"
    XML_TITLE = "{http://www.w3.org/2005/Atom}title"
    XML_SUMMARY = "{http://www.w3.org/2005/Atom}summary"
    XML_AUTHOR = "{http://www.w3.org/2005/Atom}author"
    XML_AUTHOR_NAME = "{http://www.w3.org/2005/Atom}name"
    XML_AUTHOR_AFFILIATION = "{http://arxiv.org/schemas/atom}affiliation"
    XML_DOI = "{http://arxiv.org/schemas/atom}doi"
    XML_JOURNAL_REF = "{http://arxiv.org/schemas/atom}journal_ref"
    XML_LINKS = "{http://www.w3.org/2005/Atom}link"
    XML_PRIMARY_CATEGORY = "{http://arxiv.org/schemas/atom}primary_category"
    XML_CATEGORY = "{http://www.w3.org/2005/Atom}category"
    
    entries_list = []
    entries_root = parsed.findall("./"+XML_ENTRIES)
    
    if parsed.find("./"+XML_ENTRIES):
        for entry in entries_root:        
            entry_list = []

            entry_list.append(entry.find("./"+XML_ID).text) # Entry ID
            entry_list.append(entry.find("./"+XML_UPDATED).text) # Entry Update Date
            entry_list.append(entry.find("./"+XML_PUBLISHED).text) # Entry Published Date
            entry_list.append(entry.find("./"+XML_TITLE).text) # Entry Title
            entry_list.append(entry.find("./"+XML_SUMMARY).text) # Entry Summary

            # List of entry authors and their affiliation is any
            authors_name_list = []
            authors_affiliation_list = []
            for author in entry.findall("./"+XML_AUTHOR):
                authors_name_list.append(author.find("./"+XML_AUTHOR_NAME).text)
                if author.find("./"+XML_AUTHOR_AFFILIATION) != None:
                    authors_affiliation_list.append(author.find("./"+XML_AUTHOR_AFFILIATION).text)
            entry_list.append(authors_name_list)
            entry_list.append(authors_affiliation_list)

            # Entry DOI
            doi = entry.find("./"+XML_DOI)
            if doi is not None:
                entry_list.append(doi.text)
            else:
                entry_list.append(None)

            # Entry Journal Ref
            jref = entry.find("./"+XML_JOURNAL_REF)
            if jref is not None:
                entry_list.append(jref.text)
            else:
                entry_list.append(None)

            # Entry PDF link
            for links in entry.findall("./"+XML_LINKS):
                if (links.attrib.get("title") == "pdf"): entry_list.append(links.attrib.get("href"))

            # Entry primary category
            entry_list.append(entry.find("./"+XML_PRIMARY_CATEGORY).attrib.get("term"))

            # Entry Categories
            authors_categories_list = []
            for category in entry.findall("./"+XML_CATEGORY):
                for term in category.attrib.get("term").split(';'):
                    authors_categories_list.append(term.strip())
            entry_list.append(authors_categories_list)

            # Build entries list
            entries_list.append(entry_list) # Append to main entry list
            
        return entries_list

stat_categories = readStat()
api.add_resource(Stat, "/api/stat/<string:idDocument>/<string:category>")
api.add_resource(Search, "/api/search/<string:search>")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
inMemory = readCsv()

app.run(debug=False, host='0.0.0.0', port=5000)
