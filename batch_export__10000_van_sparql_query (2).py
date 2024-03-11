# -*- coding: utf-8 -*-
"""batch export >10000 van sparql query.ipynb

Altijd al meteen een csv of json willen hebben dat de query results >10000 heeft? hiermee kan dat:
"""

pip install SPARQLWrapper

from SPARQLWrapper import SPARQLWrapper, JSON, CSV
import pandas as pd
import csv
import time

endpoint_url = "https://api.linkeddata.cultureelerfgoed.nl/datasets/rce/cho/services/cho/sparql"

def sparql_to_df(query) :
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    # query uitvoeren en resultaten binden
    results = sparql.query().convert()
    bindings = results["results"]["bindings"]

    # van de bindingen een dataframe maken
    df = pd.json_normalize(bindings)
    return df

query_patrick = """

PREFIX owms: <http://standaarden.overheid.nl/owms/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX graph: <https://linkeddata.cultureelerfgoed.nl/graph/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX ceo: <https://linkeddata.cultureelerfgoed.nl/def/ceo#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?rijksmonumentnummer
    (REPLACE(STR(?CBSCodeGemeente), "^0+", "") AS ?CBSCodeGemeente)
    ?subcat ?bovencat1 ?bovencat2 ?bovencat3 ?successor
    (REPLACE(STR(?CBSCodeGemeente_s), "^0+", "") AS ?CBSCodeGemeente_s) WHERE {
  ?rijksmonument ceo:rijksmonumentnummer ?rijksmonumentnummer ; ceo:heeftBasisregistratieRelatie/ceo:heeftGemeente ?gemeente ; ceo:heeftOorspronkelijkeFunctie ?f_uri . ?f_uri ceo:heeftFunctieNaam ?f_urinaam ; ceo:hoofdfunctie "1"^^xsd:boolean .
 GRAPH graph:bebouwdeomgeving {
    ?f_urinaam skos:broader ?broader1 . ?f_urinaam skos:prefLabel ?subcat .?broader1 skos:prefLabel ?bovencat1 .
    OPTIONAL {?broader1 skos:broader ?broader2 . ?broader2 skos:prefLabel ?bovencat2 . }
    OPTIONAL {?broader2 skos:broader ?broader3 . ?broader3 skos:prefLabel ?bovencat3 .}
  }
  # Minus monumentaard archeologisch
  MINUS {?rijksmonument ceo:heeftMonumentAard <https://data.cultureelerfgoed.nl/term/id/rn/b673c8c1-5d93-496d-8f9e-89133d579d77> .
  }
 #  Minus status voorbeschermd
  MINUS {?rijksmonument ceo:heeftJuridischeStatus
        <https://data.cultureelerfgoed.nl/term/id/rn/2e93edd1-098f-4f31-ae7e-72cb77f4d2ca>} .
 #  Minus status geen rijksmonument
  MINUS {?rijksmonument ceo:heeftJuridischeStatus
        <https://data.cultureelerfgoed.nl/term/id/rn/3e79bb7c-b459-4998-a9ed-78d91d069227>} .
  GRAPH <https://triplydb.com/koop/owms/graphs/default> {
    ?gemeente rdf:type <http://standaarden.overheid.nl/owms/terms/Gemeente> ; <http://standaarden.overheid.nl/owms/terms/CBSCode> ?CBSCodeGemeente
             optional { ?gemeente <http://standaarden.overheid.nl/owms/terms/successor> ?successor . ?successor <http://standaarden.overheid.nl/owms/terms/CBSCode> ?CBSCodeGemeente_s
  }
}
}


"""

all_dfs = []
start = 0
einde = 60001
stap = 10000
for i in range(start, einde, stap):
    offset = i
    query_with_offset = query_patrick + f""" OFFSET {offset}
    LIMIT 10000"""
    df = sparql_to_df(query_with_offset)
    df = pd.DataFrame(df)
    print(query_with_offset)
    all_dfs.append(df)




final_df = pd.concat(all_dfs, ignore_index=True)

final_df
