"""Donations from the pomegranate Donate card, paid by card on Stripe Checkout.

POST /donate/checkout/ takes the card's form (amount in US dollars, or "custom" for
Other), opens a Checkout Session and sends the visitor to Stripe. Back on the site,
?donated=1 shows a thank-you note. POST /donate/webhook/ receives Stripe's events,
checks their signature with STRIPE_WEBHOOK_SECRET and logs completed donations.
Keys: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET (server .env)."""
import hashlib
import hmac
import json
import logging
import os
import time
from urllib.parse import parse_qs, urlsplit

import aiohttp
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from api.core.i18n import localize, request_lang
from api.core.templates import SITE_URL

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/donate', tags=['Donations'], include_in_schema=False)

STRIPE_API = 'https://api.stripe.com/v1/checkout/sessions'
MIN_USD, MAX_USD = 1, 10_000
SIGNATURE_TOLERANCE = 300  # seconds, as in Stripe's own libraries


def _amount(form: dict) -> int | None:
    """Whole US dollars from the card, or None when it isn't a sensible amount."""
    raw = (form.get('amount') or [''])[0] or (form.get('custom') or [''])[0]
    try:
        dollars = int(float(raw))
    except ValueError:
        return None
    return dollars if MIN_USD <= dollars <= MAX_USD else None


def _back(request: Request, form: dict) -> str:
    """The page the visitor donated from, on this site only."""
    path = (form.get('next') or [''])[0] or urlsplit(request.headers.get('referer', '')).path
    if not path.startswith('/') or path.startswith('//'):
        path = localize('/', request_lang(request))
    return SITE_URL + path


@router.post('/checkout/')
async def checkout(request: Request):
    form = parse_qs((await request.body()).decode('utf-8', 'replace'))
    back = _back(request, form)
    key = os.getenv('STRIPE_SECRET_KEY', '').strip()
    dollars = _amount(form)
    if not key or dollars is None:
        if not key:
            logger.error('donation: STRIPE_SECRET_KEY is not set')
        return RedirectResponse(back, status_code=303)
    sep = '&' if '?' in back else '?'
    payload = {
        'mode': 'payment',
        'submit_type': 'donate',
        'line_items[0][quantity]': '1',
        'line_items[0][price_data][currency]': 'usd',
        'line_items[0][price_data][unit_amount]': str(dollars * 100),
        'line_items[0][price_data][product_data][name]': 'Donation to Baregorc',
        'success_url': f'{back}{sep}donated=1',
        'cancel_url': back,
        'metadata[site]': 'exhibitions',
    }
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
            async with session.post(STRIPE_API, data=payload, auth=aiohttp.BasicAuth(key, '')) as r:
                data = await r.json()
                if r.status != 200:
                    raise RuntimeError(f'Stripe answered {r.status}: {data.get("error", {}).get("message")}')
    except Exception:
        logger.exception('donation: could not open a Stripe Checkout session')
        return RedirectResponse(back, status_code=303)
    return RedirectResponse(data['url'], status_code=303)


def _verified(payload: bytes, header: str, secret: str) -> bool:
    parts = [p.split('=', 1) for p in header.split(',') if '=' in p]
    stamp = next((v for k, v in parts if k == 't'), '')
    signatures = [v for k, v in parts if k == 'v1']
    if not stamp.isdigit() or abs(time.time() - int(stamp)) > SIGNATURE_TOLERANCE:
        return False
    expected = hmac.new(secret.encode(), stamp.encode() + b'.' + payload, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, s) for s in signatures)


@router.post('/webhook/')
async def webhook(request: Request):
    secret = os.getenv('STRIPE_WEBHOOK_SECRET', '').strip()
    payload = await request.body()
    if not secret or not _verified(payload, request.headers.get('stripe-signature', ''), secret):
        return JSONResponse({'error': 'bad signature'}, status_code=400)
    event = json.loads(payload)
    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        logger.info('donation received: %s %s (session %s)', session.get('amount_total', 0) / 100,
                    (session.get('currency') or '').upper(), session.get('id'))
    return {'received': True}
