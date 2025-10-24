"""Example script demonstrating organization search functionality."""

import asyncio
from standards_explorer_mcp.main import (
    list_organizations_impl,
    search_organizations_impl,
    search_by_organization_impl,
    search_standards_impl
)


async def example_organization_workflow():
    """
    Demonstrate a typical workflow using organization search functionality.
    """
    print("=" * 80)
    print("ORGANIZATION SEARCH WORKFLOW DEMONSTRATION")
    print("=" * 80)

    # Step 1: List all available organizations
    print("\n1. Listing all available organizations:")
    print("-" * 80)
    organizations_result = await list_organizations_impl()

    if organizations_result["success"]:
        print(f"Found {organizations_result['total_organizations']} organizations:\n")
        for org in organizations_result["organizations"][:10]:  # Show first 10
            print(f"  • {org['name']} (ID: {org['id']})")
            desc = org['description']
            if desc and desc != "No description available":
                print(f"    Description: {desc[:80]}...")
            print()
    else:
        print(f"Error: {organizations_result.get('error')}")

    # Step 2: Search for organizations by keyword
    print("\n2. Searching for organizations related to 'health':")
    print("-" * 80)
    search_result = await search_organizations_impl("health", max_results=5)

    if search_result["success"]:
        print(f"Found {len(search_result['organizations'])} matching organizations:\n")
        for org in search_result["organizations"]:
            print(f"  • {org['name']} (ID: {org['id']})")
            print(f"    {org['description'][:80]}...")
            print()
    else:
        print(f"Error: {search_result.get('error')}")

    # Step 3: Find standards for a specific organization
    print("\n3. Finding standards related to 'HL7' organization:")
    print("-" * 80)
    hl7_standards = await search_by_organization_impl("HL7", max_results=5)

    if hl7_standards["success"]:
        print(f"Organization: {hl7_standards.get('organization_name')}")
        print(f"Organization ID: {hl7_standards.get('organization_id')}")
        print(f"Found {len(hl7_standards.get('rows', []))} standards:\n")

        for row in hl7_standards.get("rows", [])[:3]:  # Show first 3
            values = row.get("values", [])
            if len(values) >= 2:
                print(f"  • {values[0]}")  # Standard ID
                print(f"    Name: {values[1]}")  # Standard name
                print()
    else:
        print(f"Error: {hl7_standards.get('error')}")

    # Step 4: Search for responsible organizations only
    print("\n4. Finding standards where 'CDISC' is the responsible organization:")
    print("-" * 80)
    cdisc_responsible = await search_by_organization_impl(
        "CDISC", 
        max_results=5,
        search_responsible_only=True
    )

    if cdisc_responsible["success"]:
        print(f"Organization: {cdisc_responsible.get('organization_name')}")
        print(f"Organization ID: {cdisc_responsible.get('organization_id')}")
        print(f"Search responsible only: {cdisc_responsible.get('search_responsible_only')}")
        print(f"Found {len(cdisc_responsible.get('rows', []))} standards\n")

        for row in cdisc_responsible.get("rows", [])[:2]:  # Show first 2
            values = row.get("values", [])
            if len(values) >= 2:
                print(f"  • {values[1]}")  # Standard name
    else:
        print(f"Error: {cdisc_responsible.get('error')}")

    # Step 5: Demonstrate enhanced search with organization matching
    print("\n\n5. Enhanced search - searching for 'W3C' (matches organization name):")
    print("-" * 80)
    enhanced_result = await search_standards_impl("W3C", max_results=5)

    if enhanced_result["success"]:
        print(f"Search text: {enhanced_result.get('search_text')}")
        print(f"Searched columns: {enhanced_result.get('searched_columns')}")

        if "also_searched_organization" in enhanced_result:
            print(f"\n✓ Also searched by organization:")
            print(f"  Organization: {enhanced_result['also_searched_organization']['organization_name']}")
            print(f"  ID: {enhanced_result['also_searched_organization']['organization_id']}")

        print(f"\nFound {len(enhanced_result.get('rows', []))} matching standards")

        for row in enhanced_result.get("rows", [])[:2]:  # Show first 2
            values = row.get("values", [])
            if len(values) >= 2:
                print(f"\n  • {values[1]}")  # Standard name
    else:
        print(f"Error: {enhanced_result.get('error')}")

    # Step 6: Search for international standards organizations
    print("\n\n6. Searching for international standards organizations:")
    print("-" * 80)
    intl_orgs = await search_organizations_impl("international", max_results=5)

    if intl_orgs["success"]:
        if len(intl_orgs["organizations"]) > 0:
            print(f"Found {len(intl_orgs['organizations'])} international organizations:\n")
            for org in intl_orgs["organizations"]:
                print(f"  • {org['name']}")
                if org['description'] != "No description available":
                    print(f"    {org['description'][:80]}...")
                print()
        else:
            print("No international organizations found in the search.")
    else:
        print(f"Error: {intl_orgs.get('error')}")

    print("\n" + "=" * 80)
    print("Workflow complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(example_organization_workflow())
