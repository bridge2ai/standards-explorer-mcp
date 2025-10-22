"""
Example client demonstrating how to use the Standards Explorer MCP server.

This script shows how to connect to the MCP server and call its tools.
"""

import asyncio
from fastmcp import Client


async def main():
    print("Connecting to Standards Explorer MCP server...")
    print("=" * 70)
    
    # Note: You need to run the server separately before running this client
    # For example, in another terminal: uv run python -m standards_explorer_mcp
    
    async with Client("standards-explorer-mcp") as client:
        # Get table information
        print("\n1. Getting Bridge2AI Standards Explorer table information...")
        info = await client.call_tool(name="get_standards_table_info")
        print(f"\nTable ID: {info['table_id']}")
        print(f"Project ID: {info['project_id']}")
        print(f"Synapse URL: {info['synapse_url']}")
        
        # Search for standards
        print("\n" + "=" * 70)
        print("2. Searching for 'FHIR' standards...")
        results = await client.call_tool(
            name="search_standards",
            arguments={
                "query": "FHIR",
                "max_results": 3
            }
        )
        
        if results.get('success'):
            print(f"\nFound {results['total_results']} total results")
            print(f"Showing {results['returned_results']} results:\n")
            
            for i, hit in enumerate(results['hits'], 1):
                print(f"{i}. {hit.get('name', 'N/A')}")
                print(f"   ID: {hit.get('id', 'N/A')}")
                if 'description' in hit:
                    desc = hit['description']
                    print(f"   Description: {desc[:80]}...")
                print()
        else:
            print(f"Search failed: {results.get('error')}")
        
        # Paginated search
        print("=" * 70)
        print("3. Demonstrating pagination...")
        
        page1 = await client.call_tool(
            name="search_standards",
            arguments={
                "query": "metadata",
                "max_results": 2,
                "offset": 0
            }
        )
        
        page2 = await client.call_tool(
            name="search_standards",
            arguments={
                "query": "metadata",
                "max_results": 2,
                "offset": 2
            }
        )
        
        if page1.get('success') and page2.get('success'):
            print(f"\nTotal results for 'metadata': {page1['total_results']}")
            print(f"\nPage 1 (results 1-2):")
            for hit in page1['hits']:
                print(f"  - {hit.get('name', 'N/A')} ({hit.get('id', 'N/A')})")
            
            print(f"\nPage 2 (results 3-4):")
            for hit in page2['hits']:
                print(f"  - {hit.get('name', 'N/A')} ({hit.get('id', 'N/A')})")
    
    print("\n" + "=" * 70)
    print("Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
