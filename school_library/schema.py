import graphene
import graphql_jwt

from users.schema import UserQuery
from books.schema import BookQuery, BookMutation



class Query(UserQuery, BookQuery, graphene.ObjectType):
    pass


class Mutation(BookMutation, graphene.ObjectType):
    # inherited from graphql_jwt
    token_auth = graphql_jwt.relay.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.relay.Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
