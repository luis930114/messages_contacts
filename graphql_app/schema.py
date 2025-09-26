import strawberry
from strawberry.fastapi import GraphQLRouter
from .resolvers import Query, Mutation

# Crear schema GraphQL
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)

"""graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphql_ide="graphiql", 
)"""

graphql_router = GraphQLRouter(schema)