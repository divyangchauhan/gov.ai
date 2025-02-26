#!/usr/bin/env python3
"""
Script to generate static HTML pages from processed bills.
"""
import json
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def load_bills(processed_dir):
    """Load all processed bills and sort by date."""
    bills = []
    for bill_file in Path(processed_dir).glob("*.json"):
        with open(bill_file) as f:
            bill_data = json.load(f)
            bills.append(bill_data)
    
    # Sort bills by date
    return sorted(bills, key=lambda x: x.get('updateDate', ''), reverse=True)

def generate_site(bills, template_dir, output_dir):
    """Generate static HTML pages from bill data."""
    env = Environment(loader=FileSystemLoader(template_dir))
    
    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate index page
    template = env.get_template('index.html')
    index_html = template.render(
        bills=bills,
        generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    with open(output_dir / 'index.html', 'w') as f:
        f.write(index_html)
    
    # Generate individual bill pages
    bill_template = env.get_template('bill.html')
    for bill in bills:
        bill_html = bill_template.render(
            bill=bill,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        bill_file = output_dir / f"bill_{bill.get('billNumber', 'unknown')}.html"
        with open(bill_file, 'w') as f:
            f.write(bill_html)

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    processed_bills_dir = data_dir / "processed_bills"
    template_dir = base_dir / "templates"
    site_dir = base_dir / "site"
    
    bills = load_bills(processed_bills_dir)
    generate_site(bills, template_dir, site_dir)
    print(f"Generated site with {len(bills)} bills")

if __name__ == "__main__":
    main()
