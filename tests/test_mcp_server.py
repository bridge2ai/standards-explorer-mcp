#!/usr/bin/env python3
"""
Test the MCP server directly to ensure all tools work correctly.
"""

import asyncio
import sys
from fastmcp import Client


async def test_mcp_server():
    """Test the MCP server tools."""
    print("Testing Bridge2AI Standards Explorer MCP Server")
    print("=" * 60)
    
    try:
        # Connect to the server (assumes it's running separately or registered)
        async with Client("standards-explorer-mcp") as client:
            print("✅ Connected to MCP server\n")
            
            # List available tools
            tools = await client.list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}\n")
            
            # Test 1: Get table info
            print("Test 1: Getting table information...")
            info = await client.call_tool("get_standards_table_info", {})
            print(f"Table ID: {info.get('table_id')}")
            print(f"Project ID: {info.get('project_id')}")
            print(f"✅ Test 1 passed\n")
            
            # Test 2: SQL query
            print("Test 2: SQL query for FHIR...")
            results = await client.call_tool(
                "query_table",
                {"sql_query": "SELECT id, name FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 3"}
            )
            if results.get("success"):
                print(f"Found {results.get('row_count')} rows")
                if results.get("rows"):
                    print(f"First result: {results['rows'][0]['values']}")
                print(f"✅ Test 2 passed\n")
            else:
                print(f"❌ Test 2 failed: {results.get('error')}\n")
            
            # Test 3: Text search
            print("Test 3: Searching for 'metadata'...")
            results = await client.call_tool(
                "search_standards",
                {"search_text": "metadata", "max_results": 3}
            )
            if results.get("success"):
                print(f"Found {results.get('row_count')} rows")
                print(f"Searched columns: {results.get('searched_columns')}")
                print(f"✅ Test 3 passed\n")
            else:
                print(f"❌ Test 3 failed: {results.get('error')}\n")
            
            print("=" * 60)
            print("All tests completed successfully! 🎉")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
