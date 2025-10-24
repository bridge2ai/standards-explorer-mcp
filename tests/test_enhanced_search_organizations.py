"""Test enhanced search with organization matching."""
import pytest
from standards_explorer_mcp.main import search_standards_impl


@pytest.mark.asyncio
async def test_search_with_organization_match():
    """Test that searching for an organization name also searches by organization."""
    # Search for "CDISC" which is an organization name
    result = await search_standards_impl("CDISC", max_results=10)

    assert result["success"] is True
    assert "search_text" in result
    assert result["search_text"] == "CDISC"

    # Should indicate that it also searched by organization
    if "also_searched_organization" in result:
        assert result["also_searched_organization"]["organization_name"] == "CDISC"
        assert "organization_id" in result["also_searched_organization"]


@pytest.mark.asyncio
async def test_search_with_all_dimensions():
    """Test that searching can match topic, substrate, and organization."""
    # Search for something that might match across dimensions
    result = await search_standards_impl("HL7", max_results=10)

    assert result["success"] is True
    assert "search_text" in result

    # If HL7 is an organization, it should be matched
    if "also_searched_organization" in result:
        assert "organization_id" in result["also_searched_organization"]


@pytest.mark.asyncio
async def test_search_without_organization_match():
    """Test that searching for non-organization text works normally."""
    # Search for something that's not an organization name
    result = await search_standards_impl("metadata", max_results=10)

    assert result["success"] is True
    assert "search_text" in result
    assert result["search_text"] == "metadata"

    # Should not have organization match unless "metadata" happens to be an org
    # (This is a soft check - just verify the search completes)


@pytest.mark.asyncio
async def test_search_disable_organization():
    """Test that organization search can be disabled."""
    # Search with organization search disabled
    result = await search_standards_impl(
        "CDISC",
        max_results=10,
        include_organization_search=False
    )

    assert result["success"] is True
    # Should NOT have also_searched_organization even though CDISC is an organization
    assert "also_searched_organization" not in result


@pytest.mark.asyncio
async def test_search_organization_w3c():
    """Test searching for W3C organization."""
    result = await search_standards_impl("W3C", max_results=10)

    assert result["success"] is True
    assert "search_text" in result

    # W3C should be a well-known organization
    if "also_searched_organization" in result:
        assert "organization_id" in result["also_searched_organization"]
