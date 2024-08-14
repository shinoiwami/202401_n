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
#input_file = "./output/_importances.json"
input_file = "./output/_importances.json.NY.GDP.MKTP.CD"
output_dir = "./output"

top = 20
target_country_codes = ["USA", "JPN", "DEU", "SAU", "GUY", "EST"]



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


###
# GOAL: output[destination_index][country][source_index]["importance"] = importance
#			destination_index: GDP-related
#			source_index: out of GDP
#			gap_year: GDP_year - source_index_year
#		other keys (st position of "importance")
#			"importance": the largest importance during gap_period
#			"r2": coefficient of determination
#			"cor": correlation coefficient
#			"x_year_0", "x_year_1": period of source
#			"y_year_0", "y_year_1": period of destination
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
			importances[dst][cc].setdefault(src, {"importance": 0})
			order[src] = importances[dst][cc][src]["importance"]

		i = 0
		output_path = output_dir+"/"+dst+"_"+cc+"_top"+str(top)+".tsv"
		outfile = open(output_path, 'w', encoding='utf-8')
		outfile.write("Rank\tImportance\tIndicator ID\tIndicator Name\tR2\tCOR\tX Period\tY Period\n")
		for k, v in sorted(order.items(), key=lambda i: i[1], reverse=True):
			i += 1
			if v != 0:
				text = str(i)+"\t"+str(round(v,4))+"\t"+k+"\t"+indicators[k]
				text += "\t"+str(round(importances[dst][cc][k]["r2"],4))
				text += "\t"+str(round(importances[dst][cc][k]["cor"],4))
				text += "\t"+str(importances[dst][cc][k]["x_year_0"])+" - "+str(importances[dst][cc][k]["x_year_1"])
				text += "\t"+str(importances[dst][cc][k]["y_year_0"])+" - "+str(importances[dst][cc][k]["y_year_1"])
				outfile.write(text+"\n")
			else:
				outfile.write(str(i)+"\t-\t-\t-\t-\t-\t-\t-\n")
			if i >= top:
				break
		outfile.close()
