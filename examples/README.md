# Standards Explorer MCP - Examples

This directory contains example scripts and tools to help you understand and explore the Standards Explorer MCP functionality.

## Example Scripts

### Search Examples

These scripts demonstrate the search functionality for different dimensions of the standards data:

- **`example_search_topics.py`** - Demonstrates topic-based search workflow
  - List all available topics
  - Search topics by keyword
  - Find standards for specific topics
  - Enhanced search with automatic topic matching

- **`example_search_substrates.py`** - Demonstrates substrate/data format search workflow
  - List all available substrates (data formats)
  - Search substrates by keyword
  - Find standards for specific substrates (e.g., JSON, CSV, BIDS)
  - Enhanced search with automatic substrate matching

- **`example_search_organizations.py`** - Demonstrates organization-based search workflow
  - List all available organizations
  - Search organizations by keyword
  - Find standards from specific organizations (e.g., HL7, W3C, CDISC)
  - Search by responsible organizations only
  - Enhanced search with automatic organization matching

- **`example_topic_search.py`** - Additional topic search demonstrations
  - Focused examples of topic discovery and standards lookup

### Exploration Scripts

These scripts query the underlying Synapse tables to explore their structure and contents:

- **`explore_topics.py`** - Explore the DataTopics table structure
  - View column schema
  - Sample topic data

- **`explore_substrates.py`** - Explore the DataSubstrate table structure
  - View column schema
  - Sample substrate/format data

- **`explore_organizations.py`** - Explore the Organization table structure
  - View column schema
  - Sample organization data

- **`explore_standards_topics.py`** - Explore how topics are referenced in the standards table
  - Examine the concerns_data_topic column
  - See examples of topic ID arrays

### Utility Scripts

- **`example_client.py`** - Basic MCP client usage example
  - Connect to the MCP server
  - Call tools
  - Handle responses

- **`list_tools.py`** - List all available MCP tools
  - Shows all 13 registered tools
  - Groups them by category (topics, substrates, organizations)

## Running the Examples

All examples can be run using `uv`:

```bash
# From the repo root
uv run python examples/example_search_topics.py
uv run python examples/example_search_substrates.py
uv run python examples/example_search_organizations.py

# Exploration scripts
uv run python examples/explore_topics.py
uv run python examples/explore_substrates.py
uv run python examples/explore_organizations.py

# Utilities
uv run python examples/list_tools.py
```

## What These Examples Demonstrate

### Multi-Dimensional Search

The examples show how to search for standards across four dimensions:

1. **Text Search** - Search by name, description, purpose
2. **Topics** - Search by data type/domain (e.g., EHR, Genomics, Image)
3. **Substrates** - Search by data format (e.g., JSON, CSV, BIDS, DICOM)
4. **Organizations** - Search by creator/maintainer (e.g., HL7, W3C, CDISC)

### Enhanced Search

The enhanced search feature automatically enriches searches:
- Searching for "Genomics" matches both text and topic
- Searching for "JSON" matches both text and substrate
- Searching for "HL7" matches both text and organization

### Discovery Workflows

Each example follows a typical discovery workflow:
1. List all available items (topics/substrates/organizations)
2. Search by keyword to find relevant items
3. Find standards for specific items
4. Use enhanced search for integrated results

## Learning Path

Recommended order for exploring the examples:

1. Start with `list_tools.py` to see what's available
2. Try `example_search_topics.py` to understand basic search patterns
3. Move to `example_search_substrates.py` for data format discovery
4. Explore `example_search_organizations.py` for organizational relationships
5. Use exploration scripts to understand the underlying data structure

## Use Cases

These examples demonstrate solutions for common use cases:

- **Researchers**: "What standards are available for genomic data?"
- **Data Engineers**: "What standards work with JSON format?"
- **Standards Bodies**: "What standards does my organization maintain?"
- **Compliance Teams**: "Who is responsible for this standard?"
- **Integration Teams**: "What formats does this standard support?"

## API Documentation

For detailed API documentation, see:
- `TOPIC_SEARCH_IMPLEMENTATION.md`
- `SUBSTRATE_IMPLEMENTATION.md`
- `ORGANIZATION_IMPLEMENTATION.md`

## Testing

Note: These are example/demonstration scripts, not tests. The actual test suite is in the `tests/` directory and uses pytest.
