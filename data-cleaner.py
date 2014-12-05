import elasticsearch
import csv
import glob
from dateutil.parser import parse

from datetime import datetime

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
    "Begin Date Collected": "collectionDate",

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

write_header = sorted(set(mapping.values()))

count = 0
parse_failures_count = 0
for fn in glob.iglob("*.csv"):
    with open(fn,"rb") as inf:
        with open(fn+".cleaned","wb") as outf:
            cr = csv.reader(inf, dialect=csv.excel)
            cw = csv.writer(outf)
            header = cr.next()

            cw.writerow(write_header)

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

                for k in ["transcribe_date","validate_date","collectionDate"]:
                    if k in mapped:
                        try: 
                          mapped[k] = parse(mapped[k])
                        except:
                          parse_failures_count += 1
                          mapped[k] = ""
                          #print "parser failure", mapped[k]

                if "country" in mapped:
                    if mapped["country"] in country_remap:
                        mapped["country"] = country_remap[mapped["country"]]

                mapped["datafile"] = fn

                output = []
                for f in write_header:
                    if f in mapped:
                        output.append(mapped[f])
                    else:
                        output.append("") 
                cw.writerow(output)   

    print fn, count, parse_failures_count
