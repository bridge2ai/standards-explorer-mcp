"""Test organization search functionality."""
import pytest
from standards_explorer_mcp.main import (
    list_organizations_impl,
    search_by_organization_impl,
    search_organizations_impl
)


@pytest.mark.asyncio
async def test_list_organizations():
    """Test listing all organizations."""
    result = await list_organizations_impl()

    assert result["success"] is True
    assert "organizations" in result
    assert len(result["organizations"]) > 0
    assert "total_organizations" in result

    # Check structure of first organization
    first_org = result["organizations"][0]
    assert "id" in first_org
    assert "name" in first_org
    assert "description" in first_org


@pytest.mark.asyncio
async def test_search_by_organization():
    """Test searching standards by organization name."""
    # Search for CDISC organization
    result = await search_by_organization_impl("CDISC")

    assert result["success"] is True
    assert "organization_name" in result
    assert "organization_id" in result
    assert result["organization_id"].startswith("B2AI_ORG:")


@pytest.mark.asyncio
async def test_search_by_organization_hl7():
    """Test searching standards by HL7 organization."""
    # Search for HL7 organization (common standards body)
    result = await search_by_organization_impl("HL7")

    assert result["success"] is True
    assert "organization_name" in result
    assert "organization_id" in result
    assert result["organization_id"].startswith("B2AI_ORG:")


@pytest.mark.asyncio
async def test_search_by_organization_responsible_only():
    """Test searching standards by responsible organization only."""
    # Search with responsible_only flag
    result = await search_by_organization_impl("CDISC", search_responsible_only=True)

    assert result["success"] is True
    assert "organization_name" in result
    assert result.get("search_responsible_only") is True


@pytest.mark.asyncio
async def test_search_organizations():
    """Test searching organizations by keyword."""
    # Search for organizations related to "health"
    result = await search_organizations_impl("health")

    assert result["success"] is True
    assert "organizations" in result
    assert "search_text" in result
    assert result["search_text"] == "health"


@pytest.mark.asyncio
async def test_search_organizations_international():
    """Test searching organizations for "international" keyword."""
    result = await search_organizations_impl("international")

    assert result["success"] is True
    assert "organizations" in result
    assert len(result["organizations"]) > 0

    # Check structure
    for org in result["organizations"]:
        assert "id" in org
        assert "name" in org
        assert "description" in org


@pytest.mark.asyncio
async def test_search_organizations_standards():
    """Test searching organizations for standards-related terms."""
    result = await search_organizations_impl("standards")

    assert result["success"] is True
    assert "organizations" in result

    # If standards organizations exist, they should be in the results
    if len(result["organizations"]) > 0:
        org_names = [o["name"].lower() for o in result["organizations"]]
        # Check structure is correct
        for org in result["organizations"]:
            assert "id" in org
            assert "name" in org
            assert "description" in org
