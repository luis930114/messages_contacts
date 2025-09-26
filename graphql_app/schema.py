import strawberry
from strawberry.fastapi import GraphQLRouter
from .resolvers import Query, Mutation, Subscription

# Crear schema GraphQL
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription  # Opcional
)

graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    graphql_ide="graphiql", 
)