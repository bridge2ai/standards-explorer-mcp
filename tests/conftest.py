"""
Pytest configuration and shared fixtures.
"""

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require running MCP server)"
    )
    config.addinivalue_line(
        "markers", "asyncio: marks tests as async"
    )


@pytest.fixture
def sample_sql_queries():
    """Sample SQL queries for testing."""
    return {
        "simple": "SELECT * FROM syn63096833 LIMIT 5",
        "with_where": "SELECT id, name FROM syn63096833 WHERE name LIKE '%FHIR%' LIMIT 10",
        "with_offset": "SELECT * FROM syn63096833 LIMIT 3 OFFSET 3",
        "specific_columns": "SELECT id, name, category FROM syn63096833 LIMIT 5",
        "multiple_conditions": "SELECT id, name FROM syn63096833 WHERE name LIKE '%format%' AND category IS NOT NULL LIMIT 5"
    }


@pytest.fixture
def sample_search_terms():
    """Sample search terms for testing."""
    return {
        "common": "FHIR",
        "specific": "metadata",
        "general": "format",
        "rare": "xyzabc123nonexistent"
    }
