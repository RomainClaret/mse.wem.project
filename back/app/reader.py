import bz2
import csv


def readCsv():
    file_name = "arxiv_data_cs_all.csv.bz2"
    try:
        # csvfile = open(file_name, 'rt', encoding="utf8")
        csvfile = bz2.open(file_name, 'rt', encoding="utf8")  # open the file
        csvReader = csv.reader(csvfile, delimiter=",")
    except:
        print("File not found")
    d = dict()
    l = list()
    i = 0
    for row in csvReader:
        # id,updated,published,title,summary,authors,affiliations,doi,journal_ref,pdf_link,primary_category,categories
        if i > 0:
            d[row[1]] = row[0]
            tempIdPdf = row[9].split("/")
            idPdf = ""
            documents = []
            if len(tempIdPdf) > 4:
                idPdf = tempIdPdf[4]
                documents.append({"type": "pdf"})
            l.append({
                "id":row[0],
                "idPage": row[0].split("/")[4],
                "updated": row[1],
                "published": row[2],
                "title": row[3],
                "summary": row[4],
                "authors": row[5].split("|"),
                "affiliations": row[6],
                "doi": row[7],
                "journal_ref": row[8],
                "pdf_link": idPdf,
                "primary_category": row[10],
                "categories": row[11].split("|"),
                "documents": documents,
            })
        i = i + 1
    print("Number of lignes: " + str(len(l)))
    return l
