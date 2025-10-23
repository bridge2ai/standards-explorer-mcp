"""Test enhanced search that includes topic matching."""

import asyncio
from standards_explorer_mcp.main import search_standards_impl


async def test_search_with_topic_match():
    print("="*70)
    print("Testing search_standards with topic match: 'EHR'")
    print("="*70)

    result = await search_standards_impl("EHR", max_results=15)

    if result.get('success'):
        print(f"\n✅ Found {result['row_count']} results")

        if result.get('also_searched_topic'):
            print(
                f"📊 Also searched by topic: {result['also_searched_topic']['topic_name']} ({result['also_searched_topic']['topic_id']})")

        print(f"\nFirst 10 results:")
        for i, row in enumerate(result['rows'][:10], 1):
            values = row['values']
            if len(values) >= 3:
                name = values[2]
                row_id = values[0]
                topics = values[8] if len(values) > 8 else "N/A"

                print(f"\n{i}. {name}")
                print(f"   ID: {row_id}")
                print(f"   Topics: {topics}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_search_without_topic_match():
    print("\n" + "="*70)
    print("Testing search_standards without topic match: 'FHIR'")
    print("="*70)

    result = await search_standards_impl("FHIR", max_results=10)

    if result.get('success'):
        print(f"\n✅ Found {result['row_count']} results")

        if result.get('also_searched_topic'):
            print(
                f"📊 Also searched by topic: {result['also_searched_topic']['topic_name']} ({result['also_searched_topic']['topic_id']})")
        else:
            print("ℹ️  No matching topic found")

        print(f"\nFirst 5 results:")
        for i, row in enumerate(result['rows'][:5], 1):
            values = row['values']
            if len(values) >= 3:
                name = values[2]
                row_id = values[0]

                print(f"\n{i}. {name}")
                print(f"   ID: {row_id}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    await test_search_with_topic_match()
    await test_search_without_topic_match()

    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
