import os
from functools import lru_cache

from fastapi.templating import Jinja2Templates

# The one address search engines should index: canonical links, og:url and the
# sitemap all point here, whichever host or path variant served the page.
SITE_URL = os.getenv('SITE_URL', 'https://travelculturehub.com').rstrip('/')
STATIC_ROOT = 'ui/static'


@lru_cache(maxsize=None)
def asset(path: str) -> str:
    """/static URL with the file's mtime as a version, so nginx can cache it for
    a year and a deploy still reaches browsers (and Googlebot) at once."""
    try:
        version = int(os.path.getmtime(os.path.join(STATIC_ROOT, path)))
    except OSError:
        return f'/static/{path}'
    return f'/static/{path}?v={version}'


templates = Jinja2Templates(directory='ui/templates')
templates.env.globals['site_url'] = SITE_URL
templates.env.globals['asset'] = asset
