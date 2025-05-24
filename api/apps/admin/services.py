# routes/admin/exhibitions.py
from api.apps.admin.schemas import CategoryDict
from api.apps.exhibitions.models import  ExhibitionCategory
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


class AdminService:
	@staticmethod
	async def check_unique_category_title_slug(title: str, slug: str) ->CategoryDict:
		existing_title = await ExhibitionCategory.select().where(ExhibitionCategory.title == title).first()
		existing_slug = await ExhibitionCategory.select().where(ExhibitionCategory.slug == slug).first()

		if existing_title and existing_slug:
			if existing_title['id'] == existing_slug['id']:
				category = existing_title
			else:
				raise HTTPException(status_code=400, detail="This title belongs to a different category than this slug.")
		elif existing_title:
			raise HTTPException(status_code=400,
				detail="Category with this title already exists with another slug.",
			)

		elif existing_slug:
			raise HTTPException(status_code=400,
				detail="Category with this slug already exists with another title."
			)
		else:
			category = await ExhibitionCategory.objects().create(title=title, slug=slug)
		return category