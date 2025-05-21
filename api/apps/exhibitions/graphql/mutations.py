import strawberry
from strawberry.types import Info

from api.apps.exhibitions.graphql.services import ExhibitionServiceGraphQL
from api.apps.exhibitions.graphql.types import Exhibition, ExhibitionCreateInput, ExhibitionCategory, ExhibitionGeo, \
    ExhibitionDetails, ExhibitionUpdateInput
from api.apps.exhibitions.services import ExhibitionService
import logging

logger = logging.getLogger(__name__)

@strawberry.type
class ExhibitionMutationResponse:
    message: str
    exhibition: Exhibition

@strawberry.type
class DeleteResponse:
    success: bool
    message: str

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_exhibition(self, input: ExhibitionCreateInput) -> ExhibitionMutationResponse:
        result = await ExhibitionServiceGraphQL.create_with_full_data(input)
        data = result["exhibition"]

        exhibition = Exhibition.from_dict(data)

        return ExhibitionMutationResponse(message=result["message"], exhibition=exhibition)

    @strawberry.mutation
    async def update_exhibition(self, slug: str,  input: ExhibitionUpdateInput) -> ExhibitionMutationResponse:
        result = await ExhibitionServiceGraphQL.update(slug, input)
        data = result["exhibition"]

        exhibition = Exhibition.from_dict(data)

        return ExhibitionMutationResponse(message=result["message"], exhibition=exhibition)

    @strawberry.mutation
    async def delete_exhibition(self, slug: str) ->DeleteResponse:
        await ExhibitionService.delete(slug)
        return DeleteResponse(success=True, message=f'Exhibition {slug} was deleted')
