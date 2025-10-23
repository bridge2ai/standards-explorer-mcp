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
    # For example, in another terminal: uv run standards-explorer-mcp

    async with Client("standards-explorer-mcp") as client:
        # Get table information
        print("\n1. Getting Bridge2AI Standards Explorer table information...")
        info = await client.call_tool(name="get_standards_table_info")
        print(f"\nTable ID: {info['table_id']}")
        print(f"Project ID: {info['project_id']}")
        print(f"Synapse URL: {info['synapse_url']}")

        # Execute a SQL query
        print("\n" + "=" * 70)
        print("2. Querying for 'FHIR' standards using SQL...")
        results = await client.call_tool(
            name="query_table",
            arguments={
                "sql_query": "SELECT id, name, description FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 3"
            }
        )

        if results.get('success'):
            print(f"\nFound {results['row_count']} rows")
            print(f"Columns: {[col['name'] for col in results['columns']]}\n")

            for i, row in enumerate(results['rows'], 1):
                values = row['values']
                print(f"{i}. {values[1]}")  # name
                print(f"   ID: {values[0]}")  # id
                if len(values) > 2 and values[2]:
                    desc = values[2]
                    print(f"   Description: {desc[:80]}...")
                print()
        else:
            print(f"Query failed: {results.get('error')}")

        # Search for text across columns
        print("=" * 70)
        print("3. Searching for 'metadata' in name and description...")
        results = await client.call_tool(
            name="search_standards",
            arguments={
                "search_text": "metadata",
                "max_results": 3
            }
        )

        if results.get('success'):
            print(f"\nFound {results['row_count']} rows")
            print(f"Searched columns: {results['searched_columns']}\n")

            for i, row in enumerate(results['rows'], 1):
                values = row['values']
                # Assuming first few columns are id, category, name
                # name
                print(f"{i}. {values[2] if len(values) > 2 else 'N/A'}")
                # id
                print(f"   ID: {values[0] if len(values) > 0 else 'N/A'}")
                print()
        else:
            print(f"Search failed: {results.get('error')}")

        # Paginated search
        print("=" * 70)
        print("4. Demonstrating pagination with SQL...")

        page1 = await client.call_tool(
            name="query_table",
            arguments={
                "sql_query": "SELECT id, name FROM syn63096833 WHERE description LIKE '%standard%' LIMIT 2 OFFSET 0"
            }
        )

        page2 = await client.call_tool(
            name="query_table",
            arguments={
                "sql_query": "SELECT id, name FROM syn63096833 WHERE description LIKE '%standard%' LIMIT 2 OFFSET 2"
            }
        )

        if page1.get('success') and page2.get('success'):
            print(f"\nPage 1 (results 1-2):")
            for row in page1['rows']:
                values = row['values']
                print(f"  - {values[1]} ({values[0]})")  # name (id)

            print(f"\nPage 2 (results 3-4):")
            for row in page2['rows']:
                values = row['values']
                print(f"  - {values[1]} ({values[0]})")  # name (id)

    print("\n" + "=" * 70)
    print("Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
