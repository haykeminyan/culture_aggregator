import os
import uuid
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from transformers import pipeline
from slugify import slugify
from datetime import datetime, timedelta
from api.apps.admin.services import AdminService
import dateparser
from FakeAgent import Fake_Agent
from aiohttp import ClientSession, ClientTimeout
from tqdm import tqdm
import dateparser
import re
import chardet
from util import parsed_photo, parse_date_range


URL = ['https://www.eventseye.com/']
CONCURRENCY = 50
TIMEOUT = 15

sem = asyncio.Semaphore(CONCURRENCY)
fa = Fake_Agent()


async def fetch(url: str, session: ClientSession) -> tuple[str, str | None]:
    async with sem:
        try:
            async with session.get(url, headers = {"User-Agent": fa.random()}, timeout=TIMEOUT) as response:
                raw = await response.read()
                detected = chardet.detect(raw)
                encoding = detected["encoding"] or "utf-8"
                text = raw.decode(encoding, errors="replace")
                return url, text if response.status == 200 else None
        except Exception as e:
            print("ERROR:", e)
            return url, None



async def extract_main_info(session: ClientSession, url: str) -> (list[str], list[int]):
    main_links = []
    number_events = []
    url, content = await fetch(url, session)
    if content:
        soup = BeautifulSoup(content, 'lxml')
        for all_links_soup in soup.select('.zm-group'):
            for all_links in all_links_soup.select('.monthgraph'):
                for link in all_links.select('a'):
                    main_links.append('https://www.eventseye.com/fairs/' + link.get('href'))
                number_events = re.findall(r'[A-Za-z]{3}\s+(\d+)', all_links.text.strip())
    return main_links, [int(elem)//48 for elem in number_events]

def extracting_all_main_pages(main_links: list[str], number_pages: list[int]) -> list[str]:
    for link, page in zip(main_links, number_pages):
        for page_num in range(1, page + 1):
            new_link = link.replace('.html', f'_{page_num}.html')
            main_links.append(new_link)
    return main_links

async def extract_single_page(session: ClientSession, url: str) -> list[str]:
    req, content = await fetch(url, session)
    result = []
    if content:
        soup = BeautifulSoup(content, 'lxml')
        for link in soup.select('.tradeshows'):
            for a in link.select('a'):
                if 'f-' in a.get('href', ''):
                    result.append('https://www.eventseye.com/fairs/' + a['href'])
    return result

async def extract_all_pages(session: ClientSession, main_links: list[str]) -> list[str]:
    tasks = [extract_single_page(session, url) for url in main_links]
    results = await asyncio.gather(*tasks)
    # Объединяем все результаты в один список
    all_pages = [page for sublist in results for page in sublist]
    print(all_pages)
    return all_pages

async def parse_event_page(event_link: str, session: ClientSession, sem: asyncio.Semaphore) -> dict | None:
    async with sem:
        try:
            req, content = await fetch(event_link, session)
            soup = BeautifulSoup(content, 'lxml')

            title = soup.select_one('.title-line').text.strip()
            img = soup.select_one('.title-line img')
            image = parsed_photo('https://www.eventseye.com' + img['src']) if img else None

            city = re.search(r'([A-Z][A-Za-zÀ-ÿ\'\- ]+)\s*\([A-Za-zÀ-ÿ\'\- ]+\)', soup.select_one('.dates').text).group(1).strip()
            date_text = soup.select_one('.dates > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1)').text.strip()
            start_date, end_date = parse_date_range(date_text)
            description = soup.select_one('.description').text.strip().replace('Description', '')

            country = soup.select_one('.countrylink').text.strip()

            categories = [a.get('title').strip() for a in soup.select_one('.industries').select('a')]
            classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
            result = classifier(description, categories)
            final_category_ds = result['labels'][0]
            final_category = final_category_ds.split('exhibitions in')[0].strip()

            venue = soup.select_one('.venue')
            phone = venue.select_one('.ev-phone').text.strip() if venue.select_one('.ev-phone') else ''
            location_elem = venue.select_one('.placelink')
            location = location_elem.text.strip()
            location_href = 'https://www.eventseye.com/fairs/' + location_elem.get('href')

            loc_req, loc_content = await fetch(location_href, session)
            coords = re.search(r'LatLng\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)', str(loc_content))
            latitude, longitude = (float(coords.group(1)), float(coords.group(2))) if coords else (None, None)

            website = venue.select_one('.ev-web')['href'] if venue.select_one('.ev-web') else ''
            email = venue.select_one('.ev-mail')['href'] if venue.select_one('.ev-mail') else ''
            organization = soup.select_one('.orgs .orglink').get('title') if soup.select_one('.orgs .orglink') else ''

            data = {
                'images': [image], 'title': title, 'slug': slugify(str(title)),
                'short_description': description[:200], 'email': email,
                'category_title': final_category, 'category_slug': slugify(str(final_category)),
                'location': location, 'latitude': latitude, 'longitude': longitude,
                'country': country, 'city': city, 'detail': description,
                'website': website, 'organizer_name': organization,
                'start_date': start_date, 'end_date': end_date,
                'price': '', 'currency': '', 'youtube': '', 'instagram': '', 'linkedin': '', 'tiktok': ''
            }

            await AdminService.create_exhibition(**data)
            return data
        except Exception as e:
            print(f"Error parsing {event_link}: {e}")
            return None

async def parsing(links: list[str], session: ClientSession) -> list[dict]:
    sem = asyncio.Semaphore(30)
    tasks = [parse_event_page(link, session, sem) for link in links]
    results = await asyncio.gather(*tasks)

    full_data = [res for res in results if res]
    pd.DataFrame(full_data).to_csv('test.csv')
    return full_data

async def main():
    async with aiohttp.ClientSession() as session:
        all_main_links = []
        all_page_counts = []
        for url in tqdm(URL):
            links, counts = await extract_main_info(session, url)
            all_main_links.extend(links)
            all_page_counts.extend(counts)
        all_main_pages = extracting_all_main_pages(all_main_links, all_page_counts)
        all_pages = await extract_all_pages(session, all_main_pages)
        await parsing(all_pages, session)


if __name__ == "__main__":
    asyncio.run(main())
