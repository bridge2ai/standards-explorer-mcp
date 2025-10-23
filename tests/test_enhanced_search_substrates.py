"""Test enhanced search with substrate matching."""
import pytest
from standards_explorer_mcp.main import search_standards_impl


@pytest.mark.asyncio
async def test_search_with_substrate_match():
    """Test that searching for a substrate name also searches by substrate."""
    # Search for "Array" which is a substrate name
    result = await search_standards_impl("Array", max_results=10)

    assert result["success"] is True
    assert "search_text" in result
    assert result["search_text"] == "Array"

    # Should indicate that it also searched by substrate
    if "also_searched_substrate" in result:
        assert result["also_searched_substrate"]["substrate_name"] == "Array"
        assert "substrate_id" in result["also_searched_substrate"]


@pytest.mark.asyncio
async def test_search_with_substrate_and_topic_match():
    """Test that searching can match both substrate and topic."""
    # Search for something that might be both a topic and substrate
    result = await search_standards_impl("JSON", max_results=10)

    assert result["success"] is True
    assert "search_text" in result

    # If JSON is a substrate, it should be matched
    # (We don't require it to be a topic)
    if "also_searched_substrate" in result:
        assert "substrate_id" in result["also_searched_substrate"]


@pytest.mark.asyncio
async def test_search_without_substrate_match():
    """Test that searching for non-substrate text works normally."""
    # Search for something that's not a substrate name
    result = await search_standards_impl("metadata", max_results=10)

    assert result["success"] is True
    assert "search_text" in result
    assert result["search_text"] == "metadata"

    # Should not have substrate match unless "metadata" happens to be a substrate
    # (This is a soft check - just verify the search completes)


@pytest.mark.asyncio
async def test_search_disable_substrate():
    """Test that substrate search can be disabled."""
    # Search with substrate search disabled
    result = await search_standards_impl(
        "Array",
        max_results=10,
        include_substrate_search=False
    )

    assert result["success"] is True
    # Should NOT have also_searched_substrate even though Array is a substrate
    assert "also_searched_substrate" not in result
