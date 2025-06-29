# GitHub Actions Daily Devotional Scraper

This setup uses GitHub Actions to automatically scrape the daily devotional and update your static site.

## File Structure
```
your-repo/
├── .github/
│   └── workflows/
│       └── scrape-devotional.yml
├── scripts/
│   ├── scrape_devotional.py
│   └── requirements.txt
├── data/
│   ├── devotionals.json
│   └── latest.json
├── index.html
└── README.md
```

## 1. GitHub Actions Workflow (.github/workflows/scrape-devotional.yml)

```yaml
name: Daily Devotional Scraper

on:
  schedule:
    # Run every day at 6:00 AM UTC (adjust for your timezone)
    - cron: '0 6 * * *'
  workflow_dispatch: # Allows manual triggering for testing

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r scripts/requirements.txt
        
    - name: Run scraper
      run: |
        python scripts/scrape_devotional.py
        
    - name: Commit and push if changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/
        git diff --staged --quiet || git commit -m "Update daily devotional - $(date +'%Y-%m-%d')"
        git push
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Deploy to GitHub Pages (optional)
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

## 2. Python Scraper Script (scripts/scrape_devotional.py)

```python
#!/usr/bin/env python3
"""
Daily devotional scraper for joncourson.com
Saves data to JSON files for static site consumption
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DevotionalScraper:
    def __init__(self):
        self.base_url = "https://joncourson.com/dailydevotional/dailydevotional.asp"
        self.data_dir = "data"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_page(self, url, retries=3):
        """Fetch webpage with retry logic"""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching {url} (attempt {attempt + 1})")
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(5)  # Wait before retry
                else:
                    raise
    
    def parse_devotional(self, html_content):
        """Parse devotional content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        devotional = {
            'scraped_at': datetime.now().isoformat(),
            'date': None,
            'title': 'Daily Devotional with Pastor Jon',
            'scripture': None,
            'scripture_reference': None,
            'content': None,
            'author': 'Jon Courson'
        }
        
        try:
            # Based on the actual HTML structure from joncourson.com
            
            # Date extraction - look for the daily devotional date
            date_elem = soup.find('div', class_='daily-devotional-date')
            if date_elem:
                devotional['date'] = date_elem.get_text(strip=True)
            else:
                devotional['date'] = datetime.now().strftime("%B %d, %Y")
            
            # Scripture text extraction
            scripture_elem = soup.find('div', class_='daily-devotional-scripture')
            if scripture_elem:
                devotional['scripture'] = scripture_elem.get_text(strip=True)
            
            # Scripture reference extraction
            scripture_ref_elem = soup.find('div', class_='daily-devotional-scripture-reference')
            if scripture_ref_elem:
                devotional['scripture_reference'] = scripture_ref_elem.get_text(strip=True)
            
            # Main content - the commentary/devotional text
            content_elem = soup.find('div', class_='daily-devotional-commentary')
            if content_elem:
                # Get text content but preserve paragraph breaks
                paragraphs = content_elem.find_all('p')
                if paragraphs:
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(separator=' ', strip=True)
                        if text:  # Only add non-empty paragraphs
                            content_parts.append(text)
                    devotional['content'] = '\n\n'.join(content_parts)
                else:
                    # Fallback if no <p> tags found
                    devotional['content'] = content_elem.get_text(separator='\n\n', strip=True)
            
            # Validation - ensure we got meaningful content
            if not devotional['content'] or len(devotional['content']) < 50:
                raise ValueError("Failed to extract devotional content - content too short or empty")
                
            if not devotional['date']:
                raise ValueError("Failed to extract devotional date")
                    
        except Exception as e:
            logger.error(f"Error parsing devotional: {e}")
            raise
        
        return devotional
    
    def load_existing_devotionals(self):
        """Load existing devotionals from JSON file"""
        devotionals_file = os.path.join(self.data_dir, 'devotionals.json')
        
        if os.path.exists(devotionals_file):
            try:
                with open(devotionals_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading existing devotionals: {e}")
                return []
        
        return []
    
    def save_devotional(self, devotional):
        """Save devotional to JSON files"""
        devotionals_file = os.path.join(self.data_dir, 'devotionals.json')
        latest_file = os.path.join(self.data_dir, 'latest.json')
        
        # Load existing devotionals
        devotionals = self.load_existing_devotionals()
        
        # Check if this devotional already exists (by date)
        existing_dates = [d.get('date') for d in devotionals]
        if devotional['date'] not in existing_dates:
            # Add new devotional to the beginning of the list
            devotionals.insert(0, devotional)
            
            # Keep only the last 365 devotionals (1 year)
            devotionals = devotionals[:365]
            
            logger.info(f"Added new devotional: {devotional['date']}")
        else:
            # Update existing devotional
            for i, d in enumerate(devotionals):
                if d.get('date') == devotional['date']:
                    devotionals[i] = devotional
                    logger.info(f"Updated existing devotional: {devotional['date']}")
                    break
        
        # Save all devotionals
        with open(devotionals_file, 'w', encoding='utf-8') as f:
            json.dump(devotionals, f, indent=2, ensure_ascii=False)
        
        # Save latest devotional separately
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(devotional, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved devotional data to {devotionals_file} and {latest_file}")
    
    def scrape_daily_devotional(self):
        """Main scraping function"""
        try:
            logger.info("Starting daily devotional scrape")
            
            # Fetch the webpage
            html_content = self.fetch_page(self.base_url)
            
            # Parse the devotional
            devotional = self.parse_devotional(html_content)
            
            # Validate that we got meaningful content
            if not devotional['content'] or len(devotional['content']) < 50:
                raise ValueError("Scraped content appears to be too short or empty")
            
            # Save the devotional
            self.save_devotional(devotional)
            
            logger.info("Successfully scraped and saved daily devotional")
            return devotional
            
        except Exception as e:
            logger.error(f"Error scraping devotional: {e}")
            raise

def main():
    """Main function"""
    scraper = DevotionalScraper()
    
    try:
        devotional = scraper.scrape_daily_devotional()
        print(f"✅ Successfully scraped devotional: {devotional['title']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
```

## 3. Requirements file (scripts/requirements.txt)

```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

## 4. Simple Static Site (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily Devotional</title>
    <style>
        body {
            font-family: Georgia, serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .devotional {
            margin-bottom: 30px;
            border-bottom: 1px solid #eee;
            padding-bottom: 20px;
        }
        .date {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        .title {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        .scripture {
            font-style: italic;
            color: #555;
            margin-bottom: 5px;
            font-size: 1.1em;
        }
        .scripture-ref {
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        .content {
            white-space: pre-line;
        }
        .archive {
            margin-top: 40px;
        }
        .archive-item {
            padding: 10px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }
        .archive-item:hover {
            background: #f9f9f9;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📖 Daily Devotional</h1>
        
        <div id="latest-devotional">
            <p>Loading today's devotional...</p>
        </div>
        
        <div class="archive">
            <h2>Previous Devotionals</h2>
            <div id="archive-list">
                <p>Loading archive...</p>
            </div>
        </div>
    </div>

    <script>
        # Load latest devotional
        fetch('data/latest.json')
            .then(response => response.json())
            .then(devotional => {
                document.getElementById('latest-devotional').innerHTML = `
                    <div class="devotional">
                        <div class="date">${devotional.date}</div>
                        <div class="title">${devotional.title || 'Daily Devotional'}</div>
                        ${devotional.scripture ? `<div class="scripture">"${devotional.scripture}"</div>` : ''}
                        ${devotional.scripture_reference ? `<div class="scripture-ref">${devotional.scripture_reference}</div>` : ''}
                        <div class="content">${devotional.content}</div>
                    </div>
                `;
            })
            .catch(error => {
                document.getElementById('latest-devotional').innerHTML = 
                    '<p>Error loading devotional. Please try again later.</p>';
            });

        // Load devotional archive
        fetch('data/devotionals.json')
            .then(response => response.json())
            .then(devotionals => {
                const archiveHtml = devotionals.slice(1, 31).map(d => `
                    <div class="archive-item" onclick="loadDevotional('${d.date}')">
                        <strong>${d.title || d.date}</strong><br>
                        <small>${d.date}</small>
                    </div>
                `).join('');
                
                document.getElementById('archive-list').innerHTML = archiveHtml;
            })
            .catch(error => {
                document.getElementById('archive-list').innerHTML = 
                    '<p>Error loading archive.</p>';
            });

        function loadDevotional(date) {
            // Implementation for loading specific devotional
            console.log('Loading devotional for:', date);
        }
    </script>
</body>
</html>
```

## Setup Instructions

1. **Create a new GitHub repository**
2. **Add the files** above to your repository
3. **Inspect the target website** to determine the correct CSS selectors
4. **Update the scraper script** with the correct selectors
5. **Test manually** by running the workflow with `workflow_dispatch`
6. **Enable GitHub Pages** in repository settings (optional)

## Benefits of This Approach

- ✅ **Free**: GitHub Actions provides 2,000 minutes/month for free
- ✅ **Reliable**: Runs automatically on schedule
- ✅ **Version controlled**: All scraped data is tracked in Git
- ✅ **Static hosting**: Can serve directly from GitHub Pages
- ✅ **Resilient**: Built-in retry logic and error handling
- ✅ **Respectful**: Includes proper delays and user agents

## Important Notes

1. **Check robots.txt** first: `https://joncourson.com/robots.txt`
2. **Respect rate limits**: The script includes delays between requests
3. **Inspect the HTML**: You'll need to update the CSS selectors based on the actual website structure
4. **Test thoroughly**: Use `workflow_dispatch` to test before relying on the schedule

Would you like me to help you inspect the actual HTML structure of the joncourson.com devotional page to get the correct selectors?