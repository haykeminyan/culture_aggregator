"""
Парсер eventseye.com -> exhibition DB.

Ключевые изменения относительно исходной версии:
- classifier (zero-shot) грузится ОДИН раз, а не на каждой странице (это было
  главной причиной медленной работы — загрузка модели весом ~1.6GB на каждый ивент).
- classifier запускается через asyncio.to_thread, чтобы не блокировать event loop.
- Раздельные семафоры для сетевых запросов и для CPU-тяжёлой классификации.
- Ретраи с экспоненциальным backoff на fetch().
- Исправлен баг: main_links мутировался во время zip-итерации по нему же.
- Структурированное логирование в файл + консоль, статистика в конце прогона.
- Инкрементальное сохранение в CSV (не теряем прогресс при падении на середине).
- Guard'ы на отсутствующие селекторы (venue, image, categories и т.д.), чтобы
  одна битая страница не роняла весь прогон.
"""

import asyncio
import csv
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import aiohttp
import chardet
from aiohttp import ClientSession, ClientTimeout
from bs4 import BeautifulSoup
from slugify import slugify
from tqdm.asyncio import tqdm_asyncio

from api.apps.admin.services import AdminService
from FakeAgent import Fake_Agent
from util import parsed_photo, parse_date_range

# ---------------------------------------------------------------------------
# Конфиг
# ---------------------------------------------------------------------------

@dataclass
class ScraperConfig:
    urls: list[str] = field(default_factory=lambda: ["https://www.eventseye.com/"])
    fetch_concurrency: int = 12          # одновременных HTTP-запросов к сайту
    parse_concurrency: int = 6           # одновременных обработок страницы ивента
    classify_concurrency: int = 2        # одновременных вызовов классификатора (CPU-bound)
    request_timeout: int = 15
    max_retries: int = 3
    backoff_base: float = 1.5            # секунд, множится на 2**попытка
    politeness_delay: float = 0.15       # небольшая пауза между запросами, чтобы не долбить сайт
    max_pages_per_section: int = 60      # предохранитель от бесконечной пагинации
    output_csv: str = "eventseye_export.csv"
    log_file: str = "logs/scraper.log"


CONFIG = ScraperConfig()

# ---------------------------------------------------------------------------
# Логирование
# ---------------------------------------------------------------------------

def setup_logging(log_file: str) -> logging.Logger:
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("eventseye_scraper")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    console.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(fmt)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(console)
    logger.addHandler(file_handler)
    return logger


log = setup_logging(CONFIG.log_file)

# ---------------------------------------------------------------------------
# Общие ресурсы: user-agent генератор, семафоры, классификатор (ленивая загрузка один раз)
# ---------------------------------------------------------------------------

fa = Fake_Agent()

fetch_semaphore = asyncio.Semaphore(CONFIG.fetch_concurrency)
parse_semaphore = asyncio.Semaphore(CONFIG.parse_concurrency)
classify_semaphore = asyncio.Semaphore(CONFIG.classify_concurrency)

_classifier = None
_classifier_lock = asyncio.Lock()


async def get_classifier():
    """Грузим zero-shot classifier ОДИН раз на весь прогон, лениво при первом обращении."""
    global _classifier
    if _classifier is None:
        async with _classifier_lock:
            if _classifier is None:
                log.info("Загружаю zero-shot classifier (facebook/bart-large-mnli)... это займёт время один раз")
                t0 = time.perf_counter()
                # тяжёлая синхронная загрузка модели -> в отдельный поток, чтобы не блокировать loop
                from transformers import pipeline
                _classifier = await asyncio.to_thread(
                    pipeline, "zero-shot-classification", model="facebook/bart-large-mnli"
                )
                log.info("Classifier загружен за %.1fs", time.perf_counter() - t0)
    return _classifier


async def classify_category(description: str, categories: list[str]) -> str | None:
    if not categories:
        return None
    classifier = await get_classifier()
    async with classify_semaphore:
        result = await asyncio.to_thread(classifier, description, categories)
    return result["labels"][0]


# ---------------------------------------------------------------------------
# Сеть
# ---------------------------------------------------------------------------

async def fetch(url: str, session: ClientSession) -> tuple[str, str | None]:
    """GET с ретраями и экспоненциальным backoff. Возвращает (url, html|None)."""
    last_error = None
    for attempt in range(1, CONFIG.max_retries + 1):
        async with fetch_semaphore:
            try:
                await asyncio.sleep(CONFIG.politeness_delay)
                async with session.get(
                    url,
                    headers={"User-Agent": fa.random()},
                    timeout=ClientTimeout(total=CONFIG.request_timeout),
                ) as response:
                    if response.status == 429:
                        wait = CONFIG.backoff_base * (2 ** attempt)
                        log.warning("429 Too Many Requests на %s, жду %.1fs (попытка %d/%d)",
                                    url, wait, attempt, CONFIG.max_retries)
                        await asyncio.sleep(wait)
                        continue
                    if response.status != 200:
                        log.warning("HTTP %s для %s", response.status, url)
                        return url, None

                    raw = await response.read()
                    detected = chardet.detect(raw)
                    encoding = detected["encoding"] or "utf-8"
                    return url, raw.decode(encoding, errors="replace")
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = e
                wait = CONFIG.backoff_base * (2 ** attempt)
                log.warning("Ошибка сети на %s (попытка %d/%d): %s — жду %.1fs",
                            url, attempt, CONFIG.max_retries, e, wait)
                await asyncio.sleep(wait)

    log.error("Не удалось получить %s после %d попыток: %s", url, CONFIG.max_retries, last_error)
    return url, None


# ---------------------------------------------------------------------------
# Сбор ссылок
# ---------------------------------------------------------------------------

async def extract_main_info(session: ClientSession, url: str) -> list[str]:
    """Ссылки на месячные разделы (d1_trade-shows_<month>_<n>.html) с главной."""
    main_links: list[str] = []

    _, content = await fetch(url, session)
    if not content:
        log.error("Не удалось загрузить главную страницу %s", url)
        return main_links

    soup = BeautifulSoup(content, "lxml")
    for group in soup.select(".zm-group"):
        for month_block in group.select(".monthgraph"):
            for link in month_block.select("a"):
                href = link.get("href")
                if href:
                    full = href if href.startswith("http") else f"https://www.eventseye.com/fairs/{href}"
                    if full not in main_links:
                        main_links.append(full)

    log.info("Найдено %d ссылок на месячные разделы", len(main_links))
    return main_links


def _event_links_from_listing(content: str) -> list[str]:
    soup = BeautifulSoup(content, "lxml")
    result: list[str] = []
    for block in soup.select(".tradeshows"):
        for a in block.select("a"):
            href = a.get("href", "")
            if "f-" in href:
                result.append(href if href.startswith("http") else f"https://www.eventseye.com/fairs/{href}")
    return result


async def extract_month_section(session: ClientSession, url: str) -> list[str]:
    """Обходим все страницы раздела: <name>.html, <name>_1.html, <name>_2.html ...
    пока страница не вернёт ни одной новой ссылки.

    Раньше число страниц считалось из счётчика на главной (count // 48) и
    склеивалось с ссылками через zip — при 50 ивентах на страницу и любом
    расхождении текста счётчика это теряло хвосты разделов."""
    result: list[str] = []
    seen: set[str] = set()
    for page_num in range(0, CONFIG.max_pages_per_section):
        page_url = url if page_num == 0 else url.replace(".html", f"_{page_num}.html")
        _, content = await fetch(page_url, session)
        if not content:
            break
        new_links = [link for link in _event_links_from_listing(content) if link not in seen]
        if not new_links:
            break
        seen.update(new_links)
        result.extend(new_links)
    log.debug("%s: %d ивентов", url, len(result))
    return result


async def extract_all_pages(session: ClientSession, main_links: list[str]) -> list[str]:
    tasks = [extract_month_section(session, url) for url in main_links]
    results = await tqdm_asyncio.gather(*tasks, desc="Собираю ссылки на ивенты")
    total = sum(len(r) for r in results)

    # Ежегодные выставки попадают в разделы нескольких месяцев/лет (окно ~2 года),
    # но ссылка на страницу ивента одна и та же (f-<name>-<id>-1.html) и всегда
    # показывает ближайшую редакцию. Без дедупликации каждый такой ивент парсился
    # дважды, а второй раз молча отбрасывался как дубль slug.
    unique = list(dict.fromkeys(link for sublist in results for link in sublist))
    log.info("Собрано %d ссылок на ивенты, уникальных %d", total, len(unique))
    return unique


# ---------------------------------------------------------------------------
# Парсинг одной страницы ивента
# ---------------------------------------------------------------------------

def _text_or_none(el) -> str | None:
    return el.text.strip() if el else None


async def parse_event_page(event_link: str, session: ClientSession) -> dict | None:
    async with parse_semaphore:
        try:
            _, content = await fetch(event_link, session)
            if not content:
                return None
            soup = BeautifulSoup(content, "lxml")

            title_el = soup.select_one(".title-line")
            if not title_el:
                log.warning("Пропускаю %s: нет .title-line", event_link)
                return None
            title = title_el.text.strip()

            img = soup.select_one(".title-line img")
            image = parsed_photo("https://www.eventseye.com" + img["src"]) if img and img.get("src") else None

            dates_el = soup.select_one(".dates")
            city_match = re.search(r"([A-Z][A-Za-zÀ-ÿ'\- ]+)\s*\([A-Za-zÀ-ÿ'\- ]+\)", dates_el.text) if dates_el else None
            city = city_match.group(1).strip() if city_match else None

            date_cell = soup.select_one(".dates > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(1)")
            start_date = end_date = None
            if date_cell:
                start_date, end_date = parse_date_range(date_cell.text.strip())

            description = (_text_or_none(soup.select_one(".description")) or "").replace("Description", "")
            country = _text_or_none(soup.select_one(".countrylink"))

            industries_el = soup.select_one(".industries")
            categories = [a.get("title", "").strip() for a in industries_el.select("a")] if industries_el else []
            final_category = None
            if categories and description:
                label = await classify_category(description, categories)
                final_category = label.split("exhibitions in")[0].strip() if label else None

            venue = soup.select_one(".venue")
            location, location_href = None, None
            if venue:
                location_elem = venue.select_one(".placelink")
                if location_elem:
                    location = location_elem.text.strip()
                    href = location_elem.get("href")
                    location_href = f"https://www.eventseye.com/fairs/{href}" if href else None

            latitude = longitude = None
            if location_href:
                _, loc_content = await fetch(location_href, session)
                coords = re.search(r"LatLng\((-?\d+\.\d+),\s*(-?\d+\.\d+)\)", loc_content or "")
                if coords:
                    latitude, longitude = float(coords.group(1)), float(coords.group(2))

            website = venue.select_one(".ev-web")["href"] if venue and venue.select_one(".ev-web") else ""
            email = venue.select_one(".ev-mail")["href"] if venue and venue.select_one(".ev-mail") else ""
            org_el = soup.select_one(".orgs .orglink")
            organization = org_el.get("title") if org_el else ""

            data = {
                "images": [image] if image else [],
                "title": title,
                "slug": slugify(str(title)),
                "short_description": description[:200],
                "email": email,
                "category_title": final_category,
                "category_slug": slugify(str(final_category)) if final_category else None,
                "location": location,
                "latitude": latitude,
                "longitude": longitude,
                "country": country,
                "city": city,
                "detail": description,
                "website": website,
                "organizer_name": organization,
                "start_date": start_date,
                "end_date": end_date,
                "price": "",
                "currency": "",
                "youtube": "",
                "instagram": "",
                "linkedin": "",
                "tiktok": "",
            }

            response = await AdminService.create_exhibition(**data)
            if getattr(response, "status_code", 200) >= 400:
                # create_exhibition не бросает исключение, а возвращает 400 (например, дубль slug)
                log.warning("Не сохранено %s (%s): %s", title, event_link,
                            getattr(response, "body", b"").decode("utf-8", "replace"))
                return None
            log.info("OK: %s", title)
            return data
        except Exception:
            log.exception("Ошибка парсинга %s", event_link)
            return None


# ---------------------------------------------------------------------------
# CSV-writer с инкрементальным сохранением (не теряем всё при падении)
# ---------------------------------------------------------------------------

class IncrementalCsvWriter:
    def __init__(self, path: str):
        self.path = path
        self._writer = None
        self._file = None
        self._lock = asyncio.Lock()

    async def write(self, row: dict):
        async with self._lock:
            if self._writer is None:
                self._file = open(self.path, "w", newline="", encoding="utf-8")
                self._writer = csv.DictWriter(self._file, fieldnames=list(row.keys()))
                self._writer.writeheader()
            self._writer.writerow(row)
            self._file.flush()

    def close(self):
        if self._file:
            self._file.close()


# ---------------------------------------------------------------------------
# Оркестрация
# ---------------------------------------------------------------------------

async def parsing(links: list[str], session: ClientSession) -> list[dict]:
    csv_writer = IncrementalCsvWriter(CONFIG.output_csv)
    success = 0
    failed = 0

    async def _run(link: str):
        nonlocal success, failed
        result = await parse_event_page(link, session)
        if result:
            await csv_writer.write(result)
            success += 1
        else:
            failed += 1
        return result

    tasks = [_run(link) for link in links]
    results = await tqdm_asyncio.gather(*tasks, desc="Парсю ивенты")
    csv_writer.close()

    log.info("Готово: %d успешно, %d с ошибкой (см. %s)", success, failed, CONFIG.log_file)
    return [r for r in results if r]


async def main():
    t0 = time.perf_counter()
    log.info("Старт парсинга. fetch_concurrency=%d parse_concurrency=%d",
              CONFIG.fetch_concurrency, CONFIG.parse_concurrency)
    await get_classifier()
    connector = aiohttp.TCPConnector(limit=CONFIG.fetch_concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        all_main_links: list[str] = []
        for url in CONFIG.urls:
            all_main_links.extend(await extract_main_info(session, url))

        all_event_pages = await extract_all_pages(session, all_main_links)
        await parsing(all_event_pages, session)

    log.info("Весь прогон занял %.1f минут", (time.perf_counter() - t0) / 60)


if __name__ == "__main__":
    asyncio.run(main())