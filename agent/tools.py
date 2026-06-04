"""Tools the agent can call. The docstrings ARE the spec the model reads to
decide when and how to use each tool."""

import json

from agents import function_tool

from graphql_app.schema import schema
from rag.retriever import search


@function_tool
def run_graphql_query(query: str) -> str:
    """Run a GraphQL query against the operations ontology and return JSON.

    Use this for structured facts about invoices, vendors, purchase orders, and
    payments. Field names are camelCase (e.g. purchaseOrder, paidDate).
    """
    result = schema.execute_sync(query)
    return json.dumps(
        {
            "data": result.data,
            "errors": [str(e) for e in result.errors] if result.errors else None,
        }
    )


@function_tool
def search_policies(question: str) -> str:
    """Search company policy documents and return the most relevant passages
    with their source filenames.

    Use this to find the rules that govern a payment decision (approval
    thresholds, vendor standing, purchase-order mismatches, duplicate payments).
    """
    hits = search(question, k=3)
    return json.dumps([{"source": h["source"], "text": h["text"]} for h in hits])
