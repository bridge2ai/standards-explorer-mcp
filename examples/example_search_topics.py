"""
Example demonstrating search_topics functionality through MCP.

Usage:
    uv run python tests/example_search_topics.py "genetic"
    uv run python tests/example_search_topics.py "patient"
    uv run python tests/example_search_topics.py "time series"
"""

import asyncio
import sys
from fastmcp import Client
from standards_explorer_mcp.main import mcp


async def search_topics_demo(search_text: str):
    """Demonstrate searching for topics by keyword."""
    print("="*70)
    print(f"Searching for topics matching: '{search_text}'")
    print("="*70)

    async with Client(mcp) as client:
        results = await client.call_tool(
            "search_topics",
            {
                "search_text": search_text,
                "max_results": 20
            }
        )

        if results.data['success']:
            topics = results.data['topics']
            print(f"\n✅ Found {len(topics)} matching topics\n")

            if len(topics) == 0:
                print("No topics found. Try a different search term.")
            else:
                for topic in topics:
                    print(f"• {topic['name']} ({topic['id']})")
                    desc = topic['description']
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    print(f"  {desc}")
                    print()

                # Show example of using first topic with search_by_topic
                if len(topics) > 0:
                    first_topic = topics[0]['name']
                    print(
                        f"\n💡 Tip: You can now search for standards using this topic:")
                    print(f"   search_by_topic('{first_topic}')")
        else:
            print(f"\n❌ Error: {results.data.get('error')}")


async def demo_workflow():
    """Demonstrate the typical workflow: search topics -> search standards."""
    print("="*70)
    print("Demo: Topic Search → Standards Search Workflow")
    print("="*70)

    async with Client(mcp) as client:
        # Step 1: Search for topics
        print("\n1️⃣  Step 1: Find topics related to 'imaging'")
        print("-"*70)

        topic_results = await client.call_tool(
            "search_topics",
            {
                "search_text": "imaging",
                "max_results": 5
            }
        )

        if topic_results.data['success']:
            topics = topic_results.data['topics']
            print(f"\n✅ Found {len(topics)} topics:\n")

            for i, topic in enumerate(topics, 1):
                print(f"{i}. {topic['name']} ({topic['id']})")

            # Step 2: Use first topic to search for standards
            if len(topics) > 0:
                first_topic = topics[0]['name']
                print(
                    f"\n\n2️⃣  Step 2: Search for standards about '{first_topic}'")
                print("-"*70)

                standards_results = await client.call_tool(
                    "search_by_topic",
                    {
                        "topic_name": first_topic,
                        "max_results": 5
                    }
                )

                if standards_results.data['success']:
                    print(
                        f"\n✅ Found {standards_results.data['row_count']} standards\n")

                    for i, row in enumerate(standards_results.data['rows'][:5], 1):
                        values = row['values']
                        print(f"{i}. {values[2]} (ID: {values[0]})")


async def main():
    if len(sys.argv) > 1:
        search_text = " ".join(sys.argv[1:])
        await search_topics_demo(search_text)
    else:
        # Run demo workflow
        await demo_workflow()


if __name__ == "__main__":
    asyncio.run(main())
