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


def get_category_node(graph, tx, cat):
    node = graph.nodes.match('Category', label=cat).first()
    if not node:
        node = Node('Category', label=cat)
        tx.create(node)
    return node


def get_author_node(graph, tx, author):
    node = graph.nodes.match('Author', author=author).first()
    if not node:
        node = Node('Author', label=author)
        tx.create(node)
    return node


def populate(filename):
    graph = Graph('bolt://127.0.0.1:7687/db/data')
    
    graph.delete_all()

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
            cat = get_category_node(graph, tx, c)
            rel = Relationship(pub, "HAS_CATEGORY", cat)
            tx.create(rel)

        # authors nodes
        for a in record.authors.split('|'):
            author = get_author_node(graph, tx, a)
            rel = Relationship(author, "WROTE", pub)
            tx.create(rel)

        tx.commit()

    print('Number of nodes:', len(graph.nodes))
    print('Number of relations:', len(graph.relationships))


if __name__ == '__main__':
    populate(sys.argv[1])
