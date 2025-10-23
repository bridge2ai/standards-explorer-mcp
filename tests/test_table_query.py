#!/usr/bin/env python3
"""
Test script for the table query implementation.
Tests the new async table query endpoints.
"""

import asyncio
import httpx
import os
from datetime import datetime

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
    poll_count = 0
    
    while True:
        elapsed = asyncio.get_event_loop().time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Query timed out after {max_wait} seconds")
        
        poll_count += 1
        response = await client.get(url, headers=headers)
        
        print(f"  Poll #{poll_count}: Status {response.status_code}")
        
        # 202 means still processing
        if response.status_code == 202:
            await asyncio.sleep(1)
            continue
        
        # Any other status
        response.raise_for_status()
        return response.json()


async def test_table_query(sql_query):
    """Test a table query."""
    print(f"\n{'='*60}")
    print(f"Testing query: {sql_query}")
    print(f"{'='*60}")
    
    try:
        query_request = {
            "concreteType": "org.sagebionetworks.repo.model.table.QueryBundleRequest",
            "entityId": SYNAPSE_TABLE_ID,
            "query": {
                "sql": sql_query
            },
            "partMask": 0x1 | 0x4 | 0x10  # queryResults + selectColumns + columnModels
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Content-Type": "application/json",
                **get_auth_header()
            }
            
            print("\nStarting async query...")
            start_response = await client.post(
                f"{SYNAPSE_BASE_URL}/repo/v1/entity/{SYNAPSE_TABLE_ID}/table/query/async/start",
                json=query_request,
                headers=headers
            )
            start_response.raise_for_status()
            
            job_info = start_response.json()
            async_token = job_info.get("token")
            print(f"Got async token: {async_token}")
            
            if not async_token:
                print("ERROR: No async token returned")
                return
            
            print("\nPolling for results...")
            result_bundle = await poll_async_job(client, SYNAPSE_TABLE_ID, async_token)
            
            # Extract information
            query_result = result_bundle.get("queryResult", {})
            query_count = result_bundle.get("queryCount")
            select_columns = result_bundle.get("selectColumns", [])
            rows = query_result.get("queryResults", {}).get("rows", [])
            
            print(f"\n✅ Query completed successfully!")
            print(f"Total matching rows: {query_count}")
            print(f"Rows returned: {len(rows)}")
            print(f"Columns: {[col.get('name') for col in select_columns]}")
            
            if rows:
                print(f"\nFirst row sample:")
                print(f"  {rows[0]}")
            
    except httpx.HTTPStatusError as e:
        print(f"\n❌ HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text[:500]}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


async def main():
    """Run tests."""
    print(f"Testing Synapse Table Query API")
    print(f"Table ID: {SYNAPSE_TABLE_ID}")
    print(f"Base URL: {SYNAPSE_BASE_URL}")
    
    auth_token = os.environ.get("SYNAPSE_AUTH_TOKEN")
    if auth_token:
        print(f"Auth token: Found (length {len(auth_token)})")
    else:
        print("Auth token: Not set (trying without authentication)")
    
    # Test 1: Simple select with limit
    await test_table_query(f"SELECT * FROM {SYNAPSE_TABLE_ID} LIMIT 5")
    
    # Test 2: Search for FHIR
    await test_table_query(f"SELECT * FROM {SYNAPSE_TABLE_ID} WHERE name LIKE '%FHIR%' LIMIT 10")
    
    # Test 3: Search for metadata in description
    await test_table_query(f"SELECT id, name FROM {SYNAPSE_TABLE_ID} WHERE description LIKE '%metadata%' LIMIT 5")
    
    print(f"\n{'='*60}")
    print("All tests completed!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
