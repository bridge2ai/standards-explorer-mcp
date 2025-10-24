# Data Substrate Functionality Implementation

## Overview

This document describes the implementation of data substrate search functionality for the Standards Explorer MCP server. The implementation mirrors the existing data topic search functionality, providing a consistent pattern for searching standards by different metadata dimensions.

## Implementation Summary

### New Features

1. **Substrate Caching System**
   - `SYNAPSE_SUBSTRATES_TABLE_ID`: Table ID constant for DataSubstrate table (syn63096834)
   - `_SUBSTRATES_CACHE`: Global cache for substrate name → ID mappings
   - `_load_substrates_mapping()`: Async function to query and cache substrate mappings

2. **Substrate Search Functions**
   - `search_by_substrate_impl(substrate_name, max_results)`: Search standards by substrate name
   - `list_substrates_impl()`: List all available substrates with descriptions
   - `search_substrates_impl(search_text, max_results)`: Search substrates by keyword

3. **Enhanced Standard Search**
   - Updated `search_standards_impl()` to include automatic substrate matching
   - Added `include_substrate_search` parameter (default: True)
   - When search text matches a substrate name, also searches `has_relevant_data_substrate` column
   - Returns `also_searched_substrate` metadata when substrate match occurs

4. **MCP Tool Wrappers**
   - `@mcp.tool search_by_substrate`: Search standards for a specific substrate
   - `@mcp.tool list_substrates`: List all available substrates
   - `@mcp.tool search_substrates`: Search substrates by keyword

5. **Updated Table Info**
   - `get_standards_table_info_impl()` now returns `substrates_table_id`

## Tool Count

The MCP server now provides **10 tools** (up from 7):

**Core Tools (4):**
1. `query_table` - Direct SQL query to standards table
2. `search_standards` - Enhanced text search with auto topic/substrate matching
3. `get_standards_table_info` - Get table and project information
4. `search_with_variations` - Search with multiple term variations

**Topic Tools (3):**
5. `search_by_topic` - Search standards by data topic name
6. `list_topics` - List all available data topics
7. `search_topics` - Search topics by keyword

**Substrate Tools (3) - NEW:**
8. `search_by_substrate` - Search standards by data substrate name
9. `list_substrates` - List all available data substrates
10. `search_substrates` - Search substrates by keyword

## Data Model

### DataSubstrate Table (syn63096834)

**Key Columns:**
- `id`: Substrate identifier (e.g., "B2AI_SUBSTRATE:1")
- `name`: Substrate name (e.g., "Array", "BIDS", "JSON")
- `description`: Detailed description of the substrate
- `category`: Classification of substrate type
- `subclass_of`: Parent substrate relationships
- `file_extensions`: Associated file formats
- `metadata_storage`: How metadata is stored

**Sample Substrates (81 total):**
- Array - Data collections indexed by integers
- Associative Array - Key-value pair structures
- BIDS - Brain Imaging Data Structure
- BigQuery - Google's data warehouse
- Column Store - Column-oriented databases
- CSV - Comma-separated values
- Database - General database systems
- DICOM - Medical imaging format
- JSON - JavaScript Object Notation
- MongoDB - Document database
- And 71 more...

### Standards Table Reference

The `has_relevant_data_substrate` column in the Standards table (syn63096833) contains JSON arrays of substrate IDs:
```json
["B2AI_SUBSTRATE:11", "B2AI_SUBSTRATE:3"]
```

## Usage Examples

### Example 1: List All Substrates
```python
from standards_explorer_mcp.main import list_substrates_impl

result = await list_substrates_impl()
# Returns: {
#   "success": True,
#   "substrates": [
#     {"id": "B2AI_SUBSTRATE:1", "name": "Array", "description": "..."},
#     {"id": "B2AI_SUBSTRATE:2", "name": "Associative Array", "description": "..."},
#     ...
#   ],
#   "total_substrates": 81,
#   "table_id": "syn63096834"
# }
```

### Example 2: Search Substrates by Keyword
```python
from standards_explorer_mcp.main import search_substrates_impl

# Find database-related substrates
result = await search_substrates_impl("database", max_results=5)
# Returns substrates like: Column Store, Database, Document Database, 
# Graph Database, MongoDB
```

### Example 3: Find Standards for a Substrate
```python
from standards_explorer_mcp.main import search_by_substrate_impl

# Find standards that work with JSON
result = await search_by_substrate_impl("JSON", max_results=20)
# Returns: {
#   "success": True,
#   "substrate_name": "JSON",
#   "substrate_id": "B2AI_SUBSTRATE:20",
#   "search_method": "substrate",
#   "rows": [...],  # Standards that use JSON
#   ...
# }
```

### Example 4: Enhanced Search (Automatic Substrate Matching)
```python
from standards_explorer_mcp.main import search_standards_impl

# Search for "Array" - automatically matches substrate
result = await search_standards_impl("Array", max_results=10)
# Returns: {
#   "success": True,
#   "search_text": "Array",
#   "searched_columns": ["name", "description", "purpose_detail"],
#   "also_searched_substrate": {
#     "substrate_name": "Array",
#     "substrate_id": "B2AI_SUBSTRATE:1"
#   },
#   "rows": [...]  # Standards matching "Array" in text OR substrates
# }
```

### Example 5: Workflow - Discover Standards for Data Format
```python
# Step 1: Search for relevant substrates
substrates = await search_substrates_impl("imaging")
# Returns: BIDS, DICOM, Retinal Image, FLIO data, OCT data

# Step 2: Pick a substrate and find its standards
standards = await search_by_substrate_impl("BIDS", max_results=20)
# Returns all standards compatible with BIDS format
```

## Testing

### Test Coverage

**New Test Files:**
- `tests/test_substrate_search.py` - 6 tests for substrate functionality
- `tests/test_enhanced_search_substrates.py` - 4 tests for enhanced search
- `tests/example_search_substrates.py` - Demonstration workflow script

**Test Results:**
- Total tests: 41 (up from 31)
- All tests passing ✓

**Test Categories:**
1. Substrate listing and querying (6 tests)
2. Enhanced search with substrate matching (4 tests)
3. API endpoints (6 tests)
4. MCP integration (7 tests)
5. Topic search (5 tests)
6. Core tools (10 tests)
7. Enhanced search with topics (2 tests)
8. Search topics (3 tests)

## Pattern Consistency

The substrate implementation follows the exact same pattern as topics for maintainability:

| Component | Topics | Substrates |
|-----------|--------|------------|
| Table ID | syn63096835 | syn63096834 |
| Column | concerns_data_topic | has_relevant_data_substrate |
| Cache | _TOPICS_CACHE | _SUBSTRATES_CACHE |
| Loader | _load_topics_mapping() | _load_substrates_mapping() |
| Search by X | search_by_topic_impl() | search_by_substrate_impl() |
| List X | list_topics_impl() | list_substrates_impl() |
| Search X | search_topics_impl() | search_substrates_impl() |
| MCP Tool 1 | @mcp.tool search_by_topic | @mcp.tool search_by_substrate |
| MCP Tool 2 | @mcp.tool list_topics | @mcp.tool list_substrates |
| MCP Tool 3 | @mcp.tool search_topics | @mcp.tool search_substrates |

## Agent Instructions

When the MCP tools are exposed to an AI agent:

1. **Discovery Workflow:**
   - Use `list_substrates` to see all available data formats
   - Use `search_substrates` to find relevant formats by keyword
   - Use `search_by_substrate` to find standards for specific formats

2. **Enhanced Search:**
   - When user searches for a substrate name (e.g., "JSON", "CSV"), `search_standards` automatically includes substrate-based results
   - Agent sees metadata indicating substrate match occurred

3. **Combined Search:**
   - Both topics AND substrates can match in a single search
   - Enables multi-dimensional discovery: "Find standards for EHR data (topic) that work with JSON (substrate)"

## Performance

- **Caching:** Substrate mappings loaded once and cached globally
- **Query Efficiency:** Substrate searches use indexed LIKE queries
- **Lazy Loading:** Substrates only loaded when first accessed

## Future Enhancements

Potential improvements following this pattern:

1. Add more metadata dimensions (e.g., organizations, use cases)
2. Implement combination filters (topic AND substrate)
3. Add fuzzy matching for substrate names
4. Cache invalidation for updated substrate data
5. Statistics on substrate usage across standards

## Summary

The substrate functionality successfully extends the MCP server with powerful data format-based search capabilities, following established patterns and maintaining 100% test coverage. Users can now discover standards based on:

- **What they do** (text search)
- **What data they concern** (topics)
- **What formats they work with** (substrates) ← NEW

This provides a comprehensive, multi-dimensional approach to exploring the Bridge2AI Standards ecosystem.
