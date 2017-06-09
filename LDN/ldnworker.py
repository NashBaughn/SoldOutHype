from threading import Thread
from time import sleep
import re
from requests_futures.sessions import FuturesSession
import requests
import re
import datetime 
from time import sleep
import numpy as num
import signal
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sellout_list = []
database = []
index = 12

def oneadd():
	while True:
		sleep(.5)
		if updated() == True:
			update_list()		
		
		start_time = datetime.datetime.now()
		
		page = requests.get('http://www.supremenewyork.com/shop/new')
		matches = re.findall('<article>(.*?)</article>', page.text)	
		
		for i, inner in enumerate(matches):
			if check_sold(inner) == True and sellout_list[i] == 'in stock':
				links_array = re.findall('<a href="(.*?)"', inner)
				url = "http://www.supremenewyork.com" + links_array[0]
				dif = datetime.datetime.now() - start_time
				data_tup = (url,str(dif))
				sellout_list[i] = data_tup

def update_list():
	num.savetxt('curr_list.txt', database, fmt="%s")
	index += 1
	new_database()

	global index
	page = requests.get('http://www.supremenewyork.com/shop/new')
	matches = re.findall('<article>(.*?)</article>', page.text)	
	print "updating list"
	sellout_list = ['in stock']*len(matches)
	global sellout_list


def updated():
	page = requests.get('http://www.supremenewyork.com/shop/new')
	updated_matches = re.findall('<article>(.*?)</article>', page.text)	
	
	if len(updated_matches) == len(sellout_list):
		return False
	return True

def check_sold(inner):
	matches = re.findall('<div class="sold_out_tag">(.*?)</div>', inner)
	if len(matches) == 1:
	
		return True
	return False


def twoadd():
	while True:
		sleep(1)
		
		for i, item in enumerate(database):
			elems = item.split(',')
		
			key = elems[1]
			
			for url in sellout_list:
				
				if url[0] == key and url[1] != 'in stock':
				
					database[i] = elems[0]+','+elems[1]+','+url[1]
		edit_times()
		num.savetxt('curr_list.txt', database, fmt="%s")

			
def new_database():

	page = requests.get('http://www.supremenewyork.com/shop/new')
	matches = re.findall('<article>(.*?)</article>', page.text)
	links_array = get_urls(matches)
	names_array = get_names(links_array)

	database = ['']*len(matches)
	for i, name in enumerate(names_array):
		database[i] = names_array[i]+","+links_array[i]+",in stock"

	global database

def get_names(url_array):
	name_array = [0]*len(url_array)
	for i, link in enumerate(url_array):
		page = requests.get(link)
		
		names = re.findall('<title>Supreme: (.*?)</title>', page.text)
		print names[0]
		name_array[i] = names[0]
	return name_array

def get_urls(matches):
	links = [0]*len(matches)
	for i, match in enumerate(matches):
		links_array = re.findall('<a href="(.*?)"', match)
		links[i] = "http://www.supremenewyork.com" + links_array[0]
	return links	

def edit_times():
	for i, line in enumerate(database):
		elems = line.split(',')
		if elems[2] != 'in stock' and elems[2] != 'sold out':
			elems[2] = elems[2][:-4]
		database[i] = elems[0]+','+elems[1]+','+elems[2]

quick_worker = Thread(target=oneadd, args=())
quick_worker.setDaemon(True)
quick_worker.start()

dict_worker = Thread(target=twoadd, args=())
dict_worker.setDaemon(True)
dict_worker.start()	



	


	


