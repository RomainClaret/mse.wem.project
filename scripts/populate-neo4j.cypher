
USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j-data/publications.csv' AS line
CREATE (:Publication { id: line.id, updated: line.updated, published: line.published, title: line.title, summary: line.summary, doi: line.doi, journal_ref: line.journal_ref, pdf_link: line.pdf_link, categories: line.categories, authors: line.authors });
CREATE INDEX ON :Publication(id);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j-data/categories.csv' AS line
CREATE (:Category { id: toInteger(line.id), name: line.category });
CREATE INDEX ON :Category(id);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j-data/authors.csv' AS line
CREATE (:Author { id: toInteger(line.id), name: line.author });
CREATE INDEX ON :Author(id);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM 'file:///neo4j-data/affiliations.csv' AS line
CREATE (:Affiliation { id: toInteger(line.id), name: line.affiliation });
CREATE INDEX ON :Affiliation(id);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM "file:///neo4j-data/publications_categories.csv" AS line
MATCH (p:Publication {id: line.publication_id}), (c:Category {id: toInteger(line.category_id)})
CREATE (p)-[:HAS_CATEGORY]->(c);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM "file:///neo4j-data/publications_primary_categories.csv" AS line
MATCH (p:Publication {id: line.publication_id}), (c:Category {id: toInteger(line.category_id)})
CREATE (p)-[:HAS_PRIMARY_CATEGORY]->(c);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM "file:///neo4j-data/publications_authors.csv" AS line
MATCH (p:Publication {id: line.publication_id}), (a:Author {id: toInteger(line.author_id)})
CREATE (a)-[:WROTE]->(p);

USING PERIODIC COMMIT 500
LOAD CSV WITH HEADERS FROM "file:///neo4j-data/publications_affiliations.csv" AS line
MATCH (p:Publication {id: line.publication_id}), (a:Affiliation {id: toInteger(line.affiliation_id)})
CREATE (p)-[:IS_AFFILIATED]->(a);
