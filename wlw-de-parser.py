# -*- coding:utf-8 -*-

import csv
import time
import urllib.request

from bs4 import BeautifulSoup


INITIAL_PAGE = r'https://www.wlw.de/de/firmen/it-outsourcing?entered_search=1&q=IT-Outsourcing'
NUM_OF_PAGES = 12

catalog_pages = []
profiles = []
contacts = []
catalog_count = 0
profile_count = 0

for i in range(1, NUM_OF_PAGES+1):
	page = r'%s&page=%d' % (INITIAL_PAGE, i)
	catalog_pages.append(page)


def parse_catalog(url):
	global catalog_count
	global profiles
	
	time.sleep(0.5)
	with urllib.request.urlopen(url) as checked_url:
		html_doc=checked_url.read().decode('utf-8')
	soup = BeautifulSoup(html_doc, 'html.parser')
	
	hrefs = []
	for a in soup.find_all('a', string='Firmendetails ansehen'):
		hrefs.append(r'https://www.wlw.de%s' % a['href'])
	
	catalog_count += 1
	print('%s catalog page done' % catalog_count)
	
	profiles += hrefs

		
def parse_profile(url):
	print('checking profile %s' % url)
	global profile_count
	
	time.sleep(0.5)
	with urllib.request.urlopen(url) as checked_url:
		html_doc=checked_url.read().decode('utf-8')
	soup = BeautifulSoup(html_doc, 'html.parser')
	
	contact = {}
	ul = soup.find('ul', class_='profile-company-contact list-unstyled')
	for li in ul.find_all('li'):
		if 'icon-earphone' in li.a.i['class']:
			content = BeautifulSoup(li.a['data-content'], 'html.parser')
			content.a.i.decompose()
			contact['phone'] = content.a.string.strip()
		elif 'icon-email' in li.a.i['class']:
			li.a.i.decompose()
			contact['email'] = li.a.string.strip()[::-1]
		elif 'icon-website' in li.a.i['class']:
			li.a.i.decompose()
			contact['website'] = li.a.string.strip()
	
	company = soup.h1.string
	contact['company'] = company

	address = soup.find('address', class_='media').div
	contact['name'] = list(address.children)[1].string

	profile_count += 1
	print('%s profile page done' % profile_count)
	
	contacts.append(contact)


def multi_parse(parse_func, url):
	try:
		parse_func(url)
	except Exception as err:
		print('Exception occured: %s' % err)
		print('Trying again...')
		time.sleep(10)
		multi_parse(parse_func, url)


for url in catalog_pages:
	multi_parse(parse_catalog, url)

print('Gathered %s profiles' % len(profiles))

for url in profiles:
	multi_parse(parse_profile, url)

print('Writing into file...')
with open('parse_result.csv', 'w', encoding='utf-8') as csvfile:
    fieldnames = ['company', 'website', 'email', 'phone', 'name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(contacts)
