"""Languages: URL prefixes (/hy/..., /pt-br/...), interface strings and date formats.

English lives at the unprefixed URLs; every other language gets its own prefix so
search engines can index each version separately (see hreflang in base.html and
the per-language sitemaps)."""
import json
import os
import re
from functools import lru_cache

from babel import Locale, UnknownLocaleError
from babel.dates import format_date
from jinja2 import pass_context

DEFAULT_LANG = 'en'

LANGUAGES = [
    ('en', 'English'),
    ('hy', 'Հայերեն'),
    ('pt', 'Português (Portugal)'),
    ('pt-br', 'Português (Brasil)'),
    ('ka', 'ქართული'),
    ('uk', 'Українська'),
    ('gl', 'Galego'),
    ('ary', 'الدارجة'),
    ('mwl', 'Mirandés'),
    ('es', 'Español'),
    ('ca', 'Català'),
    ('eu', 'Euskara'),
    ('oc-aranes', 'Aranés'),
    ('it', 'Italiano'),
    ('da', 'Dansk'),
    ('fr', 'Français'),
    ('de', 'Deutsch'),
    ('he', 'עברית'),
    ('ar', 'العربية'),
    ('ja', '日本語'),
    ('ko', '한국어'),
    ('ru', 'Русский'),
]
CODES = [code for code, _ in LANGUAGES]
NAMES = dict(LANGUAGES)
RTL = {'he', 'ar', 'ary'}

# flag image per language (ui/static/flags/<file>.svg)
FLAGS = {
    'en': 'gb', 'hy': 'am', 'pt': 'pt', 'pt-br': 'br', 'ka': 'ge', 'uk': 'ua',
    'gl': 'es-ga', 'ary': 'ma', 'mwl': 'pt', 'es': 'es', 'ca': 'es-ct', 'eu': 'es-pv',
    'oc-aranes': 'oc', 'it': 'it', 'da': 'dk', 'fr': 'fr', 'de': 'de', 'he': 'il',
    'ar': 'sa', 'ja': 'jp', 'ko': 'kr', 'ru': 'ru',
}

# BCP 47 tags for <html lang> and hreflang
HREFLANG = {code: code for code in CODES} | {'pt': 'pt-PT', 'pt-br': 'pt-BR'}

# Babel locales for dates and country names, best match first
_BABEL = {
    'pt': ['pt_PT'], 'pt-br': ['pt_BR'], 'ary': ['ar_MA', 'ar'], 'mwl': ['mwl', 'pt_PT'],
    'oc-aranes': ['oc', 'ca'],
}

LOCALES_DIR = os.path.join('ui', 'locales')
_PREFIX = re.compile(r'^/(' + '|'.join(re.escape(c) for c in CODES if c != DEFAULT_LANG) + r')(?=/|$)')


@lru_cache(maxsize=None)
def strings(lang: str) -> dict:
    if lang == DEFAULT_LANG:
        return {}
    try:
        with open(os.path.join(LOCALES_DIR, f'{lang}.json'), encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def translate(lang: str, text: str, **kw) -> str:
    out = strings(lang).get(text) or text
    for k, v in kw.items():
        out = out.replace('{' + k + '}', str(v))
    return out


@lru_cache(maxsize=None)
def babel_locale(lang: str) -> Locale:
    for name in _BABEL.get(lang, [lang]):
        try:
            return Locale.parse(name)
        except (UnknownLocaleError, ValueError):
            continue
    return Locale.parse('en')


def prefix(lang: str) -> str:
    return '' if lang == DEFAULT_LANG else f'/{lang}'


def localize(path: str, lang: str) -> str:
    """'/exhibition/x' -> '/hy/exhibition/x'; '/' -> '/hy/'."""
    if not path.startswith('/'):
        path = '/' + path
    return prefix(lang) + path


class LanguageMiddleware:
    """Strips a leading /<lang> from the path and remembers the language in
    request.state.lang, so the app's routes stay language-agnostic."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] in ('http', 'websocket'):
            lang = DEFAULT_LANG
            m = _PREFIX.match(scope['path'])
            if m:
                lang = m.group(1)
                scope = dict(scope)
                scope['path'] = scope['path'][m.end():] or '/'
                if scope.get('raw_path'):
                    scope['raw_path'] = scope['path'].encode()
            scope.setdefault('state', {})['lang'] = lang
        await self.app(scope, receive, send)


def request_lang(request) -> str:
    return getattr(request.state, 'lang', DEFAULT_LANG) if request is not None else DEFAULT_LANG


def install(templates):
    """Jinja helpers: _(), lurl(), fdate(), lang info and hreflang alternates."""

    def _lang(ctx):
        return request_lang(ctx.get('request'))

    @pass_context
    def gettext(ctx, text, **kw):
        return translate(_lang(ctx), text, **kw)

    @pass_context
    def lurl(ctx, path, lang=None):
        return localize(path, lang or _lang(ctx))

    @pass_context
    def fdate(ctx, value, fmt='medium'):
        if not value:
            return ''
        return format_date(value, format=fmt, locale=babel_locale(_lang(ctx)))

    @pass_context
    def current_lang(ctx):
        return _lang(ctx)

    @pass_context
    def lang_switch_url(ctx, code):
        """Same page, same query, other language."""
        request = ctx.get('request')
        url = localize(request.url.path, code)
        return url + ('?' + request.url.query if request.url.query else '')

    @pass_context
    def country_name(ctx, name):
        """English country name from the data -> the visitor's language, when Babel knows it."""
        return _country(name, _lang(ctx))

    @pass_context
    def lang_prefix(ctx):
        return prefix(_lang(ctx))

    g = templates.env.globals
    g.update(
        lang_prefix=lang_prefix, _=gettext, lurl=lurl, fdate=fdate, current_lang=current_lang, lang_switch_url=lang_switch_url,
        country_name=country_name, LANGUAGES=LANGUAGES, LANG_FLAGS=FLAGS, HREFLANG=HREFLANG,
        RTL_LANGS=RTL, DEFAULT_LANG=DEFAULT_LANG,
    )


@lru_cache(maxsize=None)
def _english_territories() -> dict:
    return {name.lower(): code for code, name in Locale.parse('en').territories.items()}


@lru_cache(maxsize=4096)
def _country(name: str, lang: str) -> str:
    if not name or lang == DEFAULT_LANG:
        return name
    code = _english_territories().get(name.strip().lower())
    if not code:
        return name
    return babel_locale(lang).territories.get(code, name)
