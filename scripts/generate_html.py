#!/usr/bin/env python3
"""
Script to generate HTML files from bill data.
"""
import json
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def load_processed_bills(processed_dir):
    """Load all processed bills with AI summaries."""
    processed_bills = {}
    processed_dir = Path(processed_dir)
    
    for bill_file in processed_dir.glob("*.json"):
        with open(bill_file) as f:
            bill_data = json.load(f)
            # Use type and number as key
            bill_id = f"{bill_data['type'].lower()}{bill_data['number']}"
            processed_bills[bill_id] = bill_data.get('ai_summary')
    
    return processed_bills

def load_bills(bills_file):
    """Load bills from the JSON file."""
    with open(bills_file, 'r') as f:
        return json.load(f)

def generate_html_files(bills_data, processed_bills, templates_dir, output_dir, base_dir):
    """Generate HTML files for each bill and an index page."""
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate individual bill pages
    bill_template = env.get_template('bill.html')
    bill_text_template = env.get_template('bill_text.html')
    
    for bill in bills_data['bills']:
        bill_id = f"{bill['type'].lower()}{bill['number']}"
        # Add AI summary to bill data
        bill['ai_summary'] = processed_bills.get(bill_id)
        
        # Generate bill summary page
        output_file = output_dir / f"bill_{bill_id}.html"
        with open(output_file, 'w') as f:
            html_content = bill_template.render(bill=bill)
            f.write(html_content)
        
        # Generate bill text page if text is available
        if 'text_info' in bill and bill['text_info']:
            bill_text_path = base_dir / bill['text_info']['path']
            
            try:
                with open(bill_text_path, 'r', encoding='utf-8') as f:
                    bill_text = f.read()
                
                output_text_file = output_dir / f"bill_text_{bill_id}.html"
                with open(output_text_file, 'w') as f:
                    html_content = bill_text_template.render(
                        bill=bill,
                        bill_text=bill_text
                    )
                    f.write(html_content)
            except Exception as e:
                print(f"Error generating text page for {bill_id}: {e}")
    
    # Generate index page
    index_template = env.get_template('index.html')
    with open(output_dir / 'index.html', 'w') as f:
        html_content = index_template.render(
            bills=bills_data['bills'],
            generated_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        f.write(html_content)

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    bills_file = data_dir / 'bills.json'
    templates_dir = base_dir / 'templates'
    output_dir = base_dir / 'public'
    processed_dir = data_dir / 'processed_bills'
    
    bills_data = load_bills(bills_file)
    processed_bills = load_processed_bills(processed_dir)
    generate_html_files(bills_data, processed_bills, templates_dir, output_dir, base_dir)
    print("Successfully generated HTML files with AI summaries and bill texts")

if __name__ == "__main__":
    main()
