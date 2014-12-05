import elasticsearch
import csv
import glob
from dateutil.parser import parse

from datetime import datetime

es = elasticsearch.Elasticsearch(["c18node2.acis.ufl.edu"])

mapping = {
    "taskID": "id",
    "id": "id",
    "edan_id": "id",

    "subject_id": "image_id",
    "externalIdentifier": "image_id",

    "filename": "filename",

    "transcriberID": "transcribe_user",
    "user_name": "transcribe_user",
    
    "dateTranscribed": "transcribe_date",
    "finished_at": "transcribe_date",

    "validatorID": "validate_user",
    "dateValidated": "validate_date",

    "scientificName": "scientificName",
    "Scientific name": "scientificName",

    "BioEventSiteRef*ColDateVisitedFrom": "collectionDate",
    "Collection date": "collectionDate",
    "eventDate": "collectionDate",

    "Country": "country",
    "country": "country",
    "BioEventSiteRef*LocCountry": "country",

    "State": "stateProvince",
    "BioEventSiteRef*LocProvinceStateTerritory": "stateProvince",
    "stateProvince": "stateProvince",

    "decimalLatitude": "latitude",
    "BioEventSiteRef*LatLatitude_nesttab": "latitude",

    "decimalLongitude": "longitude",
    "BioEventSiteRef*LatLongitude_nesttab": "longitude",
}

es_mapping = {
    "transcriptions": {
       "date_detection": False,
       "properties": {
           "country": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "stateProvince": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "latitude": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "longitude": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "collectionDate": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "scientificName": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "id": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "image_id": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "filename": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "transcribe_user": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "validate_user": {
               "type": "string",
               "index" : "not_analyzed"
           },
           "transcribe_date": {
               "type": "date"
           },
           "validate_date": {
               "type": "date"
           },
           "datafile": {
               "type": "string",
               "index" : "not_analyzed"
           },
        }
    }
}

es.indices.put_mapping(index="hackathon",doc_type="transcriptions",body=es_mapping)

count = 0
for fn in glob.iglob("*.csv"):
    with open(fn,"rb") as inf:
        cr = csv.reader(inf, dialect=csv.excel)
        header = cr.next()

        for l in cr:
            count += 1
            d = dict(zip(header,l))

            if "started_at" in d and "finished_at" in d:
                d1 = parse(d["started_at"])
                d2 = parse(d["finished_at"])

                d["duration"] = (d2 - d1).total_seconds()


            mapped = {}
            for f in d:
                if f in mapping:
                    mapped[mapping[f]] = d[f] 

            for k in ["transcribe_date","validate_date"]:
                if k in mapped:
                    mapped[k] = parse(mapped[k])

            mapped["raw"] = d
            mapped["datafile"] = fn
    
            es.index(index="hackathon", doc_type="transcriptions",id=mapped["id"], body=mapped)

    print fn, count
