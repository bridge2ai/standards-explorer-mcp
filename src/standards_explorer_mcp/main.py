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
SYNAPSE_TOPICS_TABLE_ID = "syn63096835"

# Topic name to ID mapping cache
# Will be populated on first use
_TOPICS_CACHE: Optional[dict[str, str]] = None

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


async def _load_topics_mapping() -> dict[str, str]:
    """
    Load the DataTopics table and create a mapping from topic names to IDs.

    Returns:
        Dictionary mapping topic names (lowercase) to topic IDs
    """
    global _TOPICS_CACHE

    if _TOPICS_CACHE is not None:
        return _TOPICS_CACHE

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Query all topics
            query_request = {
                "concreteType": "org.sagebionetworks.repo.model.table.QueryBundleRequest",
                "entityId": SYNAPSE_TOPICS_TABLE_ID,
                "query": {
                    "sql": f"SELECT id, name FROM {SYNAPSE_TOPICS_TABLE_ID}"
                },
                "partMask": 0x1 | 0x4 | 0x10
            }

            headers = {
                "Content-Type": "application/json",
                **_get_auth_header()
            }

            start_response = await client.post(
                f"{SYNAPSE_BASE_URL}/repo/v1/entity/{SYNAPSE_TOPICS_TABLE_ID}/table/query/async/start",
                json=query_request,
                headers=headers
            )
            start_response.raise_for_status()

            async_token = start_response.json().get("token")
            if not async_token:
                return {}

            result_bundle = await _poll_async_job(client, SYNAPSE_TOPICS_TABLE_ID, async_token, 30)

            # Build the mapping
            mapping = {}
            rows = result_bundle.get("queryResult", {}).get(
                "queryResults", {}).get("rows", [])

            for row in rows:
                values = row.get("values", [])
                if len(values) >= 2:
                    topic_id = values[0]  # id column
                    topic_name = values[1]  # name column
                    if topic_id and topic_name:
                        # Store both lowercase and original case mappings
                        mapping[topic_name.lower()] = topic_id
                        mapping[topic_name] = topic_id

            _TOPICS_CACHE = mapping
            return mapping

    except Exception as e:
        # If we can't load topics, return empty mapping
        print(f"Warning: Could not load topics mapping: {e}")
        return {}


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
    offset: int = 0,
    include_topic_search: bool = True
) -> dict:
    """
    Search for text within the Bridge2AI Standards Explorer table.

    This tool searches for text across specified columns in the table (syn63096833).
    By default, it searches common text columns like name and description.

    Additionally, if the search text matches a known data topic name, it will also
    search the concerns_data_topic column for that topic ID.

    Args:
        search_text: The text to search for (case-insensitive)
        columns_to_search: List of column names to search (default: ["name", "description"])
        max_results: Maximum number of results to return (default: 10)
        offset: Number of results to skip for pagination (default: 0)
        include_topic_search: Whether to also search by topic if name matches (default: True)

    Returns:
        Query results matching the search text
    """
    if columns_to_search is None:
        columns_to_search = ["name", "description", "purpose_detail"]

    # Build WHERE clause with LIKE for each column
    where_conditions = " OR ".join([
        f"{col} LIKE '%{search_text}%'" for col in columns_to_search
    ])

    # Check if search text matches a topic name
    topic_condition = None
    matched_topic_id = None
    if include_topic_search:
        topics_map = await _load_topics_mapping()
        matched_topic_id = topics_map.get(search_text.lower())

        if matched_topic_id:
            # Add topic search to WHERE clause
            topic_condition = f"concerns_data_topic LIKE '%{matched_topic_id}%'"
            where_conditions = f"({where_conditions}) OR {topic_condition}"

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
        if matched_topic_id:
            result["also_searched_topic"] = {
                "topic_id": matched_topic_id,
                "topic_name": search_text
            }

    return result


async def search_with_variations_impl(
    search_text: str,
    search_variations: list[str],
    columns_to_search: Optional[list[str]] = None,
    max_results_per_term: int = 5
) -> dict:
    """
    Search for a term and its variations, returning combined deduplicated results.

    This tool takes a list of search term variations and searches for each one,
    combining and deduplicating the results.

    Args:
        search_text: The primary search term
        search_variations: List of term variations to search (including the original term)
        columns_to_search: List of column names to search (default: ["name", "description"])
        max_results_per_term: Maximum results per search term (default: 5)

    Returns:
        Combined search results from all term variations
    """
    all_results = []
    seen_ids = set()

    # Search for each variation
    for term in search_variations:
        result = await search_standards_impl(
            search_text=term,
            columns_to_search=columns_to_search,
            max_results=max_results_per_term,
            offset=0
        )

        if result.get("success") and result.get("rows"):
            # Deduplicate by ID
            for row in result["rows"]:
                row_id = row["values"][0] if row.get("values") else None
                if row_id and row_id not in seen_ids:
                    seen_ids.add(row_id)
                    all_results.append({
                        "row": row,
                        "matched_term": term,
                        "is_original": term == search_text
                    })

    # Get column info from first successful search
    columns = []
    if all_results:
        first_search = await search_standards_impl(
            search_text=search_text,
            columns_to_search=columns_to_search,
            max_results=1,
            offset=0
        )
        columns = first_search.get("columns", [])

    return {
        "success": True,
        "original_term": search_text,
        "search_variations": search_variations,
        "total_results": len(all_results),
        "columns": columns,
        "results": all_results,
        "table_id": SYNAPSE_TABLE_ID,
        "project_id": SYNAPSE_PROJECT_ID
    }


async def search_by_topic_impl(
    topic_name: str,
    max_results: int = 20
) -> dict:
    """
    Search for standards by data topic name.

    This function looks up the topic name in the DataTopics table to find its ID,
    then searches for standards that concern that topic.

    Args:
        topic_name: The topic name to search for (case-insensitive, e.g., "EHR", "Genomics")
        max_results: Maximum number of results to return (default: 20)

    Returns:
        Query results for standards related to the specified topic
    """
    # Load topics mapping
    topics_map = await _load_topics_mapping()

    # Look up the topic ID
    topic_id = topics_map.get(topic_name.lower())

    if not topic_id:
        # Try partial matching
        matching_topics = {}
        search_lower = topic_name.lower()
        for name, tid in topics_map.items():
            if search_lower in name.lower() or name.lower() in search_lower:
                matching_topics[name] = tid

        if not matching_topics:
            return {
                "success": False,
                "error": f"Topic '{topic_name}' not found",
                "available_topics": list(set(topics_map.values())),
                "suggestion": "Try using the list_topics tool to see available topics"
            }

        # If we found multiple matches, use the first one but inform the user
        topic_id = list(matching_topics.values())[0]
        matched_name = list(matching_topics.keys())[0]
    else:
        matched_name = topic_name

    # Search for standards with this topic ID in their concerns_data_topic column
    # The concerns_data_topic column contains JSON arrays like ["B2AI_TOPIC:12", "B2AI_TOPIC:13"]
    sql_query = f"""
        SELECT * FROM {SYNAPSE_TABLE_ID}
        WHERE concerns_data_topic LIKE '%{topic_id}%'
        LIMIT {max_results}
    """

    result = await query_table_impl(sql_query)

    if result.get("success"):
        result["topic_name"] = matched_name
        result["topic_id"] = topic_id
        result["search_method"] = "topic"

    return result


async def list_topics_impl() -> dict:
    """
    List all available data topics from the DataTopics table.

    Returns:
        Dictionary containing all available topics with their IDs and descriptions
    """
    try:
        # Query the topics table
        result = await query_table_impl(
            sql_query=f"SELECT id, name, description FROM {SYNAPSE_TOPICS_TABLE_ID}",
            max_wait_seconds=30
        )

        if result.get("success"):
            topics = []
            for row in result.get("rows", []):
                values = row.get("values", [])
                if len(values) >= 3:
                    topics.append({
                        "id": values[0],
                        "name": values[1],
                        "description": values[2] if values[2] else "No description available"
                    })

            return {
                "success": True,
                "topics": topics,
                "total_topics": len(topics),
                "table_id": SYNAPSE_TOPICS_TABLE_ID
            }
        else:
            return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list topics: {str(e)}"
        }


async def search_topics_impl(
    search_text: str,
    max_results: int = 20
) -> dict:
    """
    Search for topics by name or description.

    This function searches the DataTopics table for topics matching the search text.

    Args:
        search_text: The text to search for in topic names and descriptions
        max_results: Maximum number of results to return (default: 20)

    Returns:
        Matching topics with their IDs, names, and descriptions
    """
    try:
        # Search topics table
        sql_query = f"""
            SELECT id, name, description FROM {SYNAPSE_TOPICS_TABLE_ID}
            WHERE name LIKE '%{search_text}%' 
               OR description LIKE '%{search_text}%'
            LIMIT {max_results}
        """

        result = await query_table_impl(
            sql_query=sql_query,
            max_wait_seconds=30
        )

        if result.get("success"):
            topics = []
            for row in result.get("rows", []):
                values = row.get("values", [])
                if len(values) >= 3:
                    topics.append({
                        "id": values[0],
                        "name": values[1],
                        "description": values[2] if values[2] else "No description available"
                    })

            return {
                "success": True,
                "search_text": search_text,
                "topics": topics,
                "total_results": len(topics),
                "table_id": SYNAPSE_TOPICS_TABLE_ID
            }
        else:
            return result

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to search topics: {str(e)}"
        }


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
        "project_url": f"https://www.synapse.org/#!Synapse:{SYNAPSE_PROJECT_ID}",
        "topics_table_id": SYNAPSE_TOPICS_TABLE_ID
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


@mcp.tool
async def search_with_variations(
    search_text: str,
    search_variations: list[str],
    columns_to_search: Optional[list[str]] = None,
    max_results_per_term: int = 5
) -> dict:
    """
    Search for a term using multiple variations and combine results.

    This tool searches for multiple variations of a search term and returns combined,
    deduplicated results. This is useful when you want to search for related terms,
    synonyms, abbreviations, or different forms of a word.

    **When to use this tool:**
    - When a basic search returns no results or too few results
    - To search for synonyms or related terms (e.g., "waveform", "audio", "signal", "ECG")
    - To search for both abbreviations and full forms (e.g., "FHIR", "Fast Healthcare Interoperability Resources")
    - To search for singular/plural forms or spelling variations

    **Agent Instructions:**
    If the initial `search_standards` call returns no results or insufficient results,
    you should:
    1. Generate relevant variations based on the biomedical data science context
    2. For medical/technical terms, consider: synonyms, abbreviations, related concepts, file formats
    3. For example, if searching "waveform": try ["waveform", "audio", "wave", "signal", "time-series", "ECG", "EEG"]
    4. Use this tool with the generated variations
    5. Explain to the user that you're expanding the search to related terms

    Args:
        search_text: The primary search term (should also be in search_variations)
        search_variations: List of all search terms to try (including the original)
        columns_to_search: List of column names to search (default: ["name", "description"])
        max_results_per_term: Maximum results per search term (default: 5)

    Returns:
        Combined search results from all variations, with each result tagged by which term matched it
    """
    return await search_with_variations_impl(
        search_text, search_variations, columns_to_search, max_results_per_term
    )


@mcp.tool
async def search_by_topic(
    topic_name: str,
    max_results: int = 20
) -> dict:
    """
    Search for standards by data topic name.

    This tool allows searching for standards based on the type of data they concern.
    For example, you can search for standards related to "EHR", "Genomics", "Clinical Observations",
    "Image", etc.

    **When to use this tool:**
    - When the user asks about standards for a specific type of data or domain
    - When you want to find standards by their subject area rather than by name
    - To discover what standards are available for a particular data type

    **Agent Instructions:**
    If a user asks about standards for a particular domain (e.g., "What standards are for genomic data?"),
    you should:
    1. First try calling `list_topics` to see available topics
    2. Identify the most relevant topic name
    3. Call this tool with that topic name
    4. If the topic isn't found, the error message will suggest using `list_topics`

    Examples:
    - "EHR" - finds standards for electronic health records
    - "Genomics" - finds standards for genomic data
    - "Image" - finds standards for imaging data
    - "Clinical" - finds standards for clinical observations

    Args:
        topic_name: The topic name to search for (case-insensitive)
        max_results: Maximum number of results to return (default: 20)

    Returns:
        Standards that concern the specified data topic
    """
    return await search_by_topic_impl(topic_name, max_results)


@mcp.tool
async def list_topics() -> dict:
    """
    List all available data topics.

    This tool returns all data topics from the Bridge2AI DataTopics table, including
    their IDs, names, and descriptions. Use this to discover what topics are available
    for searching with the `search_by_topic` tool.

    **When to use this tool:**
    - When the user wants to know what data domains/types are covered
    - Before using `search_by_topic` to find the correct topic name
    - To help users understand how standards are categorized

    Returns:
        List of all available data topics with their IDs, names, and descriptions
    """
    return await list_topics_impl()


@mcp.tool
async def search_topics(
    search_text: str,
    max_results: int = 20
) -> dict:
    """
    Search for data topics by name or description.

    This tool searches the DataTopics table to find topics that match the search text.
    It searches both the topic names and descriptions, making it useful for discovering
    relevant data domains.

    **When to use this tool:**
    - When the user wants to find topics related to a specific term
    - To discover what data domains are available for a particular concept
    - Before using `search_by_topic` to find the exact topic name
    - When exploring what kinds of data are covered in the standards

    **Agent Instructions:**
    Use this tool when the user asks about topics or data domains, such as:
    - "What topics are related to genetics?"
    - "Are there topics about medical imaging?"
    - "Show me topics about patient data"

    The results can then be used with `search_by_topic` to find standards for those topics.

    Examples:
    - "genetic" - finds topics like Gene, Genome, Genomics
    - "patient" - finds topics like Clinical Observations, EHR, Demographics
    - "image" - finds topics like Image, Radiology
    - "time" - finds topics like Waveform, Time Series

    Args:
        search_text: The text to search for in topic names and descriptions
        max_results: Maximum number of results to return (default: 20)

    Returns:
        List of matching topics with their IDs, names, and descriptions
    """
    return await search_topics_impl(search_text, max_results)


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
