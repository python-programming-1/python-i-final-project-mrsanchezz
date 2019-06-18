#! python3
#
#

import requests
import calendar
import re
import time
import datetime
import json
import csv
import sys
from json2html import *
from bs4 import BeautifulSoup
from googlesearch import search
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

month_list = calendar.month_name[1:]
today = datetime.datetime.now()
wait = 0.5


def BestMonths(city, country):
	"""Google search best months to travel to city, country"""

	print('\nSearching for best months to travel to %s, %s...\t' % (city, country), end='')
	# concatenate search string
	query = 'travel us news best time to visit ' + str(city) + ' ' + str(country)

	# search and return Travel US News web url
	web_url = [x for x in search(query, tld='com', lang='en', num=1, stop=1)][0]

	# Access webpage and grab html source
	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
	res = requests.get(web_url, headers=headers)
	res.raise_for_status()
	html_source = BeautifulSoup(res.text, 'html.parser')

	# Parse out best months to travel
	element = html_source.select('.best-season-row')  	# Find all elements that uses class attrib best-seasons-row
	best_season = []
	for i in range(len(element)):
		best_season.append(element[i].strong.string)   	# Make list of best months for each season

	month_search = re.compile(r'(\w+)-(\w+)')

	# Form dictionary of month range for each best season
	best_season_months = {}
	for i in range(len(best_season)):
		best_season_months.setdefault(i, {})
		month_range = month_search.search(best_season[i])
		for j in range(2):
			best_season_months[i].setdefault(month_range.groups()[j],{})

	# Collect all months within range for best season
	month_idx_range = []
	for key, value in best_season_months.items():
		for i in value.keys():
			for idx, month in enumerate(month_list):
				if i == month:
					month_idx_range.append(idx)
		if len(range(month_idx_range[0],month_idx_range[-1])) >= 2:
			month_idx  = range(month_idx_range[0],month_idx_range[-1])
			for j in range(len(month_idx)):
				value.setdefault(month_list[month_idx[j]],{})		
			month_idx_range = []
		else:
			month_idx_range = []

	print('Complete!\n')
	return best_season_months


def weather(city, country, best_months_dict):
	""""Webscrape weather channel website for avg hi and low for destination"""

	print('Collecting avg hi and low temperatures for best months to travel to %s, %s...\t' % (city, country), end='')
	# conatenate search string
	query = 'weather.com alamanac ' + str(city) + ' ' + str(country)

	# search and return weather web url
	web_url = [x for x in search(query, tld='com', lang='en', num=1, stop=1)][0]

	# Access webpage and grab html source
	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
	res = requests.get(web_url, headers=headers)
	res.raise_for_status()
	html_source = BeautifulSoup(res.text, 'html.parser')

	# parse out avg hi and lo for each month of the year
	avg_hilo_search = re.compile(r'"avg_hi":(\d*.\d),"avg_lo":(\d*.\d)')
	avg_hilo_list = avg_hilo_search.findall(html_source.text)[:12]

	# error handlings
	if len(avg_hilo_list) < 12:
		print('ERROR!\n\t--no data found for %s, %s. Try another destination. Sorry =[' % (city, country))
		sys.exit()

	# Form dictionary of avg hi/lo to months for best seasons
	for key, value in best_months_dict.items():
		for i in value.keys():
			for idx, month in enumerate(month_list):
				if i == month:
					best_months_dict[key][i].setdefault('avg_hi', avg_hilo_list[idx][0])
					best_months_dict[key][i].setdefault('avg_lo', avg_hilo_list[idx][1])

	print('Complete!\n')
	return best_months_dict


def flights(city, country, home_airport, num_of_days, best_months_dict):
	""""Open google flights website and search round trip flights for months with available flight prices"""

	print('Opening google flights for best months with available flight prices to %s, %s...\t' % (city, country), end='')
	# Form dictionary of departaure and return dates
	for key in best_months_dict.keys():
		for val in best_months_dict[key].keys():
			for idx,month in enumerate(month_list):
				if val == month:
					if today.month - idx-1 <= 0:
						depart_date = datetime.date(today.year,idx+1,1)
						duration = datetime.timedelta(days=num_of_days)
						return_date = depart_date + duration
						best_months_dict[key][val].setdefault('Depart', str(depart_date))
						best_months_dict[key][val].setdefault('Return', str(return_date))
					elif today.month - idx-1 >= 2:
						depart_date = datetime.date(today.year+1,idx+1,1)
						duration = datetime.timedelta(days=num_of_days)
						return_date = depart_date + duration
						best_months_dict[key][val].setdefault('Depart', str(depart_date))
						best_months_dict[key][val].setdefault('Return', str(return_date))
					else:
						best_months_dict[key][val].setdefault('Depart', str('Flight prices not avail'))
						best_months_dict[key][val].setdefault('Return', str('Flight prices not avail'))

	# Set up webdriver for google chrome
	web_url = 'https://www.google.com/flights'
	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--incognito')
	chrome_options.add_experimental_option("detach", True)
	browser = webdriver.Chrome('/Users/Dennis/Documents/Python/UCLA/chromedriver', chrome_options=chrome_options)

	# open new google flights tab from home airport to destination for months with available flight prices
	browser_open = False
	tab_cnt = 0
	for season in best_months_dict.keys():
		for month in best_months_dict[season].keys():
			if best_months_dict[season][month]['Depart'] != 'Flight prices not avail':
				if not browser_open:
					browser.get(web_url)
					time.sleep(wait)
					browser_open = True

					browser.find_element_by_xpath(r'//*[@class="flt-input gws-flights-form__input-container gws-flights__flex-box gws-flights-form__airport-input gws-flights-form__swapper-right"]').click()
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Where from?"]').send_keys(home_airport, Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@class="flt-input gws-flights-form__input-container gws-flights__flex-box gws-flights-form__airport-input gws-flights-form__empty gws-flights-form__swapper-left"]').click()
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Where to?"]').send_keys(city+', '+country, Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@class="gws-flights-form__date-content"]').click()
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Departure date"]').send_keys(best_months_dict[season][month]['Depart'], Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Return date"]').send_keys(best_months_dict[season][month]['Return'], Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@role="button"]').click()
					time.sleep(wait)
				else:
					tab_cnt = tab_cnt+1
					browser.execute_script("window.open('');")
					browser.switch_to.window(browser.window_handles[tab_cnt])
					browser.get(web_url)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@class="flt-input gws-flights-form__input-container gws-flights__flex-box gws-flights-form__airport-input gws-flights-form__swapper-right"]').click()
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Where from?"]').send_keys(home_airport, Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@class="flt-input gws-flights-form__input-container gws-flights__flex-box gws-flights-form__airport-input gws-flights-form__empty gws-flights-form__swapper-left"]').click()
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Where to?"]').send_keys(city+', '+country, Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@class="gws-flights-form__date-content"]').click()
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Departure date"]').send_keys(best_months_dict[season][month]['Depart'], Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@placeholder="Return date"]').send_keys(best_months_dict[season][month]['Return'], Keys.ENTER)
					time.sleep(wait)

					browser.find_element_by_xpath(r'//*[@role="button"]').click()
					time.sleep(wait)

	print('Complete!\n')
	return best_months_dict


def report(travel_dict, file_type):
	""" Generate travel report file (json, html, or csv)"""
	print('Generating travel report...\t', end='')

	if file_type == 'json':
		with open('travel_report.json', 'w') as json_file:
			json.dump(travel_dict, json_file)
	elif file_type == 'html':
		json_data = json.dumps(travel_dict)
		with open('travel_report.html', 'w') as html_file:
			html_file.write(json2html.convert(json=json_data, table_attributes='cellpadding=\"10\" rules=\"all\" frame=\"box\"'))
	else:
		with open('travel_report.csv', 'w') as csv_file:
			headers = ['Season', 'Month', 'avg_hi', 'avg_lo', 'Depart', 'Return']
			writer = csv.DictWriter(csv_file, fieldnames=headers)
			writer.writeheader()
			for season in travel_dict.keys():
				for month in travel_dict[season].keys():
					writer.writerow({'Season': season, 'Month': month, 'avg_hi': travel_dict[season][month]['avg_hi'], 'avg_lo': travel_dict[season][month]['avg_lo'], 'Depart': travel_dict[season][month]['Depart'], 'Return': travel_dict[season][month]['Return']})

	print('Complete!\n')


city = str(input('Enter destination city: '))
country = str(input('Enter destination country: '))
home_airport = str(input('Enter home IATA airport code: '))
num_of_days = int(input('Enter number of days for trip: '))
file_type = str(input('Enter file type for travel report (csv|html|json): '))

best_season_months = BestMonths(city, country)
best_months_dict = weather(city, country, best_season_months)
travel_dict = flights(city, country, home_airport, num_of_days, best_months_dict)
report(travel_dict, file_type.lower())