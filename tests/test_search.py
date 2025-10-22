"""Simple test script to verify the search functionality."""

import asyncio
import httpx


# Direct implementation for testing (without FastMCP wrapper)
SYNAPSE_BASE_URL = "https://repo-prod.prod.sagebase.org"
SYNAPSE_TABLE_ID = "syn63096833"
SYNAPSE_PROJECT_ID = "syn63096806"


async def search_standards(query: str, max_results: int = 10, offset: int = 0) -> dict:
    """Search for standards from the Bridge2AI Standards Explorer table."""
    try:
        search_payload = {
            "queryTerm": [query],
            "start": offset,
            "size": max_results,
        }
        
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


async def get_standards_table_info() -> dict:
    """Get information about the Bridge2AI Standards Explorer table."""
    return {
        "table_id": SYNAPSE_TABLE_ID,
        "table_name": "Bridge2AI Standards Explorer Table",
        "project_id": SYNAPSE_PROJECT_ID,
        "project_name": "Bridge2AI Standards Explorer",
        "description": "This table contains standards information from the Bridge2AI Standards Explorer",
        "synapse_url": f"https://www.synapse.org/#!Synapse:{SYNAPSE_TABLE_ID}",
        "project_url": f"https://www.synapse.org/#!Synapse:{SYNAPSE_PROJECT_ID}"
    }


async def main():
    print("=" * 60)
    print("Testing Bridge2AI Standards Explorer MCP")
    print("=" * 60)
    
    # Test 1: Get table info
    print("\n1. Getting table information...")
    info = await get_standards_table_info()
    print(f"Table ID: {info['table_id']}")
    print(f"Project ID: {info['project_id']}")
    print(f"Table URL: {info['synapse_url']}")
    
    # Test 2: Search for standards
    print("\n2. Searching for 'metadata' standards...")
    results = await search_standards(query="metadata", max_results=3)
    
    if results['success']:
        print(f"Success! Found {results['total_results']} total results")
        print(f"Returned {results['returned_results']} results")
        print("\nResults:")
        for i, hit in enumerate(results['hits'], 1):
            print(f"\n  {i}. {hit.get('name', 'N/A')}")
            print(f"     ID: {hit.get('id', 'N/A')}")
            if 'description' in hit:
                desc = hit['description']
                print(f"     Description: {desc[:100]}..." if len(desc) > 100 else f"     Description: {desc}")
    else:
        print(f"Search failed: {results.get('error', 'Unknown error')}")
        if 'details' in results:
            print(f"Details: {results['details']}")
    
    # Test 3: Try another search
    print("\n3. Searching for 'FHIR' standards...")
    results2 = await search_standards(query="FHIR", max_results=2)
    
    if results2['success']:
        print(f"Success! Found {results2['total_results']} total results")
        print(f"Returned {results2['returned_results']} results")
    else:
        print(f"Search failed: {results2.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
