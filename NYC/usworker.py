from threading import Thread
from time import sleep
import re
import os
import datetime 
import numpy as num
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

sellout_list = [] #array that fast array works with, pretty much function likes times_custom.py

database = [] #array that slow thread works with, it is what is saved, all nice in fomratted

index = 12 #index is for fomratting saved files

up = False #up is sorta like an event that the fast thread can send to the slow one

def fast_thread():
	
	while True:	
		sleep(.5)
		print("fast")
		
		if updated() == True:
			update_list()		
		
		start_time = datetime.datetime.now()
		
		page = os.popen("curl http://www.supremenewyork.com/shop/new").read()
		matches = re.findall('<article>(.*?)</article>', page)	
		
		for i, inner in enumerate(matches):
			if check_sold(inner) == True and sellout_list[i] == 'in stock':
				links_array = re.findall('<a href="(.*?)"', inner)
				url = "http://www.supremenewyork.com" + links_array[0]
				dif = datetime.datetime.now() - start_time
				data_tup = (url,str(dif))
				sellout_list[i] = data_tup

def update_list():
	num.savetxt('us'+index+'.txt', database, fmt="%s")
	
	up = True
	global up
	
	index += 1
	global index
	
	page = os.popen("curl http://www.supremenewyork.com/shop/new").read()
	matches = re.findall('<article>(.*?)</article>', page)
	
	print "updating list"
	sellout_list = ['in stock']*len(matches)
	global sellout_list

def updated():
	page = os.popen("curl http://www.supremenewyork.com/shop/new").read()
	updated_matches = re.findall('<article>(.*?)</article>', page)		
	if len(updated_matches) == len(sellout_list):
		return False
	return True

def check_sold(inner):
	matches = re.findall('<div class="sold_out_tag">(.*?)</div>', inner)
	if len(matches) == 1:
		return True
	return False

def slow_thread():
	while True:
		sleep(1)
		
		if up == True:	
			new_database()
		for i, item in enumerate(database):
			elems = item.split(',')
			key = elems[1]
			for url in sellout_list:				
				if url[0] == key and url[1] != 'in stock':				
					database[i] = elems[0]+','+elems[1]+','+url[1]
		edit_times()
		num.savetxt('currnyc.txt', database, fmt="%s")

			
def new_database():
	page = os.popen("curl http://www.supremenewyork.com/shop/new").read()
	matches = re.findall('<article>(.*?)</article>', page)
	
	links_array = get_urls(matches)
	names_array = get_names(links_array)

	database = ['']*len(matches)
	for i, name in enumerate(names_array):
		database[i] = names_array[i]+","+links_array[i]+",in stock"
	up = False
	global up
	global database

def get_names(url_array):
	name_array = [0]*len(url_array)
	for i, link in enumerate(url_array):
		
		page = os.popen("curl "+link).read()
		
		names = re.findall('<title>Supreme: (.*?)</title>', page)
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

quick_worker = Thread(target=fast_thread, args=())
quick_worker.setDaemon(True)
quick_worker.start()

dict_worker = Thread(target=slow_thread, args=())
dict_worker.setDaemon(True)
dict_worker.start()	

while True:
	continue