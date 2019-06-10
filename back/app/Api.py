import json
from urllib.request import urlopen
import xml.etree.ElementTree as ET
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from gensim.matutils import Sparse2Corpus
from gensim.models.ldamodel import LdaModel
from gensim.matutils import Sparse2Corpus
import numpy as np


from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api, reqparse

from py2neo import Graph

app = Flask(__name__)
api = Api(app)

graph = Graph('bolt://neo4j:7687/db/data')
#graph = Graph('bolt://localhost:7687/db/data')

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

# LDA MAGIC INIT
df = pd.read_pickle("arxiv_data_cs_all.pickle.bz2")
df_min = 2 #100
df_max = 0.1 #0.2
cvec = CountVectorizer(min_df=df_min, max_df=df_max, stop_words='english', 
                       token_pattern='(?u)\\b\\w\\w\\w+\\b')
trans = cvec.fit_transform(df.summary.tolist())
corpus = Sparse2Corpus(trans, documents_columns=False)
id_map = dict((v, k) for k, v in cvec.vocabulary_.items())
n_topics = 10
n_passes = 50
model_path = "arxiv_data_cs_all_ntopics_"+str(n_topics)+"_npasses_"+str(n_passes)+"_nvoc_"+str(len(list(id_map)))+"_dfmin_"+str(df_min)+"_dfmax_"+str(int(df_max*100))+".model"
ldamodel = LdaModel.load(model_path)
df_papers_path = "arxiv_data_cs_all_ntopics_"+str(n_topics)+"_npasses_"+str(n_passes)+"_nvoc_"+str(len(list(id_map)))+"_dfmin_"+str(df_min)+"_dfmax_"+str(int(df_max*100))+"_paperdf.pickle.bz2"
df_papers = pd.read_pickle(df_papers_path)


def get_lda_similarities(summary):
    results = []
    for i, item in enumerate(get_similar_topics_distribution(summary)):
        if item > 0:
            results.append([i,item])
    results.sort(key=lambda x: x[1], reverse=True)

    results_topics = []
    for r in results:
        results_topics.append(r[0])

    df_filtered_papers = df_papers.copy()
    for r in results:
        df_filtered_papers = df_filtered_papers.where(df_filtered_papers[r[0]]>0).dropna()
    for i in range(len(results)-1):
        df_filtered_papers = df_filtered_papers.where(df_filtered_papers[results[i][0]]>df_filtered_papers[results[i+1][0]]).dropna()

    similar_papers_index = df_filtered_papers.index.values.astype(int)

    similar_papers_by_index = []
    for i in similar_papers_index:
        similar_papers_by_index.append([i,df.iloc[i,0]])
    similar_papers_by_index

    similar_papers_summaries = []
    for i in similar_papers_index:
        similar_papers_summaries.append(df.iloc[i,4])

    similar_papers_ranked_by_id = []
    for i, abstract in enumerate(similar_papers_summaries):
        if summary == abstract:
                continue
        similar_papers_ranked_by_id.append([i, get_score(summary, abstract)])

    similar_papers_ranked_by_id = sorted(similar_papers_ranked_by_id, key=lambda x: x[1], reverse=True)

    ranked_papers = []
    for r in similar_papers_ranked_by_id:
        ranked_papers.append(similar_papers_by_index[r[0]])

    return ranked_papers



def get_score(abstract_1, abstract_2):
    return np.dot(get_similar_topics_distribution(abstract_1),
                  get_similar_topics_distribution(abstract_2))

def get_similar_topics_distribution(abst_to_match):
    topics_array = np.zeros(n_topics)
    
    trans = cvec.transform(list([abst_to_match])) 
    corpus = Sparse2Corpus(trans, documents_columns=False)
    results = list(ldamodel.get_document_topics(bow=corpus))[0]
    
    for items in results:
        topics_array[items[0]] = items[1]
    return topics_array

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


def arxiv_to_front_from_df(ranked_articles_by_id):
    arxiv_id_url_regex = r"(\d{4}\.(\d{5}|\d{4})|\d{7})"
    print(len(ranked_articles_by_id))

    articles = []
    for article in ranked_articles_by_id:
        article_index = article[0]

        paper_id = re.findall(arxiv_id_url_regex,df.iloc[article_index,0])[0]
        arxiv_link = df.iloc[article_index,0]
        arxiv_title = sanitize_str(df.iloc[article_index,3])
        arxiv_summary = sanitize_str(df.iloc[article_index,4])
        arxiv_author = df.iloc[article_index,5]
        arxiv_pdf = df.iloc[article_index,9]
        arxiv_primary_category = df.iloc[article_index,10]
        arxiv_categories = df.iloc[article_index,11]

        articles.append({
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
        })
        
    return articles

def arxiv_to_front(list_articles):
    arxiv_id_url_regex = r"\d{4}\.\d{5}"
    
    articles = []
    for article in list_articles:
        paper_id = re.findall(arxiv_id_url_regex,article[0])[0]
        arxiv_link = article[0]
        arxiv_title = sanitize_str(article[3])
        arxiv_summary = sanitize_str(article[4])
        arxiv_author = article[5]
        arxiv_pdf = article[9]
        arxiv_primary_category = article[10]
        arxiv_categories = article[11]

        articles.append({
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
        })


        

    return articles

def fetch_arxiv(search):
    #text_abstract = "We introduce a new family of deep neural network models. Instead of specifying a discrete sequence of hidden layers, we parameterize the derivative of the hidden state using a neural network. The output of the network is computed using a black-box differential equation solver. These continuous-depth models have constant memory cost, adapt their evaluation strategy to each input, and can explicitly trade numerical precision for speed. We demonstrate these properties in continuous-depth residual networks and continuous-time latent variable models. We also construct continuous normalizing flows, a generative model that can train by maximum likelihood, without partitioning or ordering the data dimensions. For training, we show how to scalably backpropagate through any ODE solver, without access to its internal operations. This allows end-to-end training of ODEs within larger models."
    #

    arxiv_id_regex = r"\d{4}\.\d{5}.*"
    arxiv_id_url_regex = r"\d{4}\.\d{5}"
    
    arxiv_id = re.findall(arxiv_id_regex,search)[0]

    if arxiv_id:
        paper_id = re.findall(arxiv_id_url_regex,arxiv_id)[0]
        base_url = 'http://export.arxiv.org/api/query?search_query='
        url = base_url + paper_id
        data = urlopen(base_url + paper_id, None, timeout=120).read()
        parsed = ET.fromstring(data)
        parsed_list = parse_to_list(parsed)

        summary = parsed_list[0][4]

        ranked_articles_by_id = get_lda_similarities(summary)

        return arxiv_to_front_from_df(ranked_articles_by_id)
    
    return None


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


class Search(Resource):

    def searchData(self, search):
        neo4j_result = fetch_neo4j_articles(search)

        if len(neo4j_result) == 0:
            return fetch_arxiv(search)
        else:
            return neo4j_result

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
