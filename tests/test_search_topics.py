"""Test script for search_topics functionality."""

import asyncio
from standards_explorer_mcp.main import search_topics_impl


async def test_search_topics():
    print("="*70)
    print("Testing search_topics with 'genetic'")
    print("="*70)

    result = await search_topics_impl("genetic", max_results=10)

    if result.get('success'):
        print(
            f"\n✅ Found {result['total_results']} topics matching 'genetic'\n")

        for topic in result['topics']:
            print(f"• {topic['name']} ({topic['id']})")
            print(f"  {topic['description'][:80]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_search_topics_patient():
    print("\n" + "="*70)
    print("Testing search_topics with 'patient'")
    print("="*70)

    result = await search_topics_impl("patient", max_results=10)

    if result.get('success'):
        print(
            f"\n✅ Found {result['total_results']} topics matching 'patient'\n")

        for topic in result['topics']:
            print(f"• {topic['name']} ({topic['id']})")
            print(f"  {topic['description'][:80]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def test_search_topics_image():
    print("\n" + "="*70)
    print("Testing search_topics with 'image'")
    print("="*70)

    result = await search_topics_impl("image", max_results=10)

    if result.get('success'):
        print(f"\n✅ Found {result['total_results']} topics matching 'image'\n")

        for topic in result['topics']:
            print(f"• {topic['name']} ({topic['id']})")
            print(f"  {topic['description'][:100]}...")
            print()
    else:
        print(f"❌ Error: {result.get('error')}")


async def main():
    await test_search_topics()
    await test_search_topics_patient()
    await test_search_topics_image()

    print("="*70)
    print("✅ All tests complete!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
