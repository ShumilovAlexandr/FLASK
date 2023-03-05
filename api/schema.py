from graphene import Schema


from .query import Query
from .mutation import Mutation

schem = Schema(query=Query, mutation=Mutation)
