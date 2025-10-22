"""Main module for the Standards Explorer MCP implementation."""

import httpx
from fastmcp import FastMCP

mcp = FastMCP("standards_explorer_mcp")

# Synapse REST API configuration
SYNAPSE_BASE_URL = "https://repo-prod.prod.sagebase.org"

# These are the IDs for the Bridge2AI Standards Explorer
# DataStandardOrTool table and overall project
SYNAPSE_TABLE_ID = "syn63096833"
SYNAPSE_PROJECT_ID = "syn63096806"


@mcp.tool
async def search_standards(
    query: str,
    max_results: int = 10,
    offset: int = 0
) -> dict:
    """
    Search for standards from Synapse using the Search API.

    Note: The Synapse Search API searches across all public entities in Synapse.
    For more targeted searches within the Bridge2AI Standards Explorer table (syn63096833),
    consider filtering the results or using the table query API instead.

    Args:
        query: The search query string to find standards
        max_results: Maximum number of results to return (default: 10)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        A dictionary containing search results with matching entities
    """
    try:
        # Construct the search query for Synapse
        search_payload = {
            "queryTerm": [query],
            "start": offset,
            "size": max_results,
        }

        # Make the request to Synapse Search API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SYNAPSE_BASE_URL}/repo/v1/search",
                json=search_payload,
                headers={
                    "Content-Type": "application/json"
                }
            )
            response.raise_for_status()

            search_results = response.json()

            return {
                "success": True,
                "query": query,
                "total_results": search_results.get("found", 0),
                "returned_results": len(search_results.get("hits", [])),
                "offset": offset,
                "max_results": max_results,
                "note": "Results are from across all of Synapse. Filter by the table_id or project_id if needed.",
                "table_id": SYNAPSE_TABLE_ID,
                "project_id": SYNAPSE_PROJECT_ID,
                "hits": search_results.get("hits", []),
                "facets": search_results.get("facets", [])
            }

    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error occurred: {e.response.status_code}",
            "details": e.response.text
        }
    except httpx.RequestError as e:
        return {
            "success": False,
            "error": f"Request error occurred: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@mcp.tool
async def get_standards_table_info() -> dict:
    """
    Get information about the Bridge2AI Standards Explorer table.

    Returns basic information about the Synapse table being queried,
    including its ID and the project it belongs to.

    Returns:
        A dictionary with table and project information
    """
    return {
        "table_id": SYNAPSE_TABLE_ID,
        "table_name": "Bridge2AI Standards Explorer Table",
        "project_id": SYNAPSE_PROJECT_ID,
        "project_name": "Bridge2AI Standards Explorer",
        "description": "This table contains standards information from the Bridge2AI Standards Explorer",
        "synapse_url": f"https://www.synapse.org/#!Synapse:{SYNAPSE_TABLE_ID}",
        "project_url": f"https://www.synapse.org/#!Synapse:{SYNAPSE_PROJECT_ID}"
    }


# Main entrypoint
async def main() -> None:
    print("Starting standards_explorer_mcp FastMCP server.")
    await mcp.run_async("stdio")


def cli() -> None:
    """CLI entry point that properly handles the async main function."""
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    cli()
