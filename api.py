"""
FastAPI REST API for USA State Population Data

This module provides a RESTful API to query aggregated population data
for US states stored in a SQLite database.

Endpoints:
    GET / - Health check endpoint
    GET /states - Retrieve all states with population data
    GET /states/{state_name} - Retrieve specific state population data
"""

from fastapi import FastAPI, HTTPException
import sqlite3
from typing import List, Dict, Tuple

app = FastAPI(
    title="USA State Population API",
    description="API for querying aggregated US state population data",
    version="1.0.0"
)

def get_db_connection():
    """
    Establish a connection to the SQLite database.
    
    Returns:
        Tuple[sqlite3.Connection, sqlite3.Cursor]: Database connection and cursor objects
    """
    connection = sqlite3.connect('demographics.db')
    cursor = connection.cursor()
    return connection, cursor


@app.get("/")
def read_root():
    """
    Health check endpoint.
    
    Returns:
        Dict[str, str]: Simple greeting message
    """
    return {"Hello": "World"}


@app.get("/states")
def get_all_states():
    """
    Retrieve population data for all US states.
    
    Returns:
        List[Dict[str, any]]: List of dictionaries containing state_name and population
        
    Example:
        [
            {"state_name": "California", "population": 39538223},
            {"state_name": "Texas", "population": 29145505}
        ]
    """
    connection, cursor = get_db_connection()

    cursor.execute("SELECT * FROM state_population")
    rows = cursor.fetchall()
    connection.close()
    
    return [{"state_name": row[0], "population": row[1]} for row in rows]


@app.get("/states/{state_name}")
def get_state(state_name):
    """
    Retrieve population data for a specific US state.
    
    Args:
        state_name (str): Name of the state to query
        
    Returns:
        Dict[str, any]: Dictionary containing state_name and population
        
    Raises:
        HTTPException: 404 error if state is not found in database
        
    Example:
        {"state_name": "California", "population": 39538223}
    """
    connection, cursor = get_db_connection()

    cursor.execute("SELECT * FROM state_population WHERE state_name = ?", (state_name,))
    row = cursor.fetchone()
    connection.close()
    
    if row:
        return {"state_name": row[0], "population": row[1]}
    else:
        raise HTTPException(status_code=404, detail="State not found")
    