import strawberry

from api.apps.exhibitions.graphql.mutations import Mutation
from api.apps.exhibitions.graphql.queries import Query

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)
