import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from api.apps.exhibitions.utils import slugify


def parse_date_range(date_str: str) -> dict:
    """
    Парсит строку вида '12 to 14 of June' и возвращает start, end, month.
    """
    start_match = re.search(r'(\d+)\s+to\s+\d+', date_str)
    end_match = re.search(r'\d+\s+to\s+(\d+)', date_str)
    month_match = re.search(r'of\s+(\w+)', date_str)

    return {
        "start_date": start_match.group(1) if start_match else None,
        "end_date": end_match.group(1) if end_match else None,
        "month": month_match.group(1) if month_match else None,
    }

def extract_country_city(link) ->dict[str, str]:
    req = requests.get(link)
    soup = BeautifulSoup(req.content, "lxml")
    container = soup.select_one('.other_note_button')
    country = container['data-infcountry']
    city = container['data-infcity']

    return {
        'country': country if country else None,
        'city': city if city else None,
    }

def extract_exhibition_details_info(link: str) -> str:
    req = requests.get(link)
    soup = BeautifulSoup(req.content, "lxml")
    container = soup.select('.col-lg-7')
    detail_text = []
    for elem in container:
        clean_text = elem.get_text(separator=' ', strip=True)
        detail_text.append(clean_text)
    detail_text = ' '.join([i for i in detail_text if i])
    return detail_text

def extract_exhibition_info(block) -> dict | None:
    """
    Извлекает инфу об одной выставке, если всё есть.
    """
    title_tag = block.select_one(".exhibition_title a")
    short_desc = block.select_one(".exhibition_shortdescription")
    date_block = block.select_one(".only_days")
    location = block.select_one('.excenter_location_text')
    category = block.select_one(".primary_category_search")

    if not (title_tag and short_desc and date_block):
        return None

    dates = parse_date_range(date_block.text.strip())
    lines = [line.strip() for line in location.text.split('\n')]
    location = [i for i in lines if i and i !='view map']
    link = title_tag['href']

    country_city = extract_country_city(link)
    country = country_city['country']
    city = country_city['city']

    return {
        "title": title_tag.text.strip(),
        "link": link,
        "short_description": short_desc.text.strip(),
        'description': extract_exhibition_details_info(link),
        'location': location[0] if location else None,
        'country': country,
        'city': city,
        'category': category.text.strip(),
        'category_slug': slugify(category.text.strip()),
        **dates,
    }


def scrape_exhibitions(url: str) -> list[dict]:
    """
    Скрейпит список выставок со страницы.
    """
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "lxml")
    blocks = soup.select(".col-md-10")

    return list(filter(None, (extract_exhibition_info(block) for block in blocks)))


if __name__ == "__main__":
    URL = "https://expo.am/en/exhibitions/all/all/1"
    exhibitions = scrape_exhibitions(URL)
    df = pd.DataFrame(exhibitions)
    df.to_csv("exhibitions_expo_am.csv", index=False)
