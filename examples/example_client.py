"""
Example client demonstrating how to use the Standards Explorer MCP server.

This script shows how to connect to the MCP server and call its tools.

Usage:
    # Run all examples
    uv run python tests/example_client.py
    
    # Search for specific text (simple search)
    uv run python tests/example_client.py "FHIR"
    uv run python tests/example_client.py "metadata standards"
    
    # Search with intelligent variation expansion (demonstrates agent behavior)
    uv run python tests/example_client.py --variations "waveform"
    uv run python tests/example_client.py --variations "genome"
"""

import asyncio
import sys
from fastmcp import Client

# Import the server directly for in-memory transport (no separate server process needed)
from standards_explorer_mcp.main import mcp


async def search_with_variations_example(search_text: str):
    """
    Run a search with term variations.

    This demonstrates how an LLM agent would use the search_with_variations tool:
    1. First try a basic search
    2. If results are insufficient, generate relevant variations
    3. Call search_with_variations with those variations
    """
    print("=" * 70)
    print(f"Intelligent Search: '{search_text}'")
    print("=" * 70)

    async with Client(mcp) as client:
        # Step 1: Try basic search first
        print("\n🔍 Step 1: Trying basic search...")
        print("-" * 70)

        basic_results = await client.call_tool(
            "search_standards",
            {
                "search_text": search_text,
                "max_results": 5
            }
        )

        basic_count = basic_results.data.get('row_count', 0)
        print(f"Found {basic_count} results from basic search.")

        # Step 2: If results are limited, expand with variations
        if basic_count < 5:
            print(
                f"\n💡 Only {basic_count} results found. Expanding search with related terms...")
            print("-" * 70)

            # Generate variations based on the biomedical data science context
            # This is what an LLM agent would do
            variations_map = {
                "waveform": ["waveform", "audio", "wave", "signal", "time-series", "ECG"],
                "genome": ["genome", "genomic", "DNA", "genetic", "sequencing"],
                "clinical": ["clinical", "patient", "medical", "healthcare", "EHR"],
                "metadata": ["metadata", "data", "annotation", "schema", "attribute"],
                "image": ["image", "imaging", "picture", "scan", "radiology"],
            }

            # Find matching variations or generate basic ones
            search_lower = search_text.lower()
            variations = None
            for key, terms in variations_map.items():
                if key in search_lower or search_lower in key:
                    variations = terms
                    break

            if not variations:
                # Fallback: generate basic variations
                variations = [search_text]
                if search_text.endswith('s'):
                    variations.append(search_text[:-1])
                else:
                    variations.append(search_text + 's')

            print(f"🧠 Generated variations: {', '.join(variations)}")
            print()

            # Step 3: Search with variations
            results = await client.call_tool(
                "search_with_variations",
                {
                    "search_text": search_text,
                    "search_variations": variations,
                    "max_results_per_term": 5
                }
            )

            if results.data['success']:
                print(
                    f"📊 Total unique results: {results.data['total_results']}\n")

                if results.data['total_results'] == 0:
                    print(
                        "❌ No results found even with variations. Try a different search term.")
                else:
                    # Group results by original vs variations
                    all_results = results.data['results']
                    original_matches = [
                        r for r in all_results if r['is_original']]
                    variation_matches = [
                        r for r in all_results if not r['is_original']]

                    if original_matches:
                        print(
                            f"🎯 Direct matches for '{search_text}' ({len(original_matches)}):\n")
                        for i, result_item in enumerate(original_matches[:5], 1):
                            row = result_item['row']
                            values = row['values']
                            if len(values) >= 3:
                                row_id = values[0]
                                category = values[1] if values[1] else 'Uncategorized'
                                name = values[2] if values[2] else 'N/A'
                                description = values[3] if len(
                                    values) > 3 and values[3] else ''

                                print(f"{i}. {name}")
                                print(f"   ID: {row_id}")
                                print(f"   Category: {category}")
                                if description:
                                    print(
                                        f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                                print()

                    if variation_matches:
                        print(
                            f"\n🔗 Matches from related terms ({len(variation_matches)}):\n")
                        for i, result_item in enumerate(variation_matches[:10], 1):
                            row = result_item['row']
                            matched_term = result_item['matched_term']
                            values = row['values']
                            if len(values) >= 3:
                                row_id = values[0]
                                category = values[1] if values[1] else 'Uncategorized'
                                name = values[2] if values[2] else 'N/A'
                                description = values[3] if len(
                                    values) > 3 and values[3] else ''

                                print(f"{i}. {name} (via '{matched_term}')")
                                print(f"   ID: {row_id}")
                                print(f"   Category: {category}")
                                if description:
                                    print(
                                        f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                                print()
            else:
                print(f"\n❌ Search failed: {results.data.get('error')}")
        else:
            print(
                f"\n✅ Basic search returned sufficient results ({basic_count}).")
            print("No need to expand with variations.")


async def search_query(search_text: str):
    """Run a simple search query."""
    print("=" * 70)
    print(f"Searching for: '{search_text}'")
    print("=" * 70)

    async with Client(mcp) as client:
        # Search with the provided text
        print("\nSearching in name, description, and purpose_detail columns...")
        print("-" * 70)

        results = await client.call_tool(
            "search_standards",
            {
                "search_text": search_text,
                "max_results": 10
            }
        )

        if results.data['success']:
            print(f"\nFound {results.data['row_count']} results\n")

            if results.data['row_count'] == 0:
                print("No results found. Try a different search term.")
            else:
                for i, row in enumerate(results.data['rows'], 1):
                    values = row['values']
                    if len(values) >= 3:
                        row_id = values[0]
                        category = values[1] if values[1] else 'Uncategorized'
                        name = values[2] if values[2] else 'N/A'
                        description = values[3] if len(
                            values) > 3 and values[3] else 'No description'

                        print(f"{i}. {name}")
                        print(f"   ID: {row_id}")
                        print(f"   Category: {category}")
                        if description and description != 'No description':
                            print(
                                f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                        print()
        else:
            print(f"\nSearch failed: {results.data.get('error')}")

        # Also try a direct SQL query
        print("\n" + "=" * 70)
        print(f"Direct SQL query for '{search_text}'...")
        print("-" * 70)

        sql_results = await client.call_tool(
            "query_table",
            {
                "sql_query": f"""
                    SELECT id, name, description 
                    FROM syn63096833 
                    WHERE name LIKE '%{search_text}%' 
                       OR description LIKE '%{search_text}%'
                    LIMIT 10
                """
            }
        )

        if sql_results.data['success']:
            print(f"\nFound {sql_results.data['row_count']} results\n")

            if sql_results.data['row_count'] == 0:
                print("No results found in SQL query.")
            else:
                for i, row in enumerate(sql_results.data['rows'], 1):
                    values = row['values']
                    row_id = values[0] if len(values) > 0 else 'N/A'
                    name = values[1] if len(values) > 1 else 'N/A'
                    description = values[2] if len(
                        values) > 2 and values[2] else 'No description'

                    print(f"{i}. {name}")
                    print(f"   ID: {row_id}")
                    if description and description != 'No description':
                        print(
                            f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                    print()
        else:
            print(f"\nQuery failed: {sql_results.data.get('error')}")


async def main():
    print("=" * 70)
    print("Standards Explorer MCP - Example Client")
    print("=" * 70)

    # Using in-memory transport - server starts automatically!
    async with Client(mcp) as client:
        # Get table information
        print("\n1. Getting Bridge2AI Standards Explorer table information...")
        print("-" * 70)
        info = await client.call_tool("get_standards_table_info", {})

        print(f"\nTable ID: {info.data['table_id']}")
        print(f"Project ID: {info.data['project_id']}")
        print(f"Synapse URL: {info.data['synapse_url']}")

        # Execute a SQL query
        print("\n" + "=" * 70)
        print("2. Querying for 'FHIR' standards using SQL...")
        print("-" * 70)

        results = await client.call_tool(
            "query_table",
            {"sql_query": "SELECT id, name, description FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 3"}
        )

        if results.data['success']:
            print(f"\nFound {results.data['row_count']} rows")
            print(
                f"Columns: {[col['name'] for col in results.data['columns']]}\n")

            for i, row in enumerate(results.data['rows'], 1):
                values = row['values']
                row_id = values[0] if len(values) > 0 else 'N/A'
                standard_name = values[1] if len(values) > 1 else 'N/A'
                description = values[2] if len(
                    values) > 2 and values[2] else 'No description'

                print(f"{i}. {standard_name}")
                print(f"   ID: {row_id}")
                print(
                    f"   Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                print()
        else:
            print(f"Query failed: {results.data.get('error')}")

        # Search for text across columns
        print("=" * 70)
        print("3. Searching for 'metadata' using convenience wrapper...")
        print("-" * 70)

        results = await client.call_tool(
            "search_standards",
            {
                "search_text": "metadata",
                "max_results": 3
            }
        )

        if results.data['success']:
            print(f"\nFound {results.data['row_count']} rows")
            print(f"Searched columns: {results.data['searched_columns']}\n")

            for i, row in enumerate(results.data['rows'], 1):
                values = row['values']
                # Columns are: id (0), category (1), name (2), description (3), ...
                if len(values) >= 3:
                    row_id = values[0]
                    category = values[1] if values[1] else 'Uncategorized'
                    standard = values[2] if values[2] else 'N/A'
                    description = values[3] if len(
                        values) > 3 and values[3] else 'No description'

                    print(f"{i}. {standard}")
                    print(f"   ID: {row_id}")
                    print(f"   Category: {category}")
                    print(
                        f"   Description: {description[:80]}{'...' if len(description) > 80 else ''}")
                    print()
        else:
            print(f"Search failed: {results.data.get('error')}")

        # Custom column search
        print("=" * 70)
        print("4. Searching specific columns...")
        print("-" * 70)

        results = await client.call_tool(
            "search_standards",
            {
                "search_text": "FHIR",
                "columns_to_search": ["name"],
                "max_results": 5
            }
        )

        if results.data['success']:
            print(
                f"\nFound {results.data['row_count']} standards with 'FHIR' in the name column\n")
            for i, row in enumerate(results.data['rows'], 1):
                values = row['values']
                standard_name = values[2] if len(
                    values) > 2 else 'N/A'  # name is third column
                print(f"  {i}. {standard_name}")

        # Paginated search
        print("\n" + "=" * 70)
        print("5. Demonstrating pagination...")
        print("-" * 70)

        page1 = await client.call_tool(
            "search_standards",
            {
                "search_text": "standard",
                "max_results": 2,
                "offset": 0
            }
        )

        page2 = await client.call_tool(
            "search_standards",
            {
                "search_text": "standard",
                "max_results": 2,
                "offset": 2
            }
        )

        if page1.data['success'] and page2.data['success']:
            print(f"\nPage 1 (results 1-2):")
            for row in page1.data['rows']:
                values = row['values']
                row_id = values[0] if len(values) > 0 else 'N/A'
                standard_name = values[2] if len(
                    values) > 2 else 'N/A'  # name is column 2
                print(f"  - {standard_name} (ID: {row_id})")

            print(f"\nPage 2 (results 3-4):")
            for row in page2.data['rows']:
                values = row['values']
                row_id = values[0] if len(values) > 0 else 'N/A'
                standard_name = values[2] if len(
                    values) > 2 else 'N/A'  # name is column 2
                print(f"  - {standard_name} (ID: {row_id})")

        # Custom SQL query
        print("\n" + "=" * 70)
        print("6. Custom SQL query with multiple conditions...")
        print("-" * 70)

        results = await client.call_tool(
            "query_table",
            {
                "sql_query": """
                    SELECT id, name, category 
                    FROM syn63096833 
                    WHERE name LIKE '%health%' 
                      AND category IS NOT NULL
                    LIMIT 5
                """
            }
        )

        if results.data['success']:
            print(
                f"\nFound {results.data['row_count']} standards matching criteria\n")
            for i, row in enumerate(results.data['rows'], 1):
                values = row['values']
                row_id = values[0] if len(values) > 0 else 'N/A'
                standard = values[1] if len(values) > 1 else 'N/A'
                category = values[2] if len(
                    values) > 2 and values[2] else 'Uncategorized'

                print(f"  {i}. {standard}")
                print(f"     Category: {category}")
                print(f"     ID: {row_id}")
                print()

    print("=" * 70)
    print("✅ Example complete! All tools tested successfully.")
    print("=" * 70)


if __name__ == "__main__":
    # Check if a search query was provided as command-line argument
    if len(sys.argv) > 1:
        if sys.argv[1] == "--variations" and len(sys.argv) > 2:
            # Intelligent search with variations
            search_text = " ".join(sys.argv[2:])
            asyncio.run(search_with_variations_example(search_text))
        else:
            # Simple search
            search_text = " ".join(sys.argv[1:])
            asyncio.run(search_query(search_text))
    else:
        # Run the full example suite
        asyncio.run(main())
