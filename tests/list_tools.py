"""List all available MCP tools."""
import asyncio
from standards_explorer_mcp.main import mcp


async def list_tools():
    """List all registered MCP tools."""
    print("=" * 80)
    print("REGISTERED MCP TOOLS")
    print("=" * 80)
    print()

    # Access the tools directly from the mcp instance
    tools = mcp._tools

    print(f"Total tools: {len(tools)}\n")

    for i, (tool_name, tool_info) in enumerate(sorted(tools.items()), 1):
        print(f"{i}. {tool_name}")
        if hasattr(tool_info, 'fn') and hasattr(tool_info.fn, '__doc__'):
            doc = tool_info.fn.__doc__
            if doc:
                # Get first line of docstring
                first_line = doc.strip().split('\n')[0]
                print(f"   {first_line}")
        print()

    print("=" * 80)
    print("\nNEW SUBSTRATE TOOLS:")
    print("-" * 80)
    substrate_tools = [
        name for name in tools.keys() if 'substrate' in name.lower()]
    for tool_name in substrate_tools:
        print(f"  • {tool_name}")
    print()

    print("TOPIC TOOLS:")
    print("-" * 80)
    topic_tools = [name for name in tools.keys() if 'topic' in name.lower()]
    for tool_name in topic_tools:
        print(f"  • {tool_name}")
    print()


if __name__ == "__main__":
    asyncio.run(list_tools())
