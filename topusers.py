import requests
import json
import csv

users = [
    "Bill K.",
    "annedonnelly",
    "LLITLL",
    "Ma29ryAnn",
    "robgur"
]

fields = [
    "transcribe_date",
    "country",
    "datafile",
    "collectionDate"
]

header_fields = [
    "user",
    "transcribe_date",
    "country",
    "country_fixed",
    "datafile",
    "collectionDate"
]

s = requests.Session()

cr = requests.get("https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json").json()

countries = {}
for c in cr["features"]:
    countries[c["properties"]["name"]] = c

country_remap = {
    "United States": "United States of America",
    "unknown": "",
    "placeholder": "",
    "Phillipines": "Philippines",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Bahamas": "The Bahamas"
}

datafile_remap = {
    "2014-11-30_notes_from_nature_calbug_classifications.csv": "calbug",
    "2014-11-30_notes_from_nature_herbarium_classifications.csv": "herbarium",
    "2014-11-30_notes_from_nature_macrofungi_classifications.csv": "macrofungi",
    "2014-11-30_notes_from_nature_ornithological_classifications.csv": "ornithological",
}

for u in users:
    q = {
      "query": {
        "bool": {
          "must": [
            {
              "term": {
                "transcriptions.transcribe_user": u
              }
            }
          ],
          "must_not": [],
          "should": []
        }
      },
      "size": 100000
    }
    r = s.post("http://search.idigbio.org/hackathon/transcriptions/_search",data=json.dumps(q))
    r.raise_for_status()
    o = r.json()

    with open("user_" + u + ".csv", "wb") as outf:
        cw = csv.writer(outf)
        cw.writerow(header_fields)
        for hit in o["hits"]["hits"]: 
            ha = [u]
            for f in fields:
                if f in hit["_source"]:
                    fv = hit["_source"][f]
                    if f == "country":
                        ha.append(fv)
                        if fv in country_remap:
                            fv = country_remap[fv]
                        
                        if fv != "" and fv not in countries:
                            print fv
                    elif f == "datafile":
                        fv = datafile_remap[fv]

                    ha.append(fv)

                else:
                    ha.append("")
            cw.writerow(ha)