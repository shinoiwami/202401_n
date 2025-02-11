#!/usr/bin/python
# -*- coding: utf-8 -*-


import os
import re
import sys
import time
import json
import zipfile

import pandas as pd
import numpy as np
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import LabelEncoder


############################################################
# Settings

input_dir = "./download"
input_file = input_dir+"/_indicators.json"
mid_file = input_dir+"/_countries.json"

output_dir = "./output"
output_file = output_dir+"/_importances.json"

tmp_dir = "./tmp"

gdp_index = ["NY.GDP.MKTP.CD"]	# GDP
#gdp_index = ["NY.GDP.MKTP.CD", "NY.GDP.PCAP.CD"]	# GDP, GDP per capita
#gdp_index = ["NY.GDP.MKTP.KD.ZG"]	# GDP growth

removed_factor_index = ["NY.GDP.MKTP.KD", "NY.GDP.MKTP.KN", "NY.GDP.MKTP.CN", "NY.GDP.MKTP.CD", "NY.GDP.DEFL.ZS", "NY.GDP.MKTP.KD.ZG", "NY.GDP.PCAP.KD", "NY.GDP.PCAP.KN", "NY.GDP.PCAP.CN", "NY.GDP.PCAP.CD", "NY.GDP.PCAP.KD.ZG", "NY.GDP.PCAP.PP.KD", "NY.GDP.PCAP.PP.CD", "NY.GDP.MKTP.PP.KD", "NY.GDP.MKTP.PP.CD", "NY.GNP.MKTP.CN.AD"]	# GDP-related

# When the limited factors are computed, set the test_index list.
# When the test_index list is empty, all factors excluding gdp_index and removed_factor_index are used.
test_index = []		# DEFAULT
#test_index = ["SL.TLF.TOTL.FE.ZS", "SL.TLF.TOTL.IN", "SL.TLF.ADVN.ZS"]	# Labor force, female (% of total labor force); Labor force, total; Labor force with advanced education (% of total working-age population with advanced education)

year_min = 1960
year_max = 2023

gap_period = 20


############################################################
# Main
############################################################

indicator_name = {}
with open(input_file, 'rb') as infile:
	indicator_name = json.load(infile)
#	print(indicator_name)
factor_index = list(indicator_name.keys())
#print(factor_index)
for rfi in removed_factor_index:
	factor_index.remove(rfi)
if len(test_index) > 0:
	factor_index = test_index

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

output = {}
country_index = []
country_name = {}
country_num = {}

incompatible_src = []

if not os.path.exists(input_dir):
	print("Execute this Program after the Previous Step.")
	sys.exit
if not os.path.exists(output_dir):
	os.mkdir(output_dir)
if not os.path.exists(tmp_dir):
	os.mkdir(tmp_dir)

for dst in gdp_index:
	output.setdefault(dst, {})
	with zipfile.ZipFile(input_dir+"/"+dst+".zip") as zf:
		zipnames = zf.namelist()
		pattern = '^API_'+dst+'.*\.csv'

		flag = 0
		for zipname in zipnames:
			if re.match(pattern, zipname):
				flag = 1
				if not os.path.exists(tmp_dir+"/"+zipname):
					zf.extract(zipname, tmp_dir+"/")
				data_dst = pd.read_csv(tmp_dir+"/"+zipname, skiprows=3)
#				print(data_dst)
#				print(zipname, data_dst.shape)

				#####
				# To Collect Country Info. (It works once) 
				if country_index == []:
					for i in range(data_dst.shape[0]):
						cc = data_dst["Country Code"][i]
						country_index.append(cc)
						country_name[cc] = data_dst["Country Name"][i]
						country_num[cc] = i

					# output
					fw = open(mid_file, 'w', encoding='UTF-8')
					fw.write(json.dumps(country_name)+"\n")
					fw.close()
				#####

				break

		if flag == 0:
			break

		for cc in country_index:
			output[dst].setdefault(cc, {})

		for src in factor_index:
			print(src, dst)
			with zipfile.ZipFile(input_dir+"/"+src+".zip") as zf:
				zipnames = zf.namelist()
				pattern = '^API_'+src+'.*\.csv'
				for zipname in zipnames:
					if re.match(pattern, zipname):
						if not os.path.exists(tmp_dir+"/"+zipname):
							zf.extract(zipname, tmp_dir+"/")
						data_src = pd.read_csv(tmp_dir+"/"+zipname, skiprows=3)
#						print(data_src)
#						print(zipname, data_src.shape)

						if str(year_min) not in data_src:
							incompatible_src.append(src)
							break

						for cc in country_index:
							X = []
							y = []
							print("=====")

							# check period
							flag = 0
							year0_src = year_min
							year1_src = year_max
							for yr in reversed(range(year_min, year_max+1)):
								if flag == 0 and not pd.isnull(data_src[str(yr)][country_num[cc]]):
									year1_src = yr
									flag = 1
								elif flag == 1 and pd.isnull(data_src[str(yr)][country_num[cc]]):
									year0_src = yr+1
									flag = 2
									break
							print(src, "["+cc+"]", dst, "src", year1_src, year0_src, year1_src-year0_src, gap_period+1)
							if flag == 0 or year1_src-year0_src <= gap_period+1:
								print("Skip.")
								continue

							flag = 0
							year0_dst = year_min
							year1_dst = year_max
							for yr in reversed(range(year_min, year_max+1)):
								if flag == 0 and not pd.isnull(data_dst[str(yr)][country_num[cc]]):
									year1_dst = yr
									flag = 1
								elif flag == 1 and pd.isnull(data_dst[str(yr)][country_num[cc]]):
									year0_dst = yr+1
									flag = 2
									break
							print(src, "["+cc+"]", dst, "dst", year1_dst, year0_dst)
							if flag == 0 or year1_dst-year0_dst <= gap_period+1:
								print("Skip.")
								continue

							for gap in range(0, year1_src-gap_period-year0_src+1):
								x_one = []
#								print("X", gap, year0_src+1+gap, year0_src+gap_period+gap+1)
								for yr in range(year0_src+1+gap, year0_src+gap_period+gap+1):
#									print(gap, yr, data_src[str(yr)][country_num[cc]])
									x_one.append(data_src[str(yr)][country_num[cc]])
#								print(len(x_one))
								X.append(x_one)

#							print("y", year1_dst+1-gap_period, year1_dst+1)
							for yr in range(year1_dst+1-gap_period, year1_dst+1):
#								print(yr, data_dst[str(yr)][country_num[cc]])
								y.append(data_dst[str(yr)][country_num[cc]])

#							print(cc, "X-y", len(X), len(y))
#							print(X, y)
							Xnp = np.array(np.transpose(X), dtype='int64')
							ynp = np.array(y, dtype='int64')
							clf = ExtraTreesClassifier(n_estimators=100, random_state=0)

							try:
								clf.fit(Xnp, ynp)
								r2 = clf.score(Xnp, ynp)
								importances = clf.feature_importances_
								corr = np.corrcoef(y, X)
#								print("Success:", importances, r2, corr)
#								print("Success:", importances)

								i = 0
								importance_val = 0
								importance_gap = 0
								for im in importances:
									if importance_val < im:
										importance_val = im
										importance_gap = i
									i += 1

								output[dst][cc].setdefault(src, {})
								output[dst][cc][src]["importance"] = importance_val
								output[dst][cc][src]["r2"] = r2
								if str(corr[0][importance_gap+1]) != 'nan':
									output[dst][cc][src]["cor"] = corr[0][importance_gap+1]
								else:
									output[dst][cc][src]["cor"] = 10		# When it follows runtime error, x-values are not null, but always 0. As a result, it is OK to skip.
								output[dst][cc][src]["x_year_0"] = year0_src+1+importance_gap
								output[dst][cc][src]["x_year_1"] = year0_src+gap_period+importance_gap
								output[dst][cc][src]["y_year_0"] = year1_dst+1-gap_period
								output[dst][cc][src]["y_year_1"] = year1_dst
								print("Identified Values:", dst, "["+cc+"]", src, importance_gap, importance_val, r2, output[dst][cc][src]["cor"])

								# sleep to reduce CPU burden slightly (Please tune depending on your computer.)
#								time.sleep(0.1)

							except ValueError as e:
#								print("type:{0}".format(type(e)))
#								print("args:{0}".format(e.args))
#								print("message:{0}".format(e.message))
								print("Failed:", "{0}".format(e))
								continue

						break

 
	###
	# output
	fw = open(output_file, 'w', encoding='UTF-8')
	fw.write(json.dumps(output)+"\n")
	fw.close()

	fw = open(output_file+"."+dst, 'w', encoding='UTF-8')
	fw.write(json.dumps(output)+"\n")
	fw.close()

print("incompatible_src:", set(incompatible_src))


"""
GDP-related
https://data.worldbank.org/indicator/NY.GDP.MKTP.KD?view=chart
https://data.worldbank.org/indicator/NY.GDP.MKTP.KN?view=chart
https://data.worldbank.org/indicator/NY.GDP.MKTP.CN?view=chart
https://data.worldbank.org/indicator/NY.GDP.MKTP.CD?view=chart
https://data.worldbank.org/indicator/NY.GDP.DEFL.ZS?view=chart
https://data.worldbank.org/indicator/NY.GDP.MKTP.KD.ZG?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.KD?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.KN?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.CN?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.CD?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.KD.ZG?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.KD?view=chart
https://data.worldbank.org/indicator/NY.GDP.PCAP.PP.CD?view=chart
https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.KD?view=chart
https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD?view=chart
https://data.worldbank.org/indicator/NY.GNP.MKTP.CN.AD?view=chart
"""

