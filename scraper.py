from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager  # Add this import
import time
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import keyboard

class WebsiteAutomation:
    def __init__(self, url):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Maximize window
        chrome_options.add_experimental_option("detach", True)  # Keep browser open
        
        # Initialize the Chrome WebDriver with automatic driver management
        #service = Service(ChromeDriverManager().install())
        service = Service("./chromedriver.exe")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 10)  # Wait up to 10 seconds
        self.url = url
        
        # Navigate to the URL
        self.driver.get(self.url)
        
        # Create saves directory if it doesn't exist
        self.saves_dir = "webpage_saves"
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)
        
        # Set up keyboard shortcut for saving
        keyboard.add_hotkey('ctrl+s', self.save_current_page)
        
    def login(self, username, password):
        try:
            self.driver.get(self.url)
            
            # Wait for login form elements to be present
            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))  # Update selector
            )
            password_field = self.driver.find_element(By.ID, "password")  # Update selector
            
            # Enter credentials
            username_field.send_keys(username)
            password_field.send_keys(password)
            password_field.send_keys(Keys.RETURN)
            
            # Wait for login to complete
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "logged-in-indicator"))  # Update selector
            )
            
            # Save cookies to maintain login state
            cookies = self.driver.get_cookies()
            with open("cookies.json", "w") as f:
                json.dump(cookies, f)
                
        except Exception as e:
            print(f"Login failed: {str(e)}")
    
    def save_current_page(self):
        """Save the current webpage with all its resources"""
        try:
            # Get current page URL and title
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # Create timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create a safe filename from the title
            safe_title = "".join(c for c in page_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Create directory for this save
            save_dir = os.path.join(self.saves_dir, f"{safe_title}_{timestamp}")
            os.makedirs(save_dir)
            
            # Save full page HTML
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Save page info
            page_info = {
                "original_url": current_url,
                "title": page_title,
                "save_date": timestamp,
            }
            with open(os.path.join(save_dir, "page_info.json"), "w", encoding="utf-8") as f:
                json.dump(page_info, f, indent=4, ensure_ascii=False)
            
            # Save the HTML file
            html_file = os.path.join(save_dir, "page.html")
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            
            # Take a screenshot
            self.driver.save_screenshot(os.path.join(save_dir, "screenshot.png"))
            
            print(f"Page saved successfully to: {save_dir}")
            
            # Create an HTML summary file
            self._create_summary_file(save_dir, page_info)
            
        except Exception as e:
            print(f"Failed to save page: {str(e)}")
    
    def _create_summary_file(self, save_dir, page_info):
        """Create a summary HTML file for easier viewing"""
        summary_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Saved Page Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .info {{ margin-bottom: 20px; }}
                .preview {{ margin-top: 20px; }}
                img {{ max-width: 100%; border: 1px solid #ccc; }}
            </style>
        </head>
        <body>
            <h1>Saved Page Summary</h1>
            <div class="info">
                <p><strong>Original URL:</strong> <a href="{page_info['original_url']}">{page_info['original_url']}</a></p>
                <p><strong>Title:</strong> {page_info['title']}</p>
                <p><strong>Save Date:</strong> {page_info['save_date']}</p>
            </div>
            <div class="preview">
                <h2>Screenshot Preview</h2>
                <img src="screenshot.png" alt="Page Screenshot">
            </div>
            <p><a href="page.html">View Saved HTML</a></p>
        </body>
        </html>
        """
        with open(os.path.join(save_dir, "summary.html"), "w", encoding="utf-8") as f:
            f.write(summary_html)
    
    def load_cookies(self):
        try:
            with open("cookies.json", "r") as f:
                cookies = json.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            self.driver.refresh()
        except FileNotFoundError:
            print("No saved cookies found")
            
    def search(self, query):
        try:
            # Wait for Google search box and enter query
            search_box = self.wait.until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to load and find Jobs tab
            jobs_tab = self.wait.until(
                EC.presence_of_element_located((By.LINK_TEXT, "Jobs"))
            )
            jobs_tab.click()
            
            # Wait for jobs results to load
            time.sleep(2)  # Give time for jobs page to load
            
        except Exception as e:
            print(f"Search failed: {str(e)}")
            
    def scroll_results(self, scroll_pause_time=2.0):
        """Scroll through results page to bottom and back to top, then click save buttons."""
        try:
            # Get scroll height
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            print("Scrolling down...")
            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait to load page
                time.sleep(scroll_pause_time)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            print("Reached bottom, scrolling back up...")
            # Smooth scroll back to top
            self.driver.execute_script("""
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            """)
            time.sleep(scroll_pause_time)  # Wait for scroll up animation
            print("Scrolling complete")

            # Find all jsslot divs -----------------------------------------------------------------------------------------------
            print("Finding job listings...")
            jsslot_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[jsslot]")
            
            # Extract text and click through each job listing
            print("Processing job listings...")
            job_listings = []
            excluded_texts = [
                "Remote\nNo degree\nDate posted\nJob type",
                "Job postings",
                "Saved jobs",
                "Following"
            ]
            
            for jsslot in jsslot_elements:
                try:
                    # Get text content of the jsslot element
                    text = jsslot.text.strip()
                    # Get additional text from specific class elements
                    position_title = jsslot.find_element(By.CLASS_NAME, "tNxQIb.PUpOsf").text.strip()
                    company = jsslot.find_element(By.CLASS_NAME, "wHYlTd.MKCbgd.a3jPc").text.strip()
                    if text and text not in excluded_texts:  # Only include non-empty and non-excluded text
                        # Click the job listing
                        jsslot.click()
                        # Wait for job description to load
                        time.sleep(2)
                        
                        job_listings.append({
                            "listing_text": text,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        print(text)
                        print('--------------------------------------------------------------------------------------')
                        
                except Exception as e:
                    print(f"Error processing listing: {str(e)}")
                    continue
            
            # Save to JSON file
            with open("job_listings.json", "w", encoding="utf-8") as f:
                json.dump({
                    "job_listings": job_listings,
                    "total_count": len(job_listings),
                    "extraction_date": datetime.now().isoformat()
                }, f, indent=4, ensure_ascii=False)
            
            print(f"Job listing texts saved to job_listings.json ({len(job_listings)} listings)")

            
        except Exception as e:
            print(f"Error during scrolling or saving: {str(e)}")
            
    def save_results(self, criteria, output_file):
        try:
            # Find all result elements
            results = self.driver.find_elements(By.CLASS_NAME, "result-item")  # Update selector
            
            saved_results = []
            for result in results:
                # Add your criteria to filter results
                if criteria in result.text:
                    saved_results.append({
                        "title": result.find_element(By.CLASS_NAME, "title").text,  # Update selector
                        "description": result.find_element(By.CLASS_NAME, "description").text,  # Update selector
                        "link": result.find_element(By.TAG_NAME, "a").get_attribute("href")
                    })
                    
            # Save to file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(saved_results, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            print(f"Saving results failed: {str(e)}")
            
    def close(self):
        keyboard.unhook_all()  # Remove keyboard listener
        self.driver.quit()

# Example usage
def main():
    # Initialize automation
    bot = WebsiteAutomation("https://www.google.com")
    
    print("Page saving enabled - Press Ctrl+S to save the current page")
    
    # Perform search for AI jobs
    bot.search("trustworthy ai jobs")
    
    # Scroll through results and process each job listing
    bot.scroll_results()
    
    # Keep browser open, close when done
    input("Press Enter to close the browser...")
    bot.close()

if __name__ == "__main__":
    main()
