"""FastAPI app that serves the GraphQL ontology with a GraphiQL playground."""

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from graphql_app.schema import schema

graphql_router = GraphQLRouter(schema)

app = FastAPI(title="Varick Ops Ontology")
app.include_router(graphql_router, prefix="/graphql")
