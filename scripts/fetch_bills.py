#!/usr/bin/env python3
"""
Script to fetch new bills from Congress.gov API and store them for processing.
"""
import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

class CongressAPI:
    def __init__(self):
        self.api_key = os.getenv('CONGRESS_API_KEY')
        if not self.api_key:
            raise ValueError("CONGRESS_API_KEY environment variable not set")
        self.base_url = "https://api.congress.gov/v3"
        self.headers = {"X-API-Key": self.api_key}

    def fetch_recent_bills(self, days=1):
        """Fetch bills from the last N days."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        url = f"{self.base_url}/bill"
        params = {
            "fromDateTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toDateTime": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "format": "json"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

def save_bills(response_data, root_dir, raw_dir):
    """Save fetched bills to JSON files and a summary JSON."""
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the complete response to bills.json in root directory
    with open(root_dir / 'bills.json', 'w') as f:
        json.dump(response_data, f, indent=2)
    
    # Also save individual bill files in raw_bills directory
    for bill in response_data.get('bills', []):
        bill_number = bill.get('number', '')
        bill_type = bill.get('type', '').lower()
        if bill_number and bill_type:
            bill_id = f"{bill_type}{bill_number}"
            output_file = raw_dir / f"{bill_id}.json"
            with open(output_file, 'w') as f:
                json.dump(bill, f, indent=2)

def main():
    # Set up directories
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    raw_bills_dir = data_dir / "raw_bills"
    
    # Fetch and save bills
    api = CongressAPI()
    try:
        bills = api.fetch_recent_bills()
        save_bills(bills, base_dir, raw_bills_dir)
        print(f"Successfully fetched and saved bills")
    except Exception as e:
        print(f"Error fetching bills: {e}")
        raise

if __name__ == "__main__":
    main()
