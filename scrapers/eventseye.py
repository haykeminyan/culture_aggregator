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
import dateparser

UPLOAD_DIR = '../ui/static/exhibitions/exhibition_pictures'

URL = [ 'https://www.eventseye.com/fairs/zd1_trade-shows_europe_july_0_1.html'
       'https://www.eventseye.com/fairs/zd1_trade-shows_europe_august_0.html', 'https://www.eventseye.com/fairs/zd1_trade-shows_europe_august_0_1.html']

import dateparser
import re

def parse_date_range(text):
    text = text.strip()

    # Удалить лишние запятые
    text = text.replace(',', '')

    # Попробовать найти год в конце
    year_match = re.search(r'(\b\d{4}\b)$', text)
    year = year_match.group(1) if year_match else ''

    # Удалить год из текста
    text_wo_year = text.replace(year, '').strip()

    if '-' in text_wo_year:
        parts = [p.strip() for p in text_wo_year.split('-')]

        if len(parts) == 2:
            # Обработка кейса: "Aug. 29 - Sept. 06"
            # или "Aug. 29 - 31"

            # Если обе части содержат месяцы — используем как есть
            if re.search(r'[A-Za-z]', parts[1]):
                start_str = f"{parts[0]} {year}"
                end_str = f"{parts[1]} {year}"
            else:
                # Вторая часть — только число, значит месяц тот же
                month = re.match(r'[A-Za-z]+\.?', parts[0]).group()
                start_str = f"{parts[0]} {year}"
                end_str = f"{month} {parts[1]} {year}"

            start_date = dateparser.parse(start_str, date_formats=["%Y-%m-%d"])
            end_date = dateparser.parse(end_str, date_formats=["%Y-%m-%d"])
            return start_date, end_date
    else:
        # Простой случай: одна дата
        return dateparser.parse(text), None

    return None, None  # если не удалось разобрать

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
    for date in soup.select('.dates > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1)'):
        date_text = date.text.strip()
        start_date, end_date = parse_date_range(date_text)
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
               'detail': description, 'website': website, 'organizer_name': organization, 'start_date': start_date , 'end_date': end_date, 'price': '', 'currency': '', 'youtube': '', 'instagram':'', 'linkedin':'', 'tiktok': ''}

    asyncio.run(AdminService.create_exhibition(**data))
    full_data.append(data)

df = pd.DataFrame(full_data)
df.to_csv('test.csv')