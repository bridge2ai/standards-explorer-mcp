"""Quick script to see how topics are referenced in the standards table."""

import asyncio
from standards_explorer_mcp.main import query_table_impl


async def main():
    print("Querying standards with topics...")
    print("="*70)

    # Query to get standards with their topics
    result = await query_table_impl(
        sql_query="SELECT id, name, concerns_data_topic FROM syn63096833 WHERE concerns_data_topic IS NOT NULL LIMIT 10",
        max_wait_seconds=30
    )

    if result.get('success'):
        print(f"\nColumns: {[col['name'] for col in result['columns']]}")
        print(f"Total rows returned: {result['row_count']}\n")

        for i, row in enumerate(result['rows'], 1):
            values = row['values']
            print(f"{i}. {values[1]}")  # name
            print(f"   ID: {values[0]}")
            print(f"   Topics: {values[2]}")
            print()
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
