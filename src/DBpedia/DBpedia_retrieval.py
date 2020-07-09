from SPARQLWrapper import SPARQLWrapper, JSON
import networkx as nx
import matplotlib.pyplot as plt
import operator, json, os


class DBpedia_Retrieval(object):
    def __init__(self):
        self.dbpedia_data = '../../files/dbpedia_data.json'
    
    def write_json_file(self, file_name, to_write):
        file = open(file_name, 'w')
        json.dump(to_write, file, indent = 4)
        file.close()

    def query_dbpedia(self):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            PREFIX dbc: <http://dbpedia.org/resource/Category:>

            SELECT distinct ?name  ?person ?subject WHERE {
              ?person foaf:name ?name. 
              ?person dct:subject dbc:Computer_scientists.  
              ?person dct:subject ?subject.
            filter regex(?subject, "http://dbpedia.org/resource/Category:Computer_scientists")
            }
            ORDER BY ?name
        """)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return results



    def main(self):
        query_result = self.query_dbpedia()

        # Write DBpedia result on json file
        if not os.path.exists(self.dbpedia_data):   self.write_json_file(self.dbpedia_data, query_result)



if __name__ == '__main__':
    DBpedia_Retrieval_Obj = DBpedia_Retrieval().main()


