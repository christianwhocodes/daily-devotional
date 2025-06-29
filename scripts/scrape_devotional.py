#!/usr/bin/env python3
"""
Daily devotional scraper for joncourson.com
Saves data to JSON files for static site consumption
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DevotionalScraper:
    def __init__(self):
        self.base_url = "https://joncourson.com/"
        self.data_dir = Path("data")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)

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
        soup = BeautifulSoup(html_content, "html.parser")

        devotional = {
            "scraped_at": datetime.now().isoformat(),
            "date": None,
            "title": "Daily Devotional with Pastor Jon",
            "scripture": None,
            "scripture_reference": None,
            "content": None,
            "author": "Jon Courson",
        }

        try:
            # Based on the actual HTML structure from joncourson.com

            # Date extraction - look for the daily devotional date
            date_elem = soup.find("div", class_="daily-devotional-date")
            if date_elem:
                devotional["date"] = date_elem.get_text(strip=True)
            else:
                devotional["date"] = datetime.now().strftime("%B %d, %Y")

            # Scripture text extraction
            scripture_elem = soup.find("div", class_="daily-devotional-scripture")
            if scripture_elem:
                devotional["scripture"] = scripture_elem.get_text(strip=True)

            # Scripture reference extraction
            scripture_ref_elem = soup.find(
                "div", class_="daily-devotional-scripture-reference"
            )
            if scripture_ref_elem:
                devotional["scripture_reference"] = scripture_ref_elem.get_text(
                    strip=True
                )

            # Main content - the commentary/devotional text
            content_elem = soup.find("div", class_="daily-devotional-commentary")
            if content_elem:
                # Get text content but preserve paragraph breaks
                paragraphs = content_elem.find_all("p")
                if paragraphs:
                    content_parts = []
                    for p in paragraphs:
                        text = p.get_text(separator=" ", strip=True)
                        if text:  # Only add non-empty paragraphs
                            content_parts.append(text)
                    devotional["content"] = "\n\n".join(content_parts)
                else:
                    # Fallback if no <p> tags found
                    devotional["content"] = content_elem.get_text(
                        separator="\n\n", strip=True
                    )

            # Validation - ensure we got meaningful content
            if not devotional["content"] or len(devotional["content"]) < 50:
                raise ValueError(
                    "Failed to extract devotional content - content too short or empty"
                )

            if not devotional["date"]:
                raise ValueError("Failed to extract devotional date")

        except Exception as e:
            logger.error(f"Error parsing devotional: {e}")
            raise

        return devotional

    def load_existing_devotionals(self):
        """Load existing devotionals from JSON file"""
        devotionals_file = self.data_dir / "devotionals.json"

        if devotionals_file.exists():
            try:
                with devotionals_file.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Error loading existing devotionals: {e}")
                return []

        return []

    def save_devotional(self, devotional):
        """Save devotional to JSON files"""
        devotionals_file = self.data_dir / "devotionals.json"
        latest_file = self.data_dir / "latest.json"

        # Load existing devotionals
        devotionals = self.load_existing_devotionals()

        # Check if this devotional already exists (by date)
        existing_dates = [d.get("date") for d in devotionals]
        if devotional["date"] not in existing_dates:
            # Add new devotional to the beginning of the list
            devotionals.insert(0, devotional)

            # Keep only the last 365 devotionals (1 year)
            devotionals = devotionals[:365]

            logger.info(f"Added new devotional: {devotional['date']}")
        else:
            # Update existing devotional
            for i, d in enumerate(devotionals):
                if d.get("date") == devotional["date"]:
                    devotionals[i] = devotional
                    logger.info(f"Updated existing devotional: {devotional['date']}")
                    break

        # Save all devotionals
        with devotionals_file.open("w", encoding="utf-8") as f:
            json.dump(devotionals, f, indent=2, ensure_ascii=False)

        # Save latest devotional separately
        with latest_file.open("w", encoding="utf-8") as f:
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
            if not devotional["content"] or len(devotional["content"]) < 50:
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
