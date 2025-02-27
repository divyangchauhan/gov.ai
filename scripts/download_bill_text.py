#!/usr/bin/env python3
"""
Script to download full bill text from Congress.gov API.
"""
import os
import json
import time
import requests
from pathlib import Path

def get_api_key():
    """Get Congress.gov API key from environment variable."""
    api_key = os.getenv('CONGRESS_API_KEY')
    if not api_key:
        raise ValueError("CONGRESS_API_KEY environment variable not set")
    return api_key

def download_bill_text(bill_data, output_dir, api_key):
    """Download the full text of a bill."""
    congress = bill_data.get('congress')
    bill_type = bill_data.get('type').lower()
    bill_number = bill_data.get('number')
    
    # Construct API URL for bill text
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}/text"
    params = {"api_key": api_key, "format": "json"}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        text_data = response.json()

        print("text_data")
        print(text_data)
        
        # Check if there are any text versions available
        if 'textVersions' not in text_data or not text_data['textVersions']:
            print(f"No text available for {bill_type}{bill_number}")
            return None
        
        # Get the latest text version
        latest_text = text_data['textVersions'][0]
        
        # Get the formats available
        formats = latest_text.get('formats', [])
        
        # Prioritize HTML format, then plain text, then PDF
        text_content = None
        text_format = None
        
        for fmt in formats:
            if fmt.get('type') == 'HTML':
                text_url = fmt.get('url')
                if text_url:
                    text_response = requests.get(text_url)
                    text_response.raise_for_status()
                    text_content = text_response.text
                    text_format = 'html'
                    break
            elif fmt.get('type') == 'Formatted Text' and not text_content:
                text_url = fmt.get('url')
                if text_url:
                    text_response = requests.get(text_url)
                    text_response.raise_for_status()
                    text_content = text_response.text
                    text_format = 'html'
            elif fmt.get('type') == 'TXT' and not text_content:
                text_url = fmt.get('url')
                if text_url:
                    text_response = requests.get(text_url)
                    text_response.raise_for_status()
                    text_content = text_response.text
                    text_format = 'txt'
        
        if not text_content:
            print(f"No suitable text format found for {bill_type}{bill_number}")
            return None
        
        # Save the text content
        bill_id = f"{bill_type}{bill_number}"
        output_file = output_dir / f"{bill_id}.{text_format}"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Return the format and path for later use
        return {
            'format': text_format,
            'path': str(output_file.relative_to(Path(__file__).parent.parent))
        }
        
    except requests.RequestException as e:
        print(f"Error downloading text for {bill_type}{bill_number}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {bill_type}{bill_number}: {e}")
        return None

def process_bills(bills_file, output_dir):
    """Process all bills and download their text."""
    api_key = get_api_key()
    
    # Load bills data
    with open(bills_file, 'r') as f:
        bills_data = json.load(f)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Track which bills were updated with text
    updated_bills = []
    
    # Process each bill
    for bill in bills_data['bills']:
        print(f"Processing {bill.get('type')}{bill.get('number')}...")
        
        # Download bill text
        text_info = download_bill_text(bill, output_dir, api_key)
        
        if text_info:
            # Add text info to bill data
            bill['text_info'] = text_info
        
        # Add bill to updated list regardless of whether it has text
        updated_bills.append(bill)
        
        # Be nice to the API
        time.sleep(1)
    
    # Update bills data with text info
    bills_data['bills'] = updated_bills
    
    # Save updated bills data
    with open(bills_file, 'w') as f:
        json.dump(bills_data, f, indent=2)
    
    print(f"Downloaded text for {len(updated_bills)} bills")

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    bills_file = data_dir / 'bills.json'
    text_dir = data_dir / 'bill_texts'
    
    process_bills(bills_file, text_dir)

if __name__ == "__main__":
    main()
