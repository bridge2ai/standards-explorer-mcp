"""Main module for the Standards Explorer MCP implementation."""

from fastmcp import FastMCP

mcp = FastMCP("standards_explorer_mcp")

@mcp.tool
def search_standards(query: str) -> str:
    return f"Searching standards for: {query}"

if __name__ == "__main__":
    mcp.run()
