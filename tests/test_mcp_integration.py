"""
Integration tests for the MCP server through the FastMCP client.

These tests verify that the MCP server works correctly when accessed through
the MCP protocol using a client, using in-memory transport.
"""

import pytest
from fastmcp import Client

from standards_explorer_mcp.main import mcp


@pytest.fixture(scope="module")
def test_server():
    """Get the MCP server instance for testing."""
    return mcp


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_list_tools(test_server):
    """Test list_tools through MCP client."""
    async with Client(test_server) as client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        # Basic tools
        assert "query_table" in tool_names
        assert "search_standards" in tool_names
        assert "get_standards_table_info" in tool_names

        # Topic tools
        assert "search_by_topic" in tool_names
        assert "list_topics" in tool_names
        assert "search_topics" in tool_names

        # Substrate tools
        assert "search_by_substrate" in tool_names
        assert "list_substrates" in tool_names
        assert "search_substrates" in tool_names
        
        # Organization tools
        assert "search_by_organization" in tool_names
        assert "list_organizations" in tool_names
        assert "search_organizations" in tool_names

        # Should have 13 tools total
        assert len(tool_names) == 13


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_get_table_info(test_server):
    """Test get_standards_table_info through MCP client."""
    async with Client(test_server) as client:
        result = await client.call_tool("get_standards_table_info", {})

        assert result is not None
        assert result.data is not None
        assert "table_id" in result.data
        assert result.data["table_id"] == "syn63096833"
        assert result.data["project_id"] == "syn63096806"
        assert "topics_table_id" in result.data
        assert result.data["topics_table_id"] == "syn63096835"
        assert "substrates_table_id" in result.data
        assert result.data["substrates_table_id"] == "syn63096834"
        assert "organizations_table_id" in result.data
        assert result.data["organizations_table_id"] == "syn63096836"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_query_table(test_server):
    """Test query_table through MCP client."""
    async with Client(test_server) as client:
        result = await client.call_tool(
            "query_table",
            {"sql_query": "SELECT * FROM syn63096833 LIMIT 5"}
        )

        assert result is not None
        assert result.data is not None
        assert result.data["success"] is True
        assert result.data["row_count"] == 5
        assert len(result.data["rows"]) == 5


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_query_table_with_where(test_server):
    """Test query_table with WHERE clause through MCP client."""
    async with Client(test_server) as client:
        result = await client.call_tool(
            "query_table",
            {"sql_query": "SELECT id, name FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 3"}
        )

        assert result is not None
        assert result.data is not None
        assert result.data["success"] is True
        assert result.data["row_count"] > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_search_standards(test_server):
    """Test search_standards through MCP client."""
    async with Client(test_server) as client:
        result = await client.call_tool(
            "search_standards",
            {
                "search_text": "FHIR",
                "max_results": 5
            }
        )

        assert result is not None
        assert result.data is not None
        assert result.data["success"] is True
        assert result.data["search_text"] == "FHIR"
        assert result.data["row_count"] > 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_search_with_custom_columns(test_server):
    """Test search_standards with custom columns through MCP client."""
    async with Client(test_server) as client:
        result = await client.call_tool(
            "search_standards",
            {
                "search_text": "metadata",
                "columns_to_search": ["description"],
                "max_results": 3
            }
        )

        assert result is not None
        assert result.data is not None
        assert result.data["success"] is True
        assert result.data["searched_columns"] == ["description"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_mcp_search_pagination(test_server):
    """Test pagination through MCP client."""
    async with Client(test_server) as client:
        # First page
        result1 = await client.call_tool(
            "search_standards",
            {
                "search_text": "format",
                "max_results": 3,
                "offset": 0
            }
        )

        # Second page
        result2 = await client.call_tool(
            "search_standards",
            {
                "search_text": "format",
                "max_results": 3,
                "offset": 3
            }
        )

        assert result1.data["success"] is True
        assert result2.data["success"] is True

        # Verify pagination worked
        if result1.data["row_count"] > 0 and result2.data["row_count"] > 0:
            ids1 = [row["values"][0] for row in result1.data["rows"]]
            ids2 = [row["values"][0] for row in result2.data["rows"]]
            assert len(set(ids1) & set(ids2)) == 0
