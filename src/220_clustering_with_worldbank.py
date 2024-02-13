#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import re
import json

import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster


input_file = "./output/_importances.json"
input_file2 = "./download/_indicators.json"
input_file3 = "./download/_countries.json"
output_dir = "./output"

removed_country_codes = ["AFE", "AFW", "ARB", "CEB", "CSS", "EAP", "EAR", "EAS", "ECA", "ECS", "EMU", "EUU", "FCS", "HIC", "HPC", "IBD", "IBT", "IDA", "IDB", "IDX", "LAC", "LCN", "LDC", "LIC", "LMC", "LMY", "LTE", "MEA", "MIC", "MNA", "NAC", "OED", "OSS", "PRE", "PSS", "PST", "SAS", "SSA", "SSF", "SST", "TEA", "TEC", "TLA", "TMN", "TSA", "TSS", "UMC", "WLD"]



############################################################
# Main
############################################################

importances = {}
with open(input_file, 'rb') as infile:
	importances = json.load(infile)
#	print(importances)
indicators = {}
with open(input_file2, 'rb') as infile2:
	indicators = json.load(infile2)
countries = {}
with open(input_file3, 'rb') as infile3:
	countries = json.load(infile3)


# Data Format:
#		importances[destination_index][country][source_index]["year"] = gap_year
#		importances[destination_index][country][source_index]["importance"] = importance
#		 	destination_index: GDP-related
#			source_index: out of GDP
#			gap_year: GDP_year - source_index_year
###

for dst in importances.keys():
	cc_list = []
	cc_list2 = []
	src_list = []
	src_list2 = []
	for cc in importances[dst].keys():
		if cc in removed_country_codes:
			continue
		cc_list.append(cc)
		for src in importances[dst][cc].keys():
			src_list.append(src)
	cc_list = list(set(cc_list))
	src_list = list(set(src_list))
	for cc in cc_list:
		cc_list2.append(countries[cc])
	for src in src_list:
		src_list2.append(indicators[src])

	matrix = []
	for cc in cc_list:
		importances[dst].setdefault(cc, {})
		row = []
		for src in src_list:
			importances[dst][cc].setdefault(src, {"importance": 0})
			row.append(importances[dst][cc][src]["importance"])
		matrix.append(row)
	df = pd.DataFrame(matrix, index=[cc_list2, cc_list], columns=[src_list, src_list2])
	df.to_csv(output_dir+"/"+dst+".csv", encoding="utf_8")

	### ref. https://analysis-navi.com/?p=1884
	linkage_result = linkage(df, method='ward', metric='euclidean')
	plt.figure(num=None, figsize=(18, 6), dpi=200, facecolor='w', edgecolor='k')
	plt.subplots_adjust(left=0.03, right=0.99, top=0.98, bottom=0.27)
	dendrogram(linkage_result, labels=df.index)
#	plt.show()
	plt.savefig(output_dir+"/"+dst+".png")
