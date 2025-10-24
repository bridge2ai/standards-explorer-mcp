"""List all available MCP tools."""
import asyncio
from fastmcp import Client
from standards_explorer_mcp.main import mcp


async def list_tools():
    """List all registered MCP tools."""
    print("=" * 80)
    print("REGISTERED MCP TOOLS")
    print("=" * 80)
    print()

    # Use MCP client to list tools
    async with Client(mcp) as client:
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]

        print(f"Total tools: {len(tool_names)}\n")

        for i, tool in enumerate(sorted(tools, key=lambda t: t.name), 1):
            print(f"{i}. {tool.name}")
            if tool.description:
                # Get first line of description
                first_line = tool.description.strip().split('\n')[0]
                print(f"   {first_line}")
            print()

        print("=" * 80)
        print("\nTOOLS BY CATEGORY:")
        print("-" * 80)

        print("\nCore Tools:")
        core_tools = [
            name for name in tool_names if name in [
                'query_table',
                'search_standards',
                'get_standards_table_info',
                'search_with_variations']]
        for tool_name in sorted(core_tools):
            print(f"  • {tool_name}")

        print("\nTopic Tools:")
        topic_tools = [name for name in tool_names if 'topic' in name.lower()]
        for tool_name in sorted(topic_tools):
            print(f"  • {tool_name}")

        print("\nSubstrate Tools:")
        substrate_tools = [
            name for name in tool_names if 'substrate' in name.lower()]
        for tool_name in sorted(substrate_tools):
            print(f"  • {tool_name}")

        print("\nOrganization Tools:")
        org_tools = [
            name for name in tool_names if 'organization' in name.lower()]
        for tool_name in sorted(org_tools):
            print(f"  • {tool_name}")

        print()


if __name__ == "__main__":
    asyncio.run(list_tools())
