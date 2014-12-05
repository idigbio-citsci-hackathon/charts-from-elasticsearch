import requests
import json
import csv

datafiles = [
    "2014-11-30_notes_from_nature_calbug_classifications.csv",
    "2014-11-30_notes_from_nature_herbarium_classifications.csv",
    "2014-11-30_notes_from_nature_macrofungi_classifications.csv",
    "2014-11-30_notes_from_nature_ornithological_classifications.csv",    
]

fields = [
    "transcribe_date",
    "country",
    "datafile",
    "collectionDate"
]

header_fields = [
    "datafile",
    "transcribe_date",
    "country",
    "country_fixed",
    "user",
    "collectionDate"
]

s = requests.Session()

cr = s.get("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json").json()

countries = {}
for c in cr["features"]:
    countries[c["properties"]["name"]] = c

country_remap = {
    "United States": "United States of America",
    "USA": "United States of America",
    "United State of America": "United States of America",
    "usa": "United States of America",
    "U.S.A.": "United States of America",
    "U.S.": "United States of America",
    "US": "United States of America",
    "Usa": "United States of America",
    "united states": "United States of America",
    "Unitred States": "United States of America",
    "Usa": "United States of America",
    "unknown": "",
    "placeholder": "",
    "Phillipines": "Philippines",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Bahamas": "The Bahamas",
    "Uraguay": "Uruguay",
    "Afganistan": "Afghanistan",
    "United Arab Erimates": "United Arab Emirates",
    "Great Britain": "United Kingdom",
    "Korea Sout": "South Korea",
    "Korea South": "South Korea",
    "mexico": "Mexico",
    "MEXICO": "Mexico",
    "MEX": "Mexico",
    "Korean North": "North Korea",
    "Cote D'Ivoire": "Ivory Coast",
}

datafile_remap = {
    "2014-11-30_notes_from_nature_calbug_classifications.csv": "calbug",
    "2014-11-30_notes_from_nature_herbarium_classifications.csv": "herbarium",
    "2014-11-30_notes_from_nature_macrofungi_classifications.csv": "macrofungi",
    "2014-11-30_notes_from_nature_ornithological_classifications.csv": "ornithological",
}

for u in datafiles:
    q = {
      "query": {
        "bool": {
          "must": [
            {
              "term": {
                "transcriptions.datafile": u
              }
            }
          ],
          "must_not": [],
          "should": []
        }
      },
      "size": 1000000
    }
    r = s.post("http://search.idigbio.org/hackathon/transcriptions/_search",data=json.dumps(q))
    r.raise_for_status()
    o = r.json()

    with open("datafile_" + u + ".csv", "wb") as outf:
        cw = csv.writer(outf)
        cw.writerow(header_fields)
        for hit in o["hits"]["hits"]: 
            ha = [datafile_remap[u]]
            for f in fields:
                if f in hit["_source"]:
                    fv = hit["_source"][f]
                    if f == "country":
                        ha.append(fv)
                        if fv in country_remap:
                            fv = country_remap[fv]
                        
                        if fv != "" and fv not in countries:
                            print "|" + fv + "|"

                    ha.append(fv)

                else:
                    ha.append("")
            cw.writerow(ha)