"""
Example demonstrating topic-based search functionality.

Usage:
    # List all available topics
    uv run python tests/example_topic_search.py --list
    
    # Search by specific topic
    uv run python tests/example_topic_search.py --topic "EHR"
    uv run python tests/example_topic_search.py --topic "Genomics"
    
    # Show how regular search now includes topics
    uv run python tests/example_topic_search.py --demo
"""

import asyncio
import sys
from fastmcp import Client
from standards_explorer_mcp.main import mcp


async def list_all_topics():
    """List all available data topics."""
    print("="*70)
    print("All Available Data Topics")
    print("="*70)

    async with Client(mcp) as client:
        results = await client.call_tool("list_topics", {})

        if results.data['success']:
            topics = results.data['topics']
            print(f"\n✅ Found {len(topics)} topics\n")

            for topic in topics:
                print(f"• {topic['name']} ({topic['id']})")
                desc = topic['description'][:100] + \
                    "..." if len(topic['description']
                                 ) > 100 else topic['description']
                print(f"  {desc}")
                print()
        else:
            print(f"❌ Error: {results.data.get('error')}")


async def search_by_topic_example(topic_name: str):
    """Search for standards by topic name."""
    print("="*70)
    print(f"Searching for standards about: {topic_name}")
    print("="*70)

    async with Client(mcp) as client:
        results = await client.call_tool(
            "search_by_topic",
            {
                "topic_name": topic_name,
                "max_results": 15
            }
        )

        if results.data['success']:
            topic_id = results.data['topic_id']
            matched_name = results.data['topic_name']

            print(f"\n✅ Topic: {matched_name} ({topic_id})")
            print(f"📊 Found {results.data['row_count']} standards\n")

            for i, row in enumerate(results.data['rows'][:10], 1):
                values = row['values']
                if len(values) >= 3:
                    name = values[2]
                    row_id = values[0]
                    description = values[3] if len(
                        values) > 3 and values[3] else "No description"
                    topics = values[8] if len(values) > 8 else []

                    print(f"{i}. {name}")
                    print(f"   ID: {row_id}")
                    print(f"   Topics: {topics}")
                    if description != "No description":
                        desc_short = description[:80] + \
                            "..." if len(description) > 80 else description
                        print(f"   Description: {desc_short}")
                    print()
        else:
            print(f"\n❌ Error: {results.data.get('error')}")
            if results.data.get('suggestion'):
                print(f"💡 {results.data['suggestion']}")


async def demo_integrated_search():
    """Demonstrate how regular search now includes topic matching."""
    print("="*70)
    print("Demo: Integrated Topic Search")
    print("="*70)

    async with Client(mcp) as client:
        # Example 1: Searching for a term that IS a topic name
        print("\n1️⃣  Searching for 'EHR' (which is a topic name)")
        print("-"*70)

        results1 = await client.call_tool(
            "search_standards",
            {
                "search_text": "EHR",
                "max_results": 5
            }
        )

        if results1.data['success']:
            print(f"\n✅ Found {results1.data['row_count']} results")

            if results1.data.get('also_searched_topic'):
                topic_info = results1.data['also_searched_topic']
                print(
                    f"🎯 Bonus: Also searched by topic {topic_info['topic_name']} ({topic_info['topic_id']})")
                print("   This means results include both:")
                print("   - Standards with 'EHR' in their name/description")
                print("   - Standards tagged with the EHR data topic")

            print(f"\nTop 5 results:")
            for i, row in enumerate(results1.data['rows'][:5], 1):
                values = row['values']
                print(f"  {i}. {values[2]} (ID: {values[0]})")

        # Example 2: Searching for a term that is NOT a topic name
        print("\n\n2️⃣  Searching for 'FHIR' (not a topic name)")
        print("-"*70)

        results2 = await client.call_tool(
            "search_standards",
            {
                "search_text": "FHIR",
                "max_results": 5
            }
        )

        if results2.data['success']:
            print(f"\n✅ Found {results2.data['row_count']} results")

            if results2.data.get('also_searched_topic'):
                topic_info = results2.data['also_searched_topic']
                print(
                    f"🎯 Bonus: Also searched by topic {topic_info['topic_name']}")
            else:
                print("ℹ️  No matching topic - searched text fields only")

            print(f"\nTop 5 results:")
            for i, row in enumerate(results2.data['rows'][:5], 1):
                values = row['values']
                print(f"  {i}. {values[2]} (ID: {values[0]})")

        # Example 3: Direct topic search for comparison
        print("\n\n3️⃣  Direct topic search: search_by_topic('Clinical Observations')")
        print("-"*70)

        results3 = await client.call_tool(
            "search_by_topic",
            {
                "topic_name": "Clinical Observations",
                "max_results": 5
            }
        )

        if results3.data['success']:
            print(f"\n✅ Found {results3.data['row_count']} standards")
            print(
                f"📊 Topic: {results3.data['topic_name']} ({results3.data['topic_id']})")

            print(f"\nTop 5 results:")
            for i, row in enumerate(results3.data['rows'][:5], 1):
                values = row['values']
                print(f"  {i}. {values[2]} (ID: {values[0]})")


async def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            await list_all_topics()
        elif sys.argv[1] == "--topic" and len(sys.argv) > 2:
            topic_name = " ".join(sys.argv[2:])
            await search_by_topic_example(topic_name)
        elif sys.argv[1] == "--demo":
            await demo_integrated_search()
        else:
            print(__doc__)
    else:
        # Run demo by default
        await demo_integrated_search()


if __name__ == "__main__":
    asyncio.run(main())
