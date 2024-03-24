#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
from time import sleep
import os
import sys
import random
import requests


def tuned_requests(url, sleep_sec=2, proxies=None, headers=None):

	err = 1
	get_url_info = requests.get(url, proxies=proxies, headers=headers)
	while True:
		sleep(sleep_sec)
		try:
			get_url_info = requests.get(url)
			if get_url_info.status_code == 200:
				return get_url_info.text
			else:
				if sleep_sec < 60:
					sleep_sec = 60
				delay = sleep_sec*(2**(err-1))
				print(datetime.now(), str(delay)+" sec waiting... (err: "+str(err)+")")
				sleep(delay)
				if delay > 1800:	# 30 min (cumulatively about 1 hr)
					return
				err += 1

		except Exception as e:
			print(e)
			return

