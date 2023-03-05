import graphene
from graphene import relay


from .object_graphql import UserObject
from .models import User


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    users = graphene.List(UserObject)

    def resolve_users(self, info, username=None):
        query = UserObject.get_query(info)
        if username:
            query = query.filter(User.username == username)
        return query.all()
