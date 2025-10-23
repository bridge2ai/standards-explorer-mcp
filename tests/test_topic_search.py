"""Test script for topic-based search functionality."""

import asyncio
from standards_explorer_mcp.main import list_topics_impl, search_by_topic_impl


async def test_list_topics():
    print("="*70)
    print("Testing list_topics...")
    print("="*70)

    result = await list_topics_impl()

    if result.get('success'):
        print(f"\n✅ Found {result['total_topics']} topics\n")

        # Show first 10 topics
        for topic in result['topics'][:10]:
            print(f"- {topic['name']} ({topic['id']})")
            print(f"  {topic['description'][:80]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_search_by_topic():
    print("\n" + "="*70)
    print("Testing search_by_topic with 'EHR'...")
    print("="*70)

    result = await search_by_topic_impl("EHR", max_results=10)

    if result.get('success'):
        print(
            f"\n✅ Found {result['row_count']} standards for topic '{result['topic_name']}' ({result['topic_id']})\n")

        for i, row in enumerate(result['rows'][:5], 1):
            values = row['values']
            if len(values) >= 3:
                print(f"{i}. {values[2]}")  # name
                print(f"   ID: {values[0]}")
                if len(values) > 8:
                    print(f"   Topics: {values[8]}")  # concerns_data_topic
                print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_search_by_topic_genomics():
    print("\n" + "="*70)
    print("Testing search_by_topic with 'Genomics'...")
    print("="*70)

    result = await search_by_topic_impl("Genomics", max_results=10)

    if result.get('success'):
        print(
            f"\n✅ Found {result['row_count']} standards for topic '{result['topic_name']}' ({result['topic_id']})\n")

        for i, row in enumerate(result['rows'][:5], 1):
            values = row['values']
            if len(values) >= 3:
                print(f"{i}. {values[2]}")  # name
                print(f"   ID: {values[0]}")
                if len(values) > 8:
                    print(f"   Topics: {values[8]}")  # concerns_data_topic
                print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    await test_list_topics()
    await test_search_by_topic()
    await test_search_by_topic_genomics()

    print("="*70)
    print("✅ All tests complete!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
