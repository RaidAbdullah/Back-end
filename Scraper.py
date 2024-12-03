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

    def fill_location_and_price(self):
        """Fill location and price fields"""
        try:
            print("\nFilling location and price...")
            time.sleep(2)

            # Scroll down to make sure price field is visible
            print("Scrolling down...")
            self.page.evaluate("window.scrollTo(0, window.innerHeight)")
            time.sleep(2)

            # Price field
            print("Setting minimum price...")
            try:
                price_input = self.page.locator("//div[@class='RealestateInfoTransactionFilter']/div[1]/div[4]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[1]/span[1]/input[1]").first
                price_input.click()
                time.sleep(1)
                price_input.fill("1")
                time.sleep(1)
                self.page.keyboard.press("Enter")
                time.sleep(1)
                print("Price filled successfully")
            except Exception as e:
                print(f"Warning: Could not fill price: {str(e)}")
                self.logger.warning(f"Could not fill price: {str(e)}")
            
            print("Location and price fields handling completed")
            self.logger.info("Location and price fields handling completed")
        except Exception as e:
            print(f"Error in fill_location_and_price: {str(e)}")
            self.logger.error(f"Error filling location and price: {str(e)}")

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

    def scrape(self):
        """Main scraping function"""
        try:
            print("\nStarting the scraping process...")
            self.logger.info("Starting daily scrape")
            
            self.init_browser()
            
            # Navigate to URL and wait for load
            print("\nNavigating to website...")
            self.page.goto(self.url)
            self.page.wait_for_load_state('networkidle')
            time.sleep(5)  # Additional wait for dynamic content
            
            # Fill all fields
            self.fill_date_fields()
            time.sleep(2)
            self.fill_location_and_price()
            time.sleep(2)
            self.click_search()
            
            print("\nWaiting for results to load...")
            time.sleep(5)

            # Scroll multiple times to load all results
            for _ in range(5):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)  # Wait for content to load after each scroll

            # Initialize results lists
            self.data = []
            self.data2 = []

            # Scrape the cards
            print("\nScraping property cards...")
            
            # Get all cards using the correct selector
            cards_locator = self.page.locator('//ul[@class="ant-list-items"]/a/div[1]')
            cards = cards_locator.all()
            card_count = cards_locator.count()
            print(f"\nFound {card_count} property cards")

            for i, card in enumerate(cards, 1):
                try:
                    # Get all text content from the card
                    card_text = card.inner_text()
                    
                    # Split the text content by newlines and clean up
                    text_parts = [part.strip() for part in card_text.split('\n') if part.strip()]
                    
                    # Map the text parts to their respective fields
                    data = {}
                    data2={}
                    if len(text_parts) == 16:  # without Category
                        if text_parts[3] != "صفقة":
                         continue
                        data = {
                            "DISTRICT": text_parts[0].replace("الرياض ,", "").strip(),  # District name without "الرياض ,"
                            "transaction_type": text_parts[2],  # Transaction type
                            "price": text_parts[8], # Transaction price
                            "meter_price": text_parts[11],      # Price per meter
                            "date": text_parts[13],            # Date
                            "area": text_parts[16],             # Area
                            "quarter": self._get_quarter(text_parts[13])
                        }
                        self.data.append(data)
                    elif len(text_parts) == 17:  # with Category
                        if text_parts[3] != "صفقة":
                         continue
                        data2 = {
                            "DISTRICT": text_parts[0].replace("الرياض ,", "").strip(),          # District name
                            "Category": text_parts[1],         # Category
                            "transaction_type": text_parts[3],  # Transaction type
                            "price": text_parts[9], # Transaction price
                            "meter_price": text_parts[12],      # Price per meter
                            "date": text_parts[14],            # Date
                            "area": text_parts[17],             # Area
                            "quarter": self._get_quarter(text_parts[14])
                        }
                        self.data2.append(data2)
                    
                    print(f"Successfully scraped card {i}")
                except Exception as e:
                    print(f"Error scraping card {i}: {e}")
                    self.logger.error(f"Error scraping card {i}: {e}")

            print("\nScraping completed successfully")
            self.logger.info("Scraping completed successfully")
            
            # Return both datasets
            return self.data, self.data2
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            print(f"\nError occurred: {str(e)}")
        finally:
            self.cleanup()

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