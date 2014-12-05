import csv
from dateutil.parser import parse
from collections import defaultdict

with open("icoast_in.csv","rb") as inf:
	cr = csv.reader(inf)

	header = cr.next()

	daycounts = defaultdict(int)

	usercounts = defaultdict(lambda: defaultdict(int))

	for l in cr:
		d = dict(zip(header,l))

		dt = parse(d["Completion Time"])
		daycounts["{0}-{1}-{2}".format(dt.year,dt.month,dt.day)] += 1
		usercounts["{0}-{1}-{2}".format(dt.year,dt.month,dt.day)][d["User ID"]] += 1

	users = set(["716","736","882","730","712"])

	# for k in usercounts:
	# 	users.update(usercounts[k].keys())

	with open("icoast.csv","wb") as outf:
		cw = csv.writer(outf)

		cw.writerow(["date","count"] + list(users))

		for k in daycounts:
			outrow = [k,daycounts[k]]
			for u in users:
				if u in usercounts[k]:
					outrow.append(usercounts[k][u])
				else:
					outrow.append(0) 
			cw.writerow(outrow)