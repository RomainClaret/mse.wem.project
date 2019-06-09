#!/usr/bin/env python3

import bz2
import csv
import sys
from collections import namedtuple

from py2neo import Graph, Node, Relationship


def read_publications(filename):
    with bz2.open(filename, 'rt', ) as infile:
        reader = csv.reader(infile)
        data = namedtuple('record', next(reader))
        for record in map(data._make, reader):
            yield record


categories_cache = {}
def get_category_node(graph, tx, cat):
    global categories_cache

    node = categories_cache.get(cat)
    if node:
        return node

    node = graph.nodes.match('Category', label=cat).first()
    if not node:
        node = Node('Category', label=cat)
        tx.create(node)

    categories_cache[cat] = node
    return node


authors_cache = {}
def get_author_node(graph, tx, author):
    global authors_cache

    node = authors_cache.get(author)
    if node:
        return node

    node = graph.nodes.match('Author', author=author).first()
    if not node:
        node = Node('Author', label=author)
        tx.create(node)

    authors_cache[author] = node
    return node


affiliations_cache = {}
def get_affiliation_node(graph, tx, affiliation):
    global affiliations_cache

    node = affiliations_cache.get(affiliation)
    if node:
        return node

    node = graph.nodes.match('Affiliation', label=affiliation).first()
    if not node:
        node = Node('Affiliation', label=affiliation)
        tx.create(node)

    affiliations_cache[affiliation] = node
    return node


def populate(filename):
    graph = Graph('bolt://127.0.0.1:7687/db/data')
    
    graph.delete_all()

    cnt = 0
    for record in read_publications(filename):
        tx = graph.begin()

        # publication node
        pub = Node('Publication', id=record.id, title=record.title)
        tx.create(pub)

        # primary category node
        cat = get_category_node(graph, tx, record.primary_category)
        rel = Relationship(pub, "HAS_PRIMARY_CATEGORY", cat)
        tx.create(rel)

        # secondary categories nodes
        for c in record.primary_category.split('|'):
            if c:
                cat = get_category_node(graph, tx, c)
                rel = Relationship(pub, "HAS_CATEGORY", cat)
                tx.create(rel)

        # authors nodes
        for a in record.authors.split('|'):
            if a:
                author = get_author_node(graph, tx, a)
                rel = Relationship(author, "WROTE", pub)
                tx.create(rel)

        # affiliations nodes
        for a in record.affiliations.split('|'):
            if a:
                affiliation = get_affiliation_node(graph, tx, a)
                rel = Relationship(pub, "IS_AFFILIATE", affiliation)
                tx.create(rel)

        tx.commit()

        cnt += 1
        if cnt % 100 == 0:
            print('-----')
            print('Publication inserted: ', cnt)
            print('Number of nodes:', len(graph.nodes))
            print('Number of relations:', len(graph.relationships))


if __name__ == '__main__':
    populate(sys.argv[1])
