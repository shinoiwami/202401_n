#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import re
import json

import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster


countries_file = "./download/_countries.json"
indicators_file = "./download/_indicators.json"
input_file = "./output/_importances.json"
output_dir = "./output"

top = 20
target_country_codes = ["USA", "JPN", "DEU", "IND", "SAU", "THA", "PRY", "HUN", "NZL", "SGP", "GUY", "EST"]



############################################################
# Main
############################################################

countries = {}
indicators = {}
importances = {}
with open(countries_file, 'rb') as infile:
	countries = json.load(infile)
with open(indicators_file, 'rb') as infile:
	indicators = json.load(infile)
with open(input_file, 'rb') as infile:
	importances = json.load(infile)
#	print(importances)


# Data Format:
#		importances[destination_index][country][source_index]["year"] = gap_year
#		importances[destination_index][country][source_index]["importance"] = importance
#		 	destination_index: GDP-related
#			source_index: out of GDP
#			gap_year: GDP_year - source_index_year
###

for dst in importances.keys():
	cc_list = []
	src_list = []
	for cc in importances[dst].keys():
		if cc in target_country_codes:
			cc_list.append(cc)
		for src in importances[dst][cc].keys():
			src_list.append(src)
	cc_list = list(set(cc_list))
	src_list = list(set(src_list))

	top_indeces = []
	for cc in cc_list:
		importances[dst].setdefault(cc, {})
		order = {}
		year = {}
		for src in src_list:
			importances[dst][cc].setdefault(src, {"year": 0, "importance": 0})
			order[src] = importances[dst][cc][src]["importance"]
			year[src] = importances[dst][cc][src]["year"]

		i = 0
		output_path = output_dir+"/"+dst+"_"+cc+"_top"+str(top)+".tsv"
		outfile = open(output_path, 'w', encoding='utf-8')
		for k, v in sorted(order.items(), key=lambda i: i[1], reverse=True):
			i += 1
			if v != 0:
				outfile.write(str(i)+"\t"+str(v)+"\t"+k+"\t"+indicators[k]+"\t"+str(year[k])+"\n")
			else:
				outfile.write(str(i)+"\t-\t-\t-\t-\n")
			if i >= top:
				break
		outfile.close()
