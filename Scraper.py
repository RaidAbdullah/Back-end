from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import pandas as pd
import logging
import time
import json
import requests

class PropertyDealsScraper:
    def __init__(self, url):
        """Initialize the property deals scraper"""
        self.url = url
        self.BASE_URL = url
        self.page = None
        self.browser = None
        self.context = None
        self.data = []
        self.data2 = []  # Initialize second data list for category-included data
        
        # Set up logging
        logging.basicConfig(
            filename='property_scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def init_browser(self):
        """Initialize the browser with proper configuration"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu'
                ]
            )
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print("Browser initialized successfully")
        except Exception as e:
            print(f"Error initializing browser: {str(e)}")
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
            raise

    def cleanup(self):
        """Clean up browser resources"""
        try:
            if hasattr(self, 'page') and self.page:
                self.page.close()
            if hasattr(self, 'context') and self.context:
                self.context.close()
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, 'playwright') and self.playwright:
                self.playwright.stop()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")

    def fill_date_fields(self):
        """Fill the date input fields"""
        
        today = datetime.now()
        yesterday = today - timedelta(days=2)
        today_year = today.year
        today_month = today.month
        today_day = today.day
        yesterday_year = yesterday.year
        yesterday_month = yesterday.month
        yesterday_day = yesterday.day
        try:
            print("\nFilling date fields...")
            time.sleep(2)  # Wait before starting

            # From date fields
            print("Filling 'From' date...")
            self.page.locator("//div[@class='ant-row ant-row-start ant-row-middle ant-row-rtl datepicker-inputs']/div[1]/div[2]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/input[1]").click()
            self.page.keyboard.press('Control+a')
            time.sleep(0.5)
            self.page.keyboard.press('Delete')
            time.sleep(0.5)
            self.page.keyboard.type(str(yesterday_year), delay=100)  # Type slower
            time.sleep(1)
            
            self.page.locator("//div[@class='ant-row ant-row-start ant-row-middle ant-row-rtl datepicker-inputs']/div[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/input[1]").click()
            
            self.page.keyboard.press('Control+a')
            time.sleep(0.5)
            self.page.keyboard.press('Delete')
            time.sleep(0.5)
            self.page.keyboard.type(str(yesterday_month), delay=100)
            time.sleep(1)
            
            self.page.locator("//div[@class='ant-row ant-row-start ant-row-middle ant-row-rtl datepicker-inputs']/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/input[1]").click()
            
            self.page.keyboard.press('Control+a')
            time.sleep(0.5)
            self.page.keyboard.press('Delete')
            time.sleep(0.5)
            self.page.keyboard.type(str(yesterday_day), delay=100)
            

            print("Filling 'To' date...")
            # To date fields
            self.page.locator("//div[@class='ant-row ant-row-start ant-row-middle ant-row-rtl datepicker-inputs']/div[2]/div[2]/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/input[1]").click()
            
            self.page.keyboard.press('Control+a')
            time.sleep(0.5)
            self.page.keyboard.press('Delete')
            time.sleep(0.5)
            self.page.keyboard.type(str(today_year), delay=100)
            time.sleep(1)
            self.page.keyboard.press("Tab")
            self.page.keyboard.type("مدينة الرياض", delay=100)
            time.sleep(3)
            self.page.keyboard.press("Enter")
            
            
            self.page.locator("//div[@class='ant-row ant-row-start ant-row-middle ant-row-rtl datepicker-inputs']/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/input[1]").click()
            
            self.page.keyboard.press('Control+a')
            time.sleep(0.5)
            self.page.keyboard.press('Delete')
            time.sleep(0.5)
            self.page.keyboard.type(str(today_month), delay=100)
            
            
            self.page.locator("//div[@class='ant-row ant-row-start ant-row-middle ant-row-rtl datepicker-inputs']/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/span[1]/input[1]").click()
            
            self.page.keyboard.press('Control+a')
            time.sleep(0.5)
            self.page.keyboard.press('Delete')
            time.sleep(0.5)
            self.page.keyboard.type(str(today_day), delay=100)
            time.sleep(1)
            

            
            print("Date fields filled successfully")
            self.logger.info("Date fields filled successfully")
        except Exception as e:
            self.logger.error(f"Error filling date fields: {str(e)}")
            raise

    def extract_number(self, text):
        """Extract number from text"""
        try:
            return float(''.join(filter(str.isdigit, text)))
        except Exception as e:
            self.logger.error(f"Error extracting number: {str(e)}")
            return None

    def determine_property_category(self, price_per_meter):
        """Determine property category based on price per meter"""
        try:
            if price_per_meter < 1000:
                return "Low"
            elif price_per_meter < 2000:
                return "Medium"
            else:
                return "High"
        except Exception as e:
            self.logger.error(f"Error determining property category: {str(e)}")
            return None

    def scrape(self):
        """Main scraping function"""
        try:
            print("\nStarting the scraping process...")
            self.logger.info("Starting daily scrape")
            
            self.init_browser()
            
            # Navigate to URL and wait for load
            print("\nNavigating to website...")
            self.page.goto(self.BASE_URL)
            self.page.wait_for_load_state('networkidle')
            time.sleep(5)  # Additional wait for dynamic content
            
            # Fill date fields
            self.fill_date_fields()
            
            # Click search button and wait for results
            print("\nSearching for properties...")
            search_button = self.page.locator('button:has-text("بحث")')
            search_button.click()
            time.sleep(5)  # Wait for results to load
            
            # Extract property data
            print("\nExtracting property data...")
            property_data = []
            property_data_with_category = []
            
            # Get all property rows
            rows = self.page.locator('tbody tr').all()
            
            for row in rows:
                try:
                    # Extract data from each row
                    cells = row.locator('td').all()
                    
                    if len(cells) >= 6:  # Ensure we have enough cells
                        property_info = {
                            'district': cells[1].inner_text().strip(),
                            'price': self.extract_number(cells[2].inner_text()),
                            'area': self.extract_number(cells[3].inner_text()),
                            'price_per_meter': self.extract_number(cells[4].inner_text()),
                            'date': cells[5].inner_text().strip(),
                        }
                        
                        # Add to list without category
                        property_data.append(property_info)
                        
                        # Add category and append to second list
                        property_info_with_category = property_info.copy()
                        property_info_with_category['category'] = self.determine_property_category(
                            property_info['price_per_meter']
                        )
                        property_data_with_category.append(property_info_with_category)
                        
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    continue
            
            print(f"\nSuccessfully extracted {len(property_data)} properties")
            return property_data, property_data_with_category
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            self.logger.error(f"Error during scraping: {str(e)}")
            raise
        finally:
            self.cleanup()

    def click_search(self):
        """Click the search button"""
        try:
            print("\nClicking search button...")
            time.sleep(2)
            
            try:
                # Try multiple selectors for the search button
                selectors = [
                    "//button[@class='ant-btn ant-btn-primary ant-btn-rtl ant-btn-primary ant-btn-primary--success']/span[1]",
                    "//button[contains(@class, 'ant-btn-primary')]//span[contains(text(), 'بحث')]/..",
                    "//button[contains(@class, 'ant-btn')]//span[contains(text(), 'بحث')]/.."
                ]
                
                search_button = None
                for selector in selectors:
                    try:
                        search_button = self.page.locator(selector).first
                        if search_button.is_visible():
                            break
                    except:
                        continue
                
                if search_button and search_button.is_visible():
                    # Scroll to button and click
                    search_button.scroll_into_view_if_needed()
                    time.sleep(1)
                    search_button.click()
                    print("Search button clicked, waiting for results...")
                    time.sleep(5)
                    self.logger.info("Search button clicked successfully")
                else:
                    print("Warning: Could not find search button")
                    self.logger.warning("Could not find search button")
            except Exception as e:
                print(f"Warning: Error clicking search button: {str(e)}")
                self.logger.warning(f"Error clicking search button: {str(e)}")
            
        except Exception as e:
            print(f"Error in click_search: {str(e)}")
            self.logger.error(f"Error in search button handling: {str(e)}")
            # Don't raise the exception, continue with the script

    def _get_quarter(self, date_str):
        """Convert date to quarter format (e.g., Q223 for 2022 Q3)"""
        try:
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            year_short = str(date_obj.year)[2:]  # Get last 2 digits of year
            quarter = (date_obj.month - 1) // 3 + 1  # Calculate quarter (1-4)
            return f"Q{year_short}{quarter}"
        except Exception as e:
            self.logger.error(f"Error calculating quarter from date {date_str}: {e}")
            return None

def main():
    """Main function to run the scraper"""
    website_url = "https://srem.moj.gov.sa/transactions-info"
    scraper = PropertyDealsScraper(website_url)
    data, data2 = scraper.scrape()
    
    # Save data to JSON files
    with open('property_results.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    with open('property_results_with_category.json', 'w', encoding='utf-8') as f:
        json.dump(data2, f, ensure_ascii=False, indent=4)
        
    print(f"Results saved to property_results.json")
    
    print("\nScraping completed. Press Enter to close the browser...")
    input()

if __name__ == "__main__":
    main()