"""
Tests for direct Synapse API endpoint functionality.

These tests verify that we can successfully query the Synapse Table Query API
without going through the MCP server layer.
"""

import pytest
import httpx
import asyncio
import os


SYNAPSE_BASE_URL = "https://repo-prod.prod.sagebase.org"
SYNAPSE_TABLE_ID = "syn63096833"


def get_auth_header():
    """Get authentication header if token is available."""
    token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


async def poll_async_job(client, table_id, async_token, max_wait=30):
    """Poll an async job until it completes or times out."""
    url = f"{SYNAPSE_BASE_URL}/repo/v1/entity/{table_id}/table/query/async/get/{async_token}"
    headers = {
        "Content-Type": "application/json",
        **get_auth_header()
    }

    start_time = asyncio.get_event_loop().time()

    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Query timed out after {max_wait} seconds")

        response = await client.get(url, headers=headers)

        if response.status_code == 202:
            await asyncio.sleep(1)
            continue

        response.raise_for_status()
        return response.json()


async def execute_query(sql_query):
    """Execute a SQL query against the Synapse table."""
    query_request = {
        "concreteType": "org.sagebionetworks.repo.model.table.QueryBundleRequest",
        "entityId": SYNAPSE_TABLE_ID,
        "query": {
            "sql": sql_query
        },
        "partMask": 0x1 | 0x4 | 0x10
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {
            "Content-Type": "application/json",
            **get_auth_header()
        }

        start_response = await client.post(
            f"{SYNAPSE_BASE_URL}/repo/v1/entity/{SYNAPSE_TABLE_ID}/table/query/async/start",
            json=query_request,
            headers=headers
        )
        start_response.raise_for_status()

        job_info = start_response.json()
        async_token = job_info.get("token")

        result_bundle = await poll_async_job(client, SYNAPSE_TABLE_ID, async_token)
        return result_bundle


@pytest.mark.asyncio
async def test_simple_select():
    """Test a simple SELECT query with LIMIT."""
    result = await execute_query(f"SELECT * FROM {SYNAPSE_TABLE_ID} LIMIT 5")

    assert result is not None
    query_result = result.get("queryResult", {})
    rows = query_result.get("queryResults", {}).get("rows", [])

    assert len(rows) == 5, f"Expected 5 rows, got {len(rows)}"
    assert len(rows[0]["values"]) > 0, "Row should have values"


@pytest.mark.asyncio
async def test_search_fhir():
    """Test searching for FHIR in the name column."""
    result = await execute_query(
        f"SELECT id, name FROM {SYNAPSE_TABLE_ID} WHERE name LIKE '%FHIR%' LIMIT 10"
    )

    query_result = result.get("queryResult", {})
    rows = query_result.get("queryResults", {}).get("rows", [])

    assert len(rows) > 0, "Should find at least one FHIR-related standard"

    # Verify that results contain FHIR in the name
    for row in rows:
        name = row["values"][1]  # name is second column
        assert "FHIR" in name.upper(), f"Expected FHIR in name, got: {name}"


@pytest.mark.asyncio
async def test_search_metadata():
    """Test searching for metadata in the description column."""
    result = await execute_query(
        f"SELECT id, name, description FROM {SYNAPSE_TABLE_ID} WHERE description LIKE '%metadata%' LIMIT 5"
    )

    query_result = result.get("queryResult", {})
    rows = query_result.get("queryResults", {}).get("rows", [])

    assert len(
        rows) > 0, "Should find at least one result with 'metadata' in description"

    # Verify columns
    select_columns = result.get("selectColumns", [])
    column_names = [col.get("name") for col in select_columns]
    assert "id" in column_names
    assert "name" in column_names
    assert "description" in column_names


@pytest.mark.asyncio
async def test_pagination():
    """Test pagination with OFFSET."""
    # Get first page
    result1 = await execute_query(
        f"SELECT id, name FROM {SYNAPSE_TABLE_ID} LIMIT 3 OFFSET 0"
    )
    rows1 = result1.get("queryResult", {}).get(
        "queryResults", {}).get("rows", [])

    # Get second page
    result2 = await execute_query(
        f"SELECT id, name FROM {SYNAPSE_TABLE_ID} LIMIT 3 OFFSET 3"
    )
    rows2 = result2.get("queryResult", {}).get(
        "queryResults", {}).get("rows", [])

    assert len(rows1) == 3, f"Expected 3 rows in first page, got {len(rows1)}"
    assert len(rows2) == 3, f"Expected 3 rows in second page, got {len(rows2)}"

    # Verify pages are different
    ids1 = [row["values"][0] for row in rows1]
    ids2 = [row["values"][0] for row in rows2]
    assert len(set(ids1) & set(ids2)
               ) == 0, "Pages should not have overlapping IDs"


@pytest.mark.asyncio
async def test_column_selection():
    """Test selecting specific columns."""
    result = await execute_query(
        f"SELECT id, name, category FROM {SYNAPSE_TABLE_ID} LIMIT 2"
    )

    select_columns = result.get("selectColumns", [])
    column_names = [col.get("name") for col in select_columns]

    assert len(
        column_names) == 3, f"Expected 3 columns, got {len(column_names)}"
    assert "id" in column_names
    assert "name" in column_names
    assert "category" in column_names

    # Verify rows have matching number of values
    rows = result.get("queryResult", {}).get(
        "queryResults", {}).get("rows", [])
    for row in rows:
        assert len(
            row["values"]) == 3, f"Expected 3 values per row, got {len(row['values'])}"


@pytest.mark.asyncio
async def test_multiple_where_conditions():
    """Test query with multiple WHERE conditions."""
    result = await execute_query(
        f"""SELECT id, name FROM {SYNAPSE_TABLE_ID} 
        WHERE name LIKE '%format%' AND category IS NOT NULL 
        LIMIT 5"""
    )

    query_result = result.get("queryResult", {})
    rows = query_result.get("queryResults", {}).get("rows", [])

    # Should return results (even if 0, query should succeed)
    assert isinstance(rows, list), "Should return a list of rows"
