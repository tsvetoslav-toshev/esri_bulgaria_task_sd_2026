"""
Unit Tests for USA Census Data API and Aggregator

Tests both the FastAPI endpoints and the data aggregation logic
to ensure correct functionality of the population data system.
"""

import pytest
from fetch_data import aggregate_by_state
from fastapi.testclient import TestClient
from api import app

# Test client for API testing
client = TestClient(app)


def test_get_all_states():
    """
    Test GET /states endpoint returns list of all states.
    
    Verifies:
    - Response status is 200 OK
    - Response is a list
    - Each item has required fields (state_name, population)
    """
    response = client.get("/states")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "state_name" in data[0]
    assert "population" in data[0]


def test_get_single_state():
    """
    Test GET /states/{state_name} endpoint for specific state.
    
    Verifies:
    - Response status is 200 OK
    - Response contains correct state name
    - Population is a positive number
    """
    response = client.get("/states/Texas")
    
    assert response.status_code == 200
    data = response.json()
    assert data["state_name"] == "Texas"
    assert data["population"] > 0


def test_get_invalid_state():
    """
    Test GET /states/{state_name} returns 404 for non-existent state.
    
    Verifies proper error handling for invalid state names.
    """
    response = client.get("/states/InvalidState")
    
    assert response.status_code == 404


def test_aggregate_by_state():
    """
    Test aggregate_by_state function with test data.
    
    Verifies:
    - Multiple counties in same state are summed correctly
    - Different states are kept separate
    - Output format matches expectations
    """
    # Test data - simulates API response structure
    test_features = [
        {"attributes": {"STATE_NAME": "Texas", "POPULATION": 1000}},
        {"attributes": {"STATE_NAME": "Texas", "POPULATION": 2000}},
        {"attributes": {"STATE_NAME": "California", "POPULATION": 500}},
    ]
    
    # Execute function
    result = aggregate_by_state(test_features)
    
    # Expected result
    expected = {"Texas": 3000, "California": 500}
    
    # Assertions
    assert result == expected
    assert result["Texas"] == 3000
    assert result["California"] == 500


def test_aggregate_by_state_with_none():
    """
    Test aggregate_by_state handles None/null population values.
    
    Verifies that None values are treated as 0 and don't cause errors.
    """
    test_features = [
        {"attributes": {"STATE_NAME": "TestState", "POPULATION": 1000}},
        {"attributes": {"STATE_NAME": "TestState", "POPULATION": None}},
    ]
    
    result = aggregate_by_state(test_features)
    
    assert result["TestState"] == 1000