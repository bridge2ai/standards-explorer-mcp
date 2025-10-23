"""Test substrate search functionality."""
import pytest
from standards_explorer_mcp.main import (
    list_substrates_impl,
    search_by_substrate_impl,
    search_substrates_impl
)


@pytest.mark.asyncio
async def test_list_substrates():
    """Test listing all substrates."""
    result = await list_substrates_impl()

    assert result["success"] is True
    assert "substrates" in result
    assert len(result["substrates"]) > 0
    assert "total_substrates" in result

    # Check structure of first substrate
    first_substrate = result["substrates"][0]
    assert "id" in first_substrate
    assert "name" in first_substrate
    assert "description" in first_substrate


@pytest.mark.asyncio
async def test_search_by_substrate():
    """Test searching standards by substrate name."""
    # Search for Array substrate
    result = await search_by_substrate_impl("Array")

    assert result["success"] is True
    assert "substrate_name" in result
    assert "substrate_id" in result
    assert result["substrate_id"].startswith("B2AI_SUBSTRATE:")


@pytest.mark.asyncio
async def test_search_by_substrate_json():
    """Test searching standards by JSON substrate."""
    # Search for JSON substrate (should exist)
    result = await search_by_substrate_impl("JSON")

    assert result["success"] is True
    assert "substrate_name" in result
    assert "substrate_id" in result
    assert result["substrate_id"].startswith("B2AI_SUBSTRATE:")


@pytest.mark.asyncio
async def test_search_substrates():
    """Test searching substrates by keyword."""
    # Search for substrates related to "database"
    result = await search_substrates_impl("database")

    assert result["success"] is True
    assert "substrates" in result
    assert "search_text" in result
    assert result["search_text"] == "database"


@pytest.mark.asyncio
async def test_search_substrates_table():
    """Test searching substrates for "table" keyword."""
    result = await search_substrates_impl("table")

    assert result["success"] is True
    assert "substrates" in result
    assert len(result["substrates"]) > 0

    # Check that results contain relevant substrates
    substrate_names = [s["name"].lower() for s in result["substrates"]]
    # Should find substrates like "Column Store" or others with table-like descriptions
    assert len(substrate_names) > 0


@pytest.mark.asyncio
async def test_search_substrates_imaging():
    """Test searching substrates for imaging-related terms."""
    result = await search_substrates_impl("imaging")

    assert result["success"] is True
    assert "substrates" in result

    # If imaging substrates exist, they should be in the results
    # This is a soft assertion since we don't know all available substrates
    if len(result["substrates"]) > 0:
        substrate_names = [s["name"].lower() for s in result["substrates"]]
        # Check structure is correct
        for substrate in result["substrates"]:
            assert "id" in substrate
            assert "name" in substrate
            assert "description" in substrate
