"""
USA Census Data Fetcher and Aggregator

This module fetches county-level population data from the ArcGIS REST API,
aggregates it by state, and stores the results in a SQLite database.

Features:
    - Handles paginated API responses
    - Aggregates county data by state
    - Stores data in SQLite database
    - Supports scheduled periodic updates

Usage:
    python fetch_data.py              # Run once
    python fetch_data.py --schedule   # Run every hour
"""

import requests
import sqlite3
import sys
import schedule
import time
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ArcGIS REST API endpoint
API_URL = "https://services.arcgis.com/P3ePLMYs2RVChkJx/ArcGIS/rest/services/USA_Census_Counties/FeatureServer/0/query"


def fetch_counties_data():
    """
    Fetch all county population data from ArcGIS REST API.
    
    Handles pagination automatically by checking 'exceededTransferLimit' flag
    and incrementing resultOffset until all records are retrieved.
    
    Returns:
        List[Dict]: List of feature dictionaries containing county data
        
    Example response structure:
        [
            {"attributes": {"STATE_NAME": "Texas", "POPULATION": 12345}},
            ...
        ]
    """
    params = {
        "where": "1=1",
        "outFields": "POPULATION,STATE_NAME",
        "returnGeometry": "false",
        "f": "json",
        "resultOffset": 0
    }
    
    all_features = []

    # Fetch data with pagination support
    while True:
        try:
            response = requests.get(API_URL, params=params)
            data = response.json()
            features = data.get("features", []) 
            all_features.extend(features)
            
            # Check if there are more records to fetch
            if not data.get("exceededTransferLimit", False):
                break
            else:
                # Update offset for next batch
                params["resultOffset"] = params.get("resultOffset", 0) + len(features)
        
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            return all_features
                
    logging.info(f"Fetched {len(all_features)} counties")
    return all_features
    

def aggregate_by_state(features):
    """
    Aggregate county population data by state.
    
    Sums all county populations within each state to get total state population.
    Handles None/null population values by treating them as 0.
    
    Args:
        features (List[Dict]): List of county features from API
        
    Returns:
        Dict[str, int]: Dictionary mapping state names to total population
        
    Example:
        Input: [
            {"attributes": {"STATE_NAME": "Texas", "POPULATION": 1000}},
            {"attributes": {"STATE_NAME": "Texas", "POPULATION": 2000}}
        ]
        Output: {"Texas": 3000}
    """
    total_sum_population = {}

    for item in features:
        state = item["attributes"]['STATE_NAME']
        population = item["attributes"]['POPULATION'] or 0
    
        total_sum_population[state] = total_sum_population.get(state, 0) + population
    
    logging.info(f"Aggregated data for {len(total_sum_population)} states")

    return total_sum_population


def save_to_database(state_data):
    """
    Save aggregated state population data to SQLite database.
    
    Creates the state_population table if it doesn't exist.
    Uses INSERT OR REPLACE to update existing records.
    
    Args:
        state_data (Dict[str, int]): Dictionary mapping state names to populations
        
    Database Schema:
        Table: state_population
        Columns:
            - state_name (TEXT, PRIMARY KEY)
            - population (INTEGER)
    """
    try:
        connection = sqlite3.connect('demographics.db')
        cursor = connection.cursor()

        # Create table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS state_population (
                state_name TEXT PRIMARY KEY,
                population INTEGER
            )
        ''')

        # Insert or update state data
        for state_name, population in state_data.items():
            cursor.execute(
                "INSERT OR REPLACE INTO state_population VALUES (?, ?)", 
                (state_name, population)
            )

        connection.commit()

        # Log summary
        cursor.execute("SELECT COUNT(*) FROM state_population")
        count = cursor.fetchone()[0]
        logging.info(f"Database updated: {count} states saved")

        connection.close()
    
    except Exception as e:
        logging.error(f"Error saving to database: {e}")


def main():
    """
    Main execution function.
    
    Orchestrates the complete data pipeline:
    1. Fetch county data from API
    2. Aggregate by state
    3. Save to database
    """
    logging.info("Starting data fetch...")
    all_features = fetch_counties_data()
    total_sum_population = aggregate_by_state(all_features)
    save_to_database(total_sum_population)


if __name__ == "__main__":
    if "--schedule" in sys.argv:
        # Scheduled mode - run every hour
        logging.info("Starting scheduled mode - will run every 1 hour")
        main()  # Run immediately
        schedule.every(1).hour.do(main)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # Single execution mode
        main()
