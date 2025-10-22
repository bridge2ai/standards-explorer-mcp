"""Main module for the Standards Explorer MCP implementation."""

from fastmcp import FastMCP

mcp = FastMCP("standards_explorer_mcp")


@mcp.tool
def search_standards(query: str) -> str:
    return f"Searching standards for: {query}"

# Main entrypoint


async def main() -> None:
    print("Starting standards_explorer_mcp FastMCP server.")
    await mcp.run_async("stdio")


def cli() -> None:
    """CLI entry point that properly handles the async main function."""
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    cli()
