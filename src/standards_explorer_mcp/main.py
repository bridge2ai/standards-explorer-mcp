"""Main module for the Standards Explorer MCP implementation."""

import httpx
import asyncio
import os
from typing import Optional
from fastmcp import FastMCP

mcp = FastMCP("standards_explorer_mcp")

# Synapse REST API configuration
SYNAPSE_BASE_URL = "https://repo-prod.prod.sagebase.org"

# These are the IDs for the Bridge2AI Standards Explorer
# DataStandardOrTool table and overall project
SYNAPSE_TABLE_ID = "syn63096833"
SYNAPSE_PROJECT_ID = "syn63096806"

# Authentication can be provided via environment variable
# Set SYNAPSE_AUTH_TOKEN to a Synapse Personal Access Token or session token
# If not set, queries will attempt without authentication (may work for public tables)


def _get_auth_header() -> dict:
    """Get authentication header if token is available."""
    token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def _poll_async_job(client: httpx.AsyncClient, table_id: str, async_token: str, max_wait: int = 30) -> dict:
    """
    Poll an async job until it completes or times out.

    Args:
        client: HTTP client to use
        table_id: The Synapse table ID
        async_token: The async job token
        max_wait: Maximum seconds to wait (default: 30)

    Returns:
        The query result bundle
    """
    url = f"{SYNAPSE_BASE_URL}/repo/v1/entity/{table_id}/table/query/async/get/{async_token}"
    headers = {
        "Content-Type": "application/json",
        **_get_auth_header()
    }

    start_time = asyncio.get_event_loop().time()

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Query timed out after {max_wait} seconds")

        response = await client.get(url, headers=headers)

        # 202 means still processing
        if response.status_code == 202:
            await asyncio.sleep(1)  # Wait 1 second before polling again
            continue

        # Any other status
        response.raise_for_status()
        return response.json()


# Core business logic functions (testable)
async def query_table_impl(
    sql_query: str,
    max_wait_seconds: int = 30
) -> dict:
    """
    Query the Bridge2AI Standards Explorer table using SQL.

    This tool allows you to run SQL queries directly against the Synapse table (syn63096833).
    You can use standard SQL syntax including WHERE clauses for filtering.

    Example queries:
    - "SELECT * FROM syn63096833 LIMIT 10"
    - "SELECT * FROM syn63096833 WHERE name LIKE '%FHIR%'"
    - "SELECT id, name, description FROM syn63096833 WHERE description LIKE '%metadata%' LIMIT 5"

    Note: Authentication may be required. Set the SYNAPSE_AUTH_TOKEN environment variable
    with a Synapse Personal Access Token if queries fail with authentication errors.

    Args:
        sql_query: SQL query string to execute against the table
        max_wait_seconds: Maximum time to wait for query results (default: 30)

    Returns:
        A dictionary containing the query results with rows and column information
    """
    try:
        # Construct the query bundle request
        query_request = {
            "concreteType": "org.sagebionetworks.repo.model.table.QueryBundleRequest",
            "entityId": SYNAPSE_TABLE_ID,
            "query": {
                "sql": sql_query
            },
            "partMask": 0x1 | 0x4 | 0x10  # queryResults + selectColumns + columnModels
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Start the async query
            headers = {
                "Content-Type": "application/json",
                **_get_auth_header()
            }

            start_response = await client.post(
                f"{SYNAPSE_BASE_URL}/repo/v1/entity/{SYNAPSE_TABLE_ID}/table/query/async/start",
                json=query_request,
                headers=headers
            )
            start_response.raise_for_status()

            # Get the async token
            job_info = start_response.json()
            async_token = job_info.get("token")

            if not async_token:
                return {
                    "success": False,
                    "error": "No async token returned from query start"
                }

            # Poll for results
            result_bundle = await _poll_async_job(client, SYNAPSE_TABLE_ID, async_token, max_wait_seconds)

            # Extract useful information from the result
            query_result = result_bundle.get("queryResult", {})
            query_count = result_bundle.get("queryCount")
            column_models = result_bundle.get("columnModels", [])
            select_columns = result_bundle.get("selectColumns", [])

            rows = query_result.get("queryResults", {}).get("rows", [])

            return {
                "success": True,
                "sql_query": sql_query,
                "row_count": len(rows),
                "total_rows": query_count,
                "columns": [{"name": col.get("name"), "type": col.get("columnType")} for col in select_columns],
                "rows": rows,
                "table_id": SYNAPSE_TABLE_ID,
                "project_id": SYNAPSE_PROJECT_ID
            }

    except httpx.HTTPStatusError as e:
        error_detail = e.response.text
        if e.response.status_code == 401 or e.response.status_code == 403:
            error_detail = "Authentication required. Set SYNAPSE_AUTH_TOKEN environment variable with a valid Synapse token."
        return {
            "success": False,
            "error": f"HTTP error occurred: {e.response.status_code}",
            "details": error_detail
        }
    except TimeoutError as e:
        return {
            "success": False,
            "error": str(e)
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


async def search_standards_impl(
    search_text: str,
    columns_to_search: Optional[list[str]] = None,
    max_results: int = 10,
    offset: int = 0
) -> dict:
    """
    Search for text within the Bridge2AI Standards Explorer table.

    This tool searches for text across specified columns in the table (syn63096833).
    By default, it searches common text columns like name and description.

    Args:
        search_text: The text to search for (case-insensitive)
        columns_to_search: List of column names to search (default: ["name", "description"])
        max_results: Maximum number of results to return (default: 10)
        offset: Number of results to skip for pagination (default: 0)

    Returns:
        Query results matching the search text
    """
    if columns_to_search is None:
        columns_to_search = ["name", "description", "purpose_detail"]

    # Build WHERE clause with LIKE for each column
    where_conditions = " OR ".join([
        f"{col} LIKE '%{search_text}%'" for col in columns_to_search
    ])

    sql_query = f"""
        SELECT * FROM {SYNAPSE_TABLE_ID}
        WHERE {where_conditions}
        LIMIT {max_results}
        OFFSET {offset}
    """

    result = await query_table_impl(sql_query)

    if result.get("success"):
        result["search_text"] = search_text
        result["searched_columns"] = columns_to_search

    return result


def get_standards_table_info_impl() -> dict:
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


# MCP tool wrappers
@mcp.tool
async def query_table(sql_query: str, max_wait_seconds: int = 30) -> dict:
    """Query the Bridge2AI Standards Explorer table using SQL."""
    return await query_table_impl(sql_query, max_wait_seconds)


@mcp.tool
async def search_standards(
    search_text: str,
    columns_to_search: Optional[list[str]] = None,
    max_results: int = 10,
    offset: int = 0
) -> dict:
    """Search for text within the Bridge2AI Standards Explorer table."""
    return await search_standards_impl(search_text, columns_to_search, max_results, offset)


@mcp.tool
async def get_standards_table_info() -> dict:
    """Get information about the Bridge2AI Standards Explorer table."""
    return get_standards_table_info_impl()


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
