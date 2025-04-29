import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
from urllib.parse import urljoin

def scrape_documentation(base_url, output_dir):
    """Scrape documentation from a payment API provider website"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Scraping documentation from {base_url}...")

    # Get the main page
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {base_url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract links to documentation pages
    links = []
    visited_links = set()

    # Find all links in the main navigation that likely point to docs
    for a in soup.find_all('a', href=True):
        href = a['href']

        # Filter for documentation links based on common patterns
        if '/docs/' in href or '/reference/' in href or '/guides/' in href or '/api/' in href:
            # Handle relative URLs
            if href.startswith('/'):
                href = urljoin(base_url, href)
            elif not href.startswith('http'):
                href = urljoin(base_url, href)

            # Only add if not already in the list
            if href not in visited_links:
                links.append(href)
                visited_links.add(href)

    print(f"Found {len(links)} documentation links to process")

    # Process each documentation page
    for i, link in enumerate(links[:20]):  # Limit to first 20 for initial testing
        try:
            print(f"Processing {i+1}/{len(links)}: {link}")

            # Add delay to avoid rate limiting
            time.sleep(1)

            page_response = requests.get(link)
            page_response.raise_for_status()
            page_soup = BeautifulSoup(page_response.text, 'html.parser')

            # Extract content (You'll need to adapt this for each site)
            # Look for common content container classes
            content = None
            for selector in ['article', '.documentation', '.docs-content', '.content', 'main', '#main-content']:
                content = page_soup.select_one(selector)
                if content:
                    break

            if not content:
                content = page_soup.find('body')  # Fallback to body if no content container found

            # Extract code examples
            code_examples = []
            for code in page_soup.find_all(['pre', 'code']):
                code_examples.append(code.text)

            # Generate a safe filename from the URL
            filename = re.sub(r'[^\w]', '_', link.split('/')[-1])
            if not filename or filename.isspace():
                filename = f"doc_{i}"

            # Save content to file
            with open(os.path.join(output_dir, f"{filename}.json"), 'w') as f:
                json.dump({
                    'url': link,
                    'title': page_soup.title.text if page_soup.title else '',
                    'content': content.text.strip() if content else '',
                    'code_examples': code_examples
                }, f, indent=2)

            print(f"Saved {filename}.json")

        except Exception as e:
            print(f"Error processing {link}: {e}")

    print(f"Documentation scraping complete. Saved to {output_dir}")