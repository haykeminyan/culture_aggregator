import os
import uuid
import asyncio, re, dateparser
import requests
from datetime import  timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

UPLOAD_DIR = '../../ui/static/exhibitions/exhibition_pictures'

def parsed_photo(url: str):
    response = requests.get(url)
    unique_name = f'{uuid.uuid4().hex}.jpg'
    filepath = os.path.join(UPLOAD_DIR, unique_name)
    with open(filepath, 'wb') as f:
        f.write(response.content)
    return unique_name

def parse_date_range(text):
    text = text.strip()

    text = re.sub(r'(?i)\bon\b', '', text).replace(',', '').strip()

    year_match = re.search(r'(\b\d{4}\b)$', text)
    year = year_match.group(1) if year_match else ''
    text_wo_year = text.replace(year, '').strip()

    if '-' in text_wo_year:
        parts = [p.strip() for p in text_wo_year.split('-')]

        if len(parts) == 2:
            if re.search(r'[A-Za-z]', parts[1]):
                start_str = f"{parts[0]} {year}"
                end_str = f"{parts[1]} {year}"
            else:
                month = re.match(r'[A-Za-z]+\.?', parts[0]).group()
                start_str = f"{parts[0]} {year}"
                end_str = f"{month} {parts[1]} {year}"

            start_date = dateparser.parse(start_str, date_formats=["%Y-%m-%d"])
            end_date = dateparser.parse(end_str, date_formats=["%Y-%m-%d"])
            return start_date, end_date

    else:
        single_date_str = f"{text_wo_year} {year}".strip()
        single_date = dateparser.parse(single_date_str, date_formats=["%Y-%m-%d"])
        return single_date, single_date  + timedelta(days=1)

    return None, None