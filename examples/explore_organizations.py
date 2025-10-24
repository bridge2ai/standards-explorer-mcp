"""Explore the Organizations table structure."""

import asyncio
from standards_explorer_mcp.main import query_table_impl

SYNAPSE_ORGANIZATIONS_TABLE_ID = "syn63096836"


async def explore_organizations_table():
    """Query the Organizations table to understand its structure."""
    
    print("=" * 80)
    print("ORGANIZATIONS TABLE STRUCTURE")
    print("=" * 80)
    print(f"\nTable ID: {SYNAPSE_ORGANIZATIONS_TABLE_ID}")
    
    # Query to get all columns and some sample data
    sql_query = f"SELECT * FROM {SYNAPSE_ORGANIZATIONS_TABLE_ID} LIMIT 10"
    
    result = await query_table_impl(sql_query)
    
    if result.get("success"):
        headers = result.get("headers", [])
        print(f"\nColumns: {[h['name'] for h in headers]}")
        print(f"\nSample organizations (first 10):")
        print("-" * 80)
        
        for row in result.get("rows", []):
            values = row.get("values", [])
            print(f"\nID: {values[0]}")
            print(f"Name: {values[1] if len(values) > 1 else 'N/A'}")
            if len(values) > 2 and values[2]:
                desc = values[2]
                print(f"Description: {desc[:100] if desc else 'N/A'}...")
        
        return result
    else:
        print(f"Error: {result.get('error')}")
        return None


if __name__ == "__main__":
    asyncio.run(explore_organizations_table())
