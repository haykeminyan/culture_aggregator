import os

from fastapi.templating import Jinja2Templates

# The one address search engines should index: canonical links, og:url and the
# sitemap all point here, whichever host or path variant served the page.
SITE_URL = os.getenv('SITE_URL', 'https://travelculturehub.com').rstrip('/')

templates = Jinja2Templates(directory='ui/templates')
templates.env.globals['site_url'] = SITE_URL
