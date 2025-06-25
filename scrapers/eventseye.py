import os
import uuid
import asyncio
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from transformers import pipeline
from slugify import slugify
from datetime import datetime
from api.apps.admin.services import AdminService
from scrapers.util import parsed_photo

UPLOAD_DIR = '../ui/static/exhibitions/exhibition_pictures'

URL = [ 'https://www.eventseye.com/fairs/zd1_trade-shows_europe_july_0_1.html'
       'https://www.eventseye.com/fairs/zd1_trade-shows_europe_august_0.html', 'https://www.eventseye.com/fairs/zd1_trade-shows_europe_august_0_1.html']

links = []
for url in URL:
	req = requests.get(url)
	soup = BeautifulSoup(req.content, 'lxml')
	for link in soup.select('.tradeshows'):
		for a in link.select('a'):
			if 'f-' in a['href']:
				links.append('https://www.eventseye.com/fairs/' + a['href'])

full_data = []
for event_link in links:
	print(event_link)
	req = requests.get(event_link)
	soup = BeautifulSoup(req.content, 'lxml')
	for image in soup.select('.title-line'):
		title = image.text.strip()
		for img in image.select('img'):
			image_url = 'https://www.eventseye.com'+ img['src']
			image = parsed_photo(image_url)

	for elem in soup.select('.dates'):
		city = re.search(r'([A-Z][A-Za-zÀ-ÿ\'\- ]+)\s*\([A-Za-zÀ-ÿ\'\- ]+\)', elem.text.strip()).group(1).strip()
		# Пробуем сначала "Month DD - DD, YYYY"
		range_match = re.search(r'([A-Za-z]+)\s(\d{1,2})\s*-\s*(\d{1,2}),\s*(\d{4})', elem.text.strip())

		# Пробуем "on Month YYYY"
		month_year_match = re.search(r'on\s([A-Za-z]+)\s(\d{4})', elem.text.strip())

		if range_match:
			month_str, day_start, day_end, year = range_match.groups()
			month_num = datetime.strptime(month_str, "%B").month
			start_date = f"{year}-{month_num:02d}-{int(day_start):02d}"
			end_date = f"{year}-{month_num:02d}-{int(day_end):02d}"
		elif month_year_match:
			month_str, year = month_year_match.groups()
			month_num = datetime.strptime(month_str, "%B").month
			start_date = f"{year}-{month_num:02d}-01"
			end_date = f"{year}-{month_num:02d}-28"
		else:
			start_date = None
			end_date = None
	for desc in soup.select('.description'):
		description = desc.text.strip().replace('Description', '')
	for country_soup in soup.select('.countrylink'):
		country = country_soup.text.strip()
	for category_soup in soup.select('.industries'):
		categories = []
		for category_title in category_soup.select('a'):
			category = category_title.get('title')
			categories.append(category)
		classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

		result = classifier(description, categories)
		final_category_ds = result['labels'][0]
		final_category = final_category_ds.split('exhibitions in')[0]
	for body in soup.select('.venue'):
		for elem in body.select('.ev-phone'):
			phone = elem.text.strip()
		for elem in body.select('.placelink'):
			location = elem.text.strip()
			location_href = 'https://www.eventseye.com/fairs/' + elem.get('href')
			req_loc = requests.get(location_href)
			soup_loc = BeautifulSoup(req_loc.content, 'lxml')
			try:
				coordinates = re.search(r'LatLng\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)', str(soup_loc)).groups()
				latitude = float(coordinates[0])
				longitude = float(coordinates[1])
			except AttributeError:
				latitude = None
				longitude = None
		for elem in body.select('.ev-web'):
			website = elem['href']
		for elem in body.select('.ev-mail'):
			email = elem['href']
	for elem in soup.select('.orgs'):
		for org in elem.select('.orglink'):
			organization = org.get('title')

	data = {'images': [image], 'title': title, 'slug': slugify(str(title)), 'short_description': description[:200], 'email': email,
	        'category_title': final_category, 'category_slug': slugify(str(final_category)), 'location': location, 'latitude': latitude, 'longitude': longitude, 'country': country, 'city': city,
	           'detail': description, 'website': website, 'organizer_name': organization, 'start_date': datetime.strptime(start_date, "%Y-%m-%d"), 'end_date': datetime.strptime(end_date, "%Y-%m-%d"), 'price': '', 'currency': '', 'youtube': '', 'instagram':'', 'linkedin':'', 'tiktok': ''}

	asyncio.run(AdminService.create_exhibition(**data))
	full_data.append(data)

df = pd.DataFrame(full_data)
df.to_csv('test.csv')