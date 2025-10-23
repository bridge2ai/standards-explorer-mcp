"""
Tests for the MCP server tools.

These tests verify that the MCP server tools work correctly by calling them directly
without going through the MCP protocol layer.
"""

import pytest
from standards_explorer_mcp.main import (
    query_table_impl,
    search_standards_impl,
    get_standards_table_info_impl
)


@pytest.mark.asyncio
async def test_get_table_info():
    """Test getting table information."""
    result = get_standards_table_info_impl()

    assert result is not None
    assert result["table_id"] == "syn63096833"
    assert result["project_id"] == "syn63096806"
    assert "synapse_url" in result
    assert "project_url" in result
    assert "Bridge2AI" in result["table_name"]


@pytest.mark.asyncio
async def test_query_table_simple():
    """Test simple SQL query through query_table tool."""
    result = await query_table_impl("SELECT * FROM syn63096833 LIMIT 5")

    assert result is not None
    assert result["success"] is True
    assert result["row_count"] == 5
    assert "columns" in result
    assert "rows" in result
    assert len(result["rows"]) == 5


@pytest.mark.asyncio
async def test_query_table_with_where():
    """Test SQL query with WHERE clause."""
    result = await query_table_impl(
        "SELECT id, name FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 10"
    )

    assert result is not None
    assert result["success"] is True
    assert result["row_count"] > 0, "Should find at least one FHIR result"
    assert len(result["columns"]) == 2, "Should return 2 columns"

    # Verify FHIR is in the results
    found_fhir = False
    for row in result["rows"]:
        name = row["values"][1]  # name column
        if "FHIR" in name.upper():
            found_fhir = True
            break
    assert found_fhir, "Should find at least one result with FHIR in name"


@pytest.mark.asyncio
async def test_query_table_column_selection():
    """Test selecting specific columns."""
    result = await query_table_impl(
        "SELECT id, name, category FROM syn63096833 LIMIT 3"
    )

    assert result is not None
    assert result["success"] is True
    assert len(result["columns"]) == 3

    column_names = [col["name"] for col in result["columns"]]
    assert "id" in column_names
    assert "name" in column_names
    assert "category" in column_names


@pytest.mark.asyncio
async def test_search_standards_basic():
    """Test basic text search using search_standards tool."""
    result = await search_standards_impl(
        search_text="FHIR",
        max_results=5
    )

    assert result is not None
    assert result["success"] is True
    assert result["search_text"] == "FHIR"
    assert "searched_columns" in result
    assert result["row_count"] > 0, "Should find FHIR results"


@pytest.mark.asyncio
async def test_search_standards_custom_columns():
    """Test search with custom columns specified."""
    result = await search_standards_impl(
        search_text="metadata",
        columns_to_search=["description"],
        max_results=5
    )

    assert result is not None
    assert result["success"] is True
    assert result["searched_columns"] == ["description"]
    assert result["search_text"] == "metadata"


@pytest.mark.asyncio
async def test_search_standards_pagination():
    """Test search with pagination."""
    # First page
    result1 = await search_standards_impl(
        search_text="standard",
        max_results=3,
        offset=0
    )

    # Second page
    result2 = await search_standards_impl(
        search_text="standard",
        max_results=3,
        offset=3
    )

    assert result1["success"] is True
    assert result2["success"] is True

    # Verify different results
    if result1["row_count"] > 0 and result2["row_count"] > 0:
        ids1 = [row["values"][0] for row in result1["rows"]]
        ids2 = [row["values"][0] for row in result2["rows"]]
        # Pages should have different IDs
        assert len(set(ids1) & set(ids2)
                   ) == 0, "Pagination should return different results"


@pytest.mark.asyncio
async def test_search_standards_no_results():
    """Test search that returns no results."""
    result = await search_standards_impl(
        search_text="xyzabc123nonexistent",
        max_results=5
    )

    assert result is not None
    assert result["success"] is True
    assert result["row_count"] == 0, "Should return 0 results for nonexistent term"


@pytest.mark.asyncio
async def test_query_table_invalid_sql():
    """Test that invalid SQL is handled gracefully."""
    result = await query_table_impl("SELECT * FROM nonexistent_table")

    assert result is not None
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_search_multiple_columns():
    """Test searching across multiple columns."""
    result = await search_standards_impl(
        search_text="format",
        columns_to_search=["name", "description", "purpose_detail"],
        max_results=10
    )

    assert result is not None
    assert result["success"] is True
    assert len(result["searched_columns"]) == 3
