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
from selenium.common.exceptions import NoSuchElementException

class WebsiteAutomation:
    def __init__(self, url):
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")  # Maximize window
        chrome_options.add_experimental_option("detach", True)  # Keep browser open
        
        # Initialize instance variables
        self.last_search_query = ""
        
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
            # Store the search query
            self.last_search_query = query
            
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
                    location = jsslot.find_element(By.CLASS_NAME, "wHYlTd.FqK3wc.MKCbgd").text.strip()
                    if text and text not in excluded_texts:  # Only include non-empty and non-excluded text
                        # Click the job listing
                        jsslot.click()
                        # Wait for job description to load
                        time.sleep(2)
                        
                       
                        print('--------------------------------------------------------------------------------------') 
                        print(text)
                        print("***")
                        print(position_title)
                        print("***")
                        print(company)
                        print("***")
                        print(location)
                       

                        
                        # Find and print job details from c-wiz element ----------------------------
                        try:
                            # Find all c-wiz elements
                            c_wiz_elements = self.driver.find_elements(By.TAG_NAME, "c-wiz")
                            # Look for the one with matching aria-label
                            for c_wiz in c_wiz_elements:
                                aria_label = c_wiz.get_attribute("aria-label")
                                if aria_label and aria_label.startswith("Job details for") and position_title in aria_label:
                                    print("\nProcessing next job ...:")
                                    #print(c_wiz.text)
                                    #print('----------------------------------------')
                                    
                                    # Try to find and click "More job highlights"
                                    try:
                                        time.sleep(1)
                                        more_highlights = c_wiz.find_element(By.XPATH, ".//null[text()='More job highlights']")
                                        # self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_highlights)
                                        # time.sleep(1)
                                        more_highlights.click()
                                        print('Clicked More Job Highlights for {position_title} ==================================')
                                        time.sleep(2.5)
                                    except Exception as e:
                                        print(f"More job highlights not for {position_title} found: {str(e)}")
                                    
                                   # Try to find and click "Show full description"
                                    try:
                                        time.sleep(1)
                                        full_description = c_wiz.find_element(By.XPATH, ".//null[text()='Show full description']")
                                        # self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", full_description)
                                        # time.sleep(1)
                                        full_description.click()
                                        print('Clicked Show Full Description for {position_title} ==================================')
                                        time.sleep(2.5)
                                    except Exception as e:
                                        print(f"More job highlights not for {position_title} found: {str(e)}")
                                    
                                    job_highlight_items = []
                                    job_highlight_text = ''
                                    # get job highlights ==========================================================
                                    try:
                                        # Locate the <ul> that follows an <h3> containing text "Job highlights"
                                        job_highlights_ul = c_wiz.find_element(
                                            By.XPATH,
                                            ".//h3[text()='Job highlights']/following-sibling::ul"
                                        )
                                        
                                        # Find all <li> elements within this <ul>
                                        li_elements = job_highlights_ul.find_elements(By.TAG_NAME, "li")
                                                                                
                                        # Once found, you can do whatever you need with it
                                        print("Found Job Highlights <ul>:")
                                        job_highlight_text = job_highlights_ul.text

                                        # Collect each <li>'s text in a list
                                        for li in li_elements:
                                            highlight_text = li.text.strip()
                                            if highlight_text:
                                                job_highlight_items.append(highlight_text)

                                        # (Optional) Print out the collected highlights
                                        if job_highlight_items:
                                            print("Job highlights found:")
                                            for item in job_highlight_items:
                                                print(f" • {item}")
                                        print('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

                                    except NoSuchElementException:
                                        print("Could not find the <ul> following <h3> with text 'Job highlights'")
                                    except Exception as e:
                                        print(f"An error occurred: {str(e)}")                                    
                                    
                                    
                                    qualifications_items = []
                                    qualifications_text = ''
                                    # get qualifications ==========================================================
                                    try:
                                        # 1. Find the <ul> that follows an <h4> with the text "qualifications"
                                        #    This <h4> should be a sibling of <h3> that has text "Job highlights".
                                        qualifications_ul = c_wiz.find_element(
                                            By.XPATH,
                                            ".//h3[text()='Job highlights']/following-sibling::h4[text()='Qualifications']/following-sibling::ul"
                                        )
                                                                            
                                       # 2. Within that <ul>, locate all <li> elements
                                        li_elements = qualifications_ul.find_elements(By.TAG_NAME, "li")
                                                                                
                                        # Once found, you can do whatever you need with it
                                        print("Found Qualifications <ul>:")
                                        qualifications_text = qualifications_ul.text

                                        # 3. Build a list of text from the <li> elements
                                        for li in li_elements:
                                            text_value = li.text.strip()
                                            if text_value:
                                                qualifications_items.append(text_value)

                                        # (Optional) Print out the collected Qualifications
                                        if qualifications_items:
                                            print("Job Qualifications found:")
                                            for item in qualifications_items:
                                                print(f" • {item}")
                                        print('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

                                    except NoSuchElementException:
                                        print("Could not find the <ul> following <h3> with text 'Job highlights'")
                                    except Exception as e:
                                        print(f"An error occurred: {str(e)}")                                          
                                    
                                    
                                    benefits_items = []
                                    benefits_text = ''
                                    # get benefits ==========================================================
                                    try:
                                        # 1. Find the <ul> that follows an <h4> with the text "Benefits"
                                        #    This <h4> should be a sibling of <h3> that has text "Job highlights".
                                        benefits_ul = c_wiz.find_element(
                                            By.XPATH,
                                            ".//h3[text()='Job highlights']/following-sibling::h4[text()='Benefits']/following-sibling::ul"
                                        )

                                        # 2. Within that <ul>, locate all <li> elements
                                        li_elements = benefits_ul.find_elements(By.TAG_NAME, "li")

                                        # Once found, log or store the full text of the <ul>
                                        print("Found Benefits <ul>:")
                                        benefits_text = benefits_ul.text

                                        # 3. Build a list of text from the <li> elements
                                        for li in li_elements:
                                            text_value = li.text.strip()
                                            if text_value:
                                                benefits_items.append(text_value)

                                        # (Optional) Print out the collected Benefits
                                        if benefits_items:
                                            print("Job Benefits found:")
                                            for item in benefits_items:
                                                print(f" • {item}")

                                        print('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

                                    except NoSuchElementException:
                                        print("Could not find the <ul> following <h3> with text 'Job highlights' for Benefits")
                                    except Exception as e:
                                        print(f"An error occurred: {str(e)}")                                    
                                    
                                    


                                    responsibilities_items = []
                                    responsibilities_text = ''
                                     # get responsibilities ==========================================================
                                    try:
                                        # 1. Find the <ul> that follows an <h4> with the text "Responsibilities"
                                        #    This <h4> should be a sibling of <h3> that has text "Job highlights".
                                        responsibilities_ul = c_wiz.find_element(
                                            By.XPATH,
                                            ".//h3[text()='Job highlights']/following-sibling::h4[text()='Responsibilities']/following-sibling::ul"
                                        )

                                        # 2. Within that <ul>, locate all <li> elements
                                        li_elements = responsibilities_ul.find_elements(By.TAG_NAME, "li")

                                        # Once found, log or store the full text of the <ul>
                                        print("Found Responsibilities <ul>:")
                                        responsibilities_text = responsibilities_ul.text

                                        # 3. Build a list of text from the <li> elements
                                        for li in li_elements:
                                            text_value = li.text.strip()
                                            if text_value:
                                                responsibilities_items.append(text_value)

                                        # (Optional) Print out the collected Responsibilities
                                        if responsibilities_items:
                                            print("Job Responsibilities found:")
                                            for item in responsibilities_items:
                                                print(f" • {item}")

                                        print('oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')

                                    except NoSuchElementException:
                                        print("Could not find the <ul> following <h3> with text 'Job highlights' for Responsibilities")
                                    except Exception as e:
                                        print(f"An error occurred: {str(e)}")
                                    
                                    
                                    
                                    # Get job description +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                                    job_description_text = ""

                                    try:
                                        # 1. Find all <span> elements between <h3>Job description</h3> 
                                        # and <div>Report this listing</div>
                                        description_spans = c_wiz.find_elements(
                                            By.XPATH,
                                            (
                                                #".//h3[text()='Job description']"
                                                #"/following-sibling::span"
                                                #"[following-sibling::div[text()='Report this listing']]"
                                                ".//h3[text()='Job description']/following-sibling::span"
                                            )
                                        )

                                        if not description_spans:
                                            print("No <span> elements found between 'Job description' and 'Report this listing'.")
                                        else:
                                            # 2. Accumulate the text from each <span>
                                            for span in description_spans:
                                                text_value = span.text.strip()
                                                if text_value:
                                                    job_description_text += text_value + "\n"

                                            # 3. Print or store the combined text
                                            print("Job Description (extracted from multiple <span> elements):")
                                            print(job_description_text)
                                            print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")
                                            print("oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo")

                                    except NoSuchElementException:
                                        print("Could not find the required elements (<h3>Job description</h3> or <div>Report this listing</div>).")
                                    except Exception as e:
                                        print(f"An error occurred while extracting job description text: {str(e)}")                                    
                                    
                                    
                                    job_listings.append({
                                        "title": position_title,
                                        "company": company,
                                        "location": location,
                                        "timestamp": datetime.now().isoformat(),
                                        "job_highlights_text": job_highlight_text,
                                        "job_highlights_items": job_highlight_items,
                                        "qualifications_text": qualifications_text,
                                        "qualifications_items": qualifications_items,
                                        "benefits_text": benefits_text,
                                        "benefits_items": benefits_items,
                                        "responsibilities_text": benefits_text,
                                        "responsibilities_items": benefits_items,
                                        "job_description": job_description_text
                                        # ,"listing_text": text
                                    })                                    
                                                
                                    
                                    
                                    break
                        except Exception as e:
                            print(f"Error getting job details from c_wiz: {str(e)}")
                            
                            
                except Exception as e:
                    print(f"Error processing listing: {str(e)}")
                    continue
            
            # Generate timestamp and base filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Clean up query for filename
            clean_query = "".join(c if c.isalnum() else '_' for c in self.last_search_query).rstrip('_')
            base_filename = f"{clean_query}_{timestamp}"
            
            # Save to JSON file
            json_filename = f"{base_filename}.json"
            with open(json_filename, "w", encoding="utf-8") as f:
                json.dump({
                    "job_listings": job_listings,
                    "total_count": len(job_listings),
                    "extraction_date": datetime.now().isoformat(),
                    "search_query": self.last_search_query
                }, f, indent=4, ensure_ascii=False)
            
            print(f"Job listing texts saved to {json_filename} ({len(job_listings)} listings)")

            
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
