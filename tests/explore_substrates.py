"""Quick script to explore the DataSubstrate table structure."""

import asyncio
from standards_explorer_mcp.main import query_table_impl

async def main():
    print("Querying DataSubstrate table (syn63096834)...")
    print("="*70)
    
    # Query to get all substrates
    result = await query_table_impl(
        sql_query="SELECT * FROM syn63096834 LIMIT 10",
        max_wait_seconds=30
    )
    
    if result.get('success'):
        print(f"\nColumns: {[col['name'] for col in result['columns']]}")
        print(f"Total rows returned: {result['row_count']}\n")
        
        for i, row in enumerate(result['rows'][:5], 1):
            values = row['values']
            print(f"Row {i}:")
            for j, col in enumerate(result['columns']):
                col_name = col['name']
                val = values[j] if j < len(values) else None
                print(f"  {col_name}: {val}")
            print()
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
