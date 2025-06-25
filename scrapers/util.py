import os
import uuid
import asyncio
import requests
UPLOAD_DIR = '../ui/static/exhibitions/exhibition_pictures'

def parsed_photo(url: str):
	response = requests.get(url)
	unique_name = f'{uuid.uuid4().hex}.jpg'
	filepath = os.path.join(UPLOAD_DIR, unique_name)
	with open(filepath, 'wb') as f:
		f.write(response.content)
	return unique_name