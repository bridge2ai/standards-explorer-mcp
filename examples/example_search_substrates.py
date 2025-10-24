"""Example script demonstrating substrate search functionality."""

import asyncio
from standards_explorer_mcp.main import (
    list_substrates_impl,
    search_substrates_impl,
    search_by_substrate_impl,
    search_standards_impl
)


async def example_substrate_workflow():
    """
    Demonstrate a typical workflow using substrate search functionality.
    """
    print("=" * 80)
    print("SUBSTRATE SEARCH WORKFLOW DEMONSTRATION")
    print("=" * 80)

    # Step 1: List all available substrates
    print("\n1. Listing all available data substrates:")
    print("-" * 80)
    substrates_result = await list_substrates_impl()

    if substrates_result["success"]:
        print(f"Found {substrates_result['total_substrates']} substrates:\n")
        for substrate in substrates_result["substrates"][:5]:  # Show first 5
            print(f"  • {substrate['name']} (ID: {substrate['id']})")
            desc = substrate['description']
            if desc and desc != "No description available":
                print(f"    Description: {desc[:100]}...")
            print()
    else:
        print(f"Error: {substrates_result.get('error')}")

    # Step 2: Search for substrates by keyword
    print("\n2. Searching for substrates related to 'database':")
    print("-" * 80)
    search_result = await search_substrates_impl("database", max_results=5)

    if search_result["success"]:
        print(
            f"Found {len(search_result['substrates'])} matching substrates:\n")
        for substrate in search_result["substrates"]:
            print(f"  • {substrate['name']} (ID: {substrate['id']})")
            print(f"    {substrate['description'][:100]}...")
            print()
    else:
        print(f"Error: {search_result.get('error')}")

    # Step 3: Find standards for a specific substrate
    print("\n3. Finding standards that work with 'Array' substrate:")
    print("-" * 80)
    array_standards = await search_by_substrate_impl("Array", max_results=5)

    if array_standards["success"]:
        print(f"Substrate: {array_standards.get('substrate_name')}")
        print(f"Substrate ID: {array_standards.get('substrate_id')}")
        print(f"Found {len(array_standards.get('rows', []))} standards:\n")

        for row in array_standards.get("rows", [])[:3]:  # Show first 3
            values = row.get("values", [])
            if len(values) >= 2:
                print(f"  • {values[0]}")  # Standard ID
                print(f"    Name: {values[1]}")  # Standard name
                print()
    else:
        print(f"Error: {array_standards.get('error')}")

    # Step 4: Demonstrate enhanced search with substrate matching
    print("\n4. Enhanced search - searching for 'JSON' (matches substrate name):")
    print("-" * 80)
    enhanced_result = await search_standards_impl("JSON", max_results=5)

    if enhanced_result["success"]:
        print(f"Search text: {enhanced_result.get('search_text')}")
        print(f"Searched columns: {enhanced_result.get('searched_columns')}")

        if "also_searched_substrate" in enhanced_result:
            print(f"\n✓ Also searched by substrate:")
            print(
                f"  Substrate: {enhanced_result['also_searched_substrate']['substrate_name']}")
            print(
                f"  ID: {enhanced_result['also_searched_substrate']['substrate_id']}")

        print(
            f"\nFound {len(enhanced_result.get('rows', []))} matching standards")

        for row in enhanced_result.get("rows", [])[:2]:  # Show first 2
            values = row.get("values", [])
            if len(values) >= 2:
                print(f"\n  • {values[1]}")  # Standard name
    else:
        print(f"Error: {enhanced_result.get('error')}")

    # Step 5: Search for imaging-related substrates
    print("\n\n5. Searching for imaging-related substrates:")
    print("-" * 80)
    imaging_substrates = await search_substrates_impl("imaging", max_results=5)

    if imaging_substrates["success"]:
        if len(imaging_substrates["substrates"]) > 0:
            print(
                f"Found {len(imaging_substrates['substrates'])} imaging-related substrates:\n")
            for substrate in imaging_substrates["substrates"]:
                print(f"  • {substrate['name']}")
                if substrate['description'] != "No description available":
                    print(f"    {substrate['description'][:100]}...")
                print()
        else:
            print("No imaging-related substrates found in the search.")
    else:
        print(f"Error: {imaging_substrates.get('error')}")

    print("\n" + "=" * 80)
    print("Workflow complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(example_substrate_workflow())
