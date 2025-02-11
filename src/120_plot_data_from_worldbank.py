#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import re
import json
import zipfile

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

input_dir = "./download"
indicators_file = input_dir+"/_indicators.json"
output_dir = "./output"
tmp_dir = "./tmp"

x_indices = ["NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD"]
y_indices = ["NY.GDP.MKTP.KD.ZG"]

target_year = 2023
drop_cc = ["AFE", "AFW", "ARB", "CEB", "CSS", "EAP", "EAR", "EAS", "ECA", "ECS", "EMU", "EUU", "FCS", "HIC", "HPC", "IBD", "IBT", "IDA", "IDB", "IDX", "LAC", "LCN", "LDC", "LIC", "LMC", "LMY", "LTE", "MEA", "MIC", "MNA", "NAC", "OED", "OSS", "PRE", "PSS", "PST", "SAS", "SSA", "SSF", "SST", "TEA", "TEC", "TLA", "TMN", "TSA", "TSS", "UMC", "WLD"]
# outliner
drop_cc.extend(["USA", "CHN", "GUY", "MAC", "TLS", "SDN"])


############################################################
# Main
############################################################

with open(indicators_file, 'rb') as infile:
	indicators = json.load(infile)

for x_index in x_indices:
	filename = ""
	pattern = '^API_'+x_index+'.*\.csv'

	# extract file from zip
	with zipfile.ZipFile(input_dir+"/"+x_index+".zip") as zf:
		zipnames = zf.namelist()

		for zipname in zipnames:
			if re.match(pattern, zipname):
				if not os.path.exists(tmp_dir+"/"+zipname):
					zf.extract(zipname, tmp_dir+"/")
    
	for csvname in os.listdir(tmp_dir):
		if re.match(pattern, csvname):
			filename = csvname
			break
	x_load = pd.read_csv(tmp_dir+"/"+filename, skiprows=3, index_col=['Country Code'])
	x_load = x_load.drop(index=drop_cc)

	for y_index in y_indices:
		filename = ""
		pattern = '^API_'+y_index+'.*\.csv'

		# extract file from zip
		with zipfile.ZipFile(input_dir+"/"+y_index+".zip") as zf:
			zipnames = zf.namelist()

			for zipname in zipnames:
				if re.match(pattern, zipname):
					if not os.path.exists(tmp_dir+"/"+zipname):
						zf.extract(zipname, tmp_dir+"/")

		for csvname in os.listdir(tmp_dir):
			if re.match(pattern, csvname):
				filename = csvname
				break
		y_load = pd.read_csv(tmp_dir+"/"+filename, skiprows=3, index_col=['Country Code'])
		y_load = y_load.drop(index=drop_cc)

#		x_load[str(target_year)], y_load[str(target_year)], y_load["Country Name"]
		x = np.array(x_load[str(target_year)])
		y = np.array(y_load[str(target_year)])
		y_load.reset_index(inplace=True)
		labels = y_load["Country Name"]

		plt.figure(figsize=(9, 6), dpi=200)		
		plt.scatter(x, y)
#		plt.title("title")
		plt.xlabel(indicators[x_index])
		plt.ylabel(indicators[y_index])
		for i, label in enumerate(labels):
		    plt.text(x[i], y[i], label)
		plt.subplots_adjust(left=0.06, right=0.98, bottom=0.08, top=0.98)
#		plt.show()
		plt.savefig(output_dir+"/_dist_"+x_index+"_"+y_index+".png")
