#!/usr/bin/python
# -*- coding: utf-8 -*-


from time import sleep
import requests
import urllib.request
import os
import re
import json

net = __import__("010_net")


############################################################
# Settings

output_dir = "./download"
output_file = output_dir+"/_indicators.json"

sleep_sec = 20


############################################################
# Main
############################################################
url = "https://data.worldbank.org/indicator?tab=all"
htmltext = net.tuned_requests(url, sleep_sec)
print(url, htmltext)

if htmltext == None:
	print("Access Error! WorldBank Indocator: "+url)
else:
	if not os.path.exists(output_dir):
		os.mkdir(output_dir)

	indicator_name = {}
	res = re.findall(r'<a href="/indicator/([\w.]+)\?view=chart" data-reactid="(\d+)">([^<>]+)</a>', htmltext, re.IGNORECASE)
#	print(res)
	for r in res:
		indicator_name[r[0]] = r[2]

	# output
	fw = open(output_file, 'w', encoding='UTF-8')
	fw.write(json.dumps(indicator_name)+"\n")
	fw.close()

	i = 0
	for index in indicator_name.keys():
		i += 1
		if os.path.exists(output_dir+"/"+index+".zip"):
			print(i, end=' ')
			continue

		sleep(sleep_sec)
		print("\n", i, len(indicator_name)-i, index, end='')
		url = "https://api.worldbank.org/v2/en/indicator/"+index+"?downloadformat=csv"
		urllib.request.urlretrieve(url, output_dir+"/"+index+".zip")
