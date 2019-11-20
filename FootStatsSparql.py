from rdflib import Graph, Literal
from rdflib.namespace import DC, FOAF, RDF


g = Graph()
filename = 'FootStats.ttl'
g.parse(filename, format='turtle')
g.bind('foot','https://footstats.com.br/#')
ans = g.query(
    """SELECT ?x 
        WHERE {
        ?a foot:timede ?liga .
        ?a foaf:firstname ?x .
         FILTER (?liga = "Premier_League") }"""
)

for row in ans :
    print(row.x)