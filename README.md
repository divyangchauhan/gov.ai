# Gov.AI - Automated Bill Tracking and Summarization

This project automatically fetches, summarizes, and publishes information about new government bills using AI. The system runs daily using GitHub Actions and publishes results to GitHub Pages.

## Features

- Daily automatic fetching of new bills from Congress.gov API
- AI-powered bill summarization using Hugging Face models
- Static site generation for easy browsing of bill summaries
- Fully automated pipeline using GitHub Actions
- Zero-cost hosting using GitHub Pages

## Setup

1. Set up required API keys:
   - Congress.gov API key
   - Hugging Face API token

2. Configure GitHub repository:
   - Enable GitHub Pages
   - Add API keys as repository secrets

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export CONGRESS_API_KEY=your_key_here
   export HUGGINGFACE_API_KEY=your_key_here
   ```

3. Run the pipeline:
   ```bash
   # Fetch new bills from Congress.gov API
   python scripts/fetch_bills.py

   # Generate AI summaries
   python scripts/summarize_bills.py
   
   # Download full bill texts (when available)
   python scripts/download_bill_text.py

   # Generate HTML files
   python scripts/generate_html.py

   # Start local development server
   cd public && python -m http.server 8000
   ```

   Then visit http://localhost:8000 to view the site.

## Architecture

- `scripts/`: Python scripts for fetching and processing bills
- `templates/`: HTML templates for static site generation
- `public/`: Generated static site content
- `.github/workflows/`: GitHub Actions workflow configurations

## License

MIT License
