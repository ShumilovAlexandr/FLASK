import graphene
from flask_graphql_auth import create_access_token

from . import db as db
from api.object_graphql import UserObject
from api.models import User


class UserMutation(graphene.Mutation):
    user = graphene.Field(UserObject)
    
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, email, password):
        user = User(username=username, email=email, password=password)

        db.session.add(user)
        db.session.commit()

        return UserMutation(user=user)


class AuthMutation(graphene.Mutation):
    
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    access_token = graphene.String()

    def mutate(self, info, username, email, password):
        user = User.query.filter_by(username=username, email=email, password=password).first()
        return AuthMutation(
            access_token = create_access_token(user)
            )


class Mutation(graphene.ObjectType):
    mutate_user = UserMutation.Field()
    auth_user = AuthMutation.Field()
