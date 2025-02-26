#!/usr/bin/env python3
"""
Script to summarize bills using Hugging Face API.
"""
import os
import json
from pathlib import Path
import requests

class HuggingFaceAPI:
    def __init__(self):
        self.api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not self.api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
        self.api_url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def summarize_text(self, text):
        """Generate a summary using the BART model."""
        payload = {"inputs": text, "parameters": {"max_length": 300, "min_length": 100}}
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()[0]['summary_text']

def process_bills(raw_dir, processed_dir):
    """Process all raw bills and generate summaries."""
    raw_dir = Path(raw_dir)
    processed_dir = Path(processed_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    api = HuggingFaceAPI()
    
    for bill_file in raw_dir.glob("*.json"):
        try:
            # Read raw bill
            with open(bill_file) as f:
                bill_data = json.load(f)
            
            # Extract text to summarize
            text = bill_data.get('title', '') + "\n" + bill_data.get('summary', '')
            if not text.strip():
                continue
                
            # Generate summary
            summary = api.summarize_text(text)
            
            # Save processed bill with summary
            bill_data['ai_summary'] = summary
            output_file = processed_dir / bill_file.name
            with open(output_file, 'w') as f:
                json.dump(bill_data, f, indent=2)
                
            print(f"Processed {bill_file.name}")
            
        except Exception as e:
            print(f"Error processing {bill_file}: {e}")

def main():
    data_dir = Path(__file__).parent.parent / "data"
    raw_bills_dir = data_dir / "raw_bills"
    processed_bills_dir = data_dir / "processed_bills"
    
    process_bills(raw_bills_dir, processed_bills_dir)

if __name__ == "__main__":
    main()
