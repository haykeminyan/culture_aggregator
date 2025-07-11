import asyncio
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import pandas as pd
import dateparser
from FakeAgent import Fake_Agent
from transformers import pipeline
import mdformat

URLS = ['https://slickdeals.net/ajax/dealsYouMayHaveMissed.php?format=vuerango^&hasPrefs=0^&isReturningUser=1^&fpListType=grid',
       'https://slickdeals.net/frontpage/promoted-content/json?isReturningUser=1&hasPrefs=0']
CONCURRENCY = 50
TIMEOUT = 15

sem = asyncio.Semaphore(CONCURRENCY)
fa = Fake_Agent()


CATEGORIES = [
    "toilet paper",
    "shoes",
    "electronics",
    "laptop",
    "headphones",
    "clothing",
    "furniture",
    "groceries",
    "tools",
    "smartphones",
    "smartwatches",
    "pet supplies",
    "office supplies",
    "beauty",
    "sports",
    "home improvement",
    "gift cards",
    "smart home",
    "kitchen appliances",
    "cleaning supplies",
    "vision care",
    "baby products",
    "automotive",
    "gaming",
    "subscription services",
]
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

async def classify_description(text: str) -> str:
    result = classifier(text, CATEGORIES, multi_label=False)
    print(result['labels'][0])
    return result['labels'][0]

async def fetch_description(session: ClientSession, elem: dict):
    try:
        async with session.get(elem['deal_link'], headers={"User-Agent": fa.random()}, timeout=TIMEOUT) as req:
            html = await req.text()
            soup = BeautifulSoup(html, "lxml")
            for description in soup.select('.dealDetailsTab__content'):
                elem['deal_description'] = mdformat.text(description.text.strip())
                print(elem['deal_description'])
                return
            elem['deal_description'] = None
    except Exception as e:
        print(f"[!] Error fetching description for {elem['deal_link']}: {e}")
        elem['deal_description'] = None


async def fetch(url: str, session: ClientSession):
    try:
        async with session.get(url, headers={"User-Agent": fa.random()}, timeout=TIMEOUT) as req:
            response = await req.json()
    except Exception as e:
        print(f"[!] Error fetching {url}: {e}")
        return []

    if isinstance(response, dict) and 'dealCards' in response:
        raw_deals = response['dealCards']
    elif isinstance(response, list):
        raw_deals = response
    else:
        print(f"[!] Unknown format in response from {url}")
        return []

    all_data = []
    for elem in raw_deals:
        image_url = elem.get('dealImageUrl')
        all_data.append({
            'deal_title': elem.get('dealTitle'),
            'deal_link': 'https://slickdeals.net' + elem.get('dealThreadUrl'),
            'deal_title_add': elem.get('dealAdditionalInfo'),
            'deal_image_url': f"https://slickdeals.net{image_url}" if image_url else None,
            'is_fire_deal': elem.get('isFireDeal'),
            'deal_old_price': elem.get('listPriceText'),
            'list_price_text': elem.get('finalPriceText'),
            'final_price_text': elem.get('finalPriceText'),
            'discount': elem.get('discount'),
            'store_name': elem.get('storeName'),
            'store_url': elem.get('storeUrl'),
        })

    # Параллельно описание
    tasks = [fetch_description(session, elem) for elem in all_data]
    await asyncio.gather(*tasks)

    # Параллельно категории
    classify_tasks = [classify_description(elem['deal_title']) for elem in all_data]
    categories = await asyncio.gather(*classify_tasks)
    for elem, category in zip(all_data, categories):
        elem['deal_category'] = category

    return all_data




async def main():
    result = []
    async with ClientSession() as session:
        for url in URLS:
            res = await fetch(url, session)
            result.extend(res)
        df = pd.DataFrame(result)
        df.to_csv('discounts.csv', index=False)

if __name__ == "__main__":
    asyncio.run(main())