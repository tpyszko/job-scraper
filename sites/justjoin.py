import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# WebDriver setup notes for GitHub Actions:
# 1. ChromeDriver needs to be installed in the GitHub Actions environment.
#    This can be done in the workflow YAML file using a setup step, e.g.:
#    - name: Set up Chrome
#      uses: browser-actions/setup-chrome@v1
#    - name: Set up ChromeDriver
#      uses: nanasess/setup-chromedriver@v2
# 2. Alternatively, if using a Docker container, ensure ChromeDriver is in the PATH.
# 3. The script attempts to find ChromeDriver automatically from PATH.
#    If chromedriver is installed via a package manager like apt, it might be in /usr/bin/chromedriver or /usr/local/bin/chromedriver.
#    The setup-chromedriver action usually handles placing it in the PATH.

def scrape(keywords, location_filter_keyword): # Renamed location to location_filter_keyword for clarity
    url = "https://justjoin.it/all/python" # The task specifies this URL

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") # Often needed in CI environments
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu") # Optional, but can help in headless
    chrome_options.add_argument("window-size=1920,1080") # Set a reasonable window size

    # Attempt to find ChromeDriver from PATH or use a direct path if known
    # For GitHub Actions, 'chromedriver' should be in PATH if setup-chromedriver action is used.
    try:
        service = ChromeService() # Assumes chromedriver is in PATH
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error setting up ChromeDriver from PATH: {e}")
        print("Attempting common direct paths for ChromeDriver...")
        # Common paths where ChromeDriver might be installed in CI environments
        common_paths = ["/usr/local/bin/chromedriver", "/usr/bin/chromedriver", "chromedriver"]
        driver_path_found = None
        for path_option in common_paths:
            try:
                service = ChromeService(executable_path=path_option)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver_path_found = path_option
                print(f"ChromeDriver found at {driver_path_found}")
                break
            except Exception:
                continue
        if not driver_path_found:
            print("ChromeDriver not found in common paths. Please ensure it is installed and in PATH.")
            return []


    offers = []
    try:
        driver.get(url)

        # Wait for the job offer elements to be loaded
        # The task asks to identify the correct CSS selector.
        # We'll use the existing selector 'a.css-4lqp8g' to wait for,
        # as this is the most likely candidate for offer links.
        # If this doesn't work, it implies the selector has changed.
        offer_selector_css = "a.css-4lqp8g" # Existing selector

        # A more general parent might be safer if the 'a' tag's class changes often.
        # For example, if offers are in a list: ul[data-test="job-offers-list"]
        # For now, sticking to the 'a' tag directly.
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, offer_selector_css))
        )

        # Scroll down a bit to ensure all elements are loaded if there's lazy loading
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        # time.sleep(2) # Wait for any lazy-loaded content
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # time.sleep(2)


        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Use the same selector to find all job elements
        job_elements = soup.select(offer_selector_css)

        if not job_elements:
            print(f"No job elements found with selector '{offer_selector_css}'. The site structure might have changed.")
            # Attempt to save page source for debugging if no offers found
            # with open("debug_page_source.html", "w", encoding="utf-8") as f:
            #     f.write(driver.page_source)
            # print("Debug page source saved to debug_page_source.html")
            return []

        for job_element in job_elements:
            title = job_element.get("title", "").strip()

            # Keyword filtering
            if keywords and not any(k.lower() in title.lower() for k in keywords):
                continue

            company_name = "Unknown"
            # Try to find company name from a common data attribute or a specific element structure
            # This part might need adjustment based on actual HTML structure
            company_element = job_element.find_next(attrs={"data-company": True}) # Example
            if company_element:
                company_name = company_element.get("data-company", "Unknown")
            else:
                # Fallback: try to find it within the 'a' tag's children if structured differently
                # This is highly dependent on the actual HTML.
                # Example: company_span = job_element.find('span', class_='company-name-class')
                # if company_span: company_name = company_span.text.strip()
                pass # Add more specific selectors if known

            job_url = "https://justjoin.it" + job_element.get("href", "")

            # Location extraction:
            # The location is often within the text of the job_element or a child/sibling.
            # This needs careful inspection of the rendered HTML.
            # For now, let's assume location_text is within the job_element itself.
            location_text_raw = job_element.text.lower() # Get all text within the 'a' tag

            # This is a placeholder. Actual location extraction needs a reliable selector.
            # It might be in a specific div/span with a class.
            # e.g., location_div = job_element.find('div', class_='location-class')
            # if location_div: location_text_raw = location_div.text.lower()

            # Location filtering
            if location_filter_keyword.lower() not in location_text_raw:
                 # Try to find a more specific location element if primary text doesn't match
                location_elements = job_element.select('div[class*="location"], span[class*="location"]') # Common patterns
                found_location_in_sub_element = False
                for loc_el in location_elements:
                    if location_filter_keyword.lower() in loc_el.text.lower():
                        found_location_in_sub_element = True
                        break
                if not found_location_in_sub_element:
                    continue


            offers.append({
                "title": title,
                "company": company_name,
                "location": location_filter_keyword, # Using the filter keyword as location, as per original script logic
                "url": job_url,
            })

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        # Attempt to save page source on error for debugging
        # try:
        #     with open("error_page_source.html", "w", encoding="utf-8") as f:
        #         f.write(driver.page_source)
        #     print("Error page source saved to error_page_source.html")
        # except Exception as e_save:
        #     print(f"Could not save page source on error: {e_save}")

    finally:
        if 'driver' in locals() and driver is not None:
            driver.quit()

    return offers

if __name__ == '__main__':
    # Example usage:
    # Ensure ChromeDriver is in your PATH or specify its location via ChromeService
    # For example:
    # service = ChromeService(executable_path='/path/to/chromedriver')
    # driver = webdriver.Chrome(service=service, options=chrome_options)

    test_keywords = ["Python Developer", "Software Engineer"]
    test_location = "Warszawa" # Or "remote" or "krakow" etc.

    print(f"Scraping for keywords: {test_keywords} in location: {test_location}")
    scraped_offers = scrape(test_keywords, test_location)

    if scraped_offers:
        print(f"Found {len(scraped_offers)} offers:")
        for offer in scraped_offers:
            print(f"  Title: {offer['title']}")
            print(f"  Company: {offer['company']}")
            print(f"  Location: {offer['location']}")
            print(f"  URL: {offer['url']}")
            print("-" * 20)
    else:
        print("No offers found matching the criteria.")

# Note on CSS Selector for job offers (a.css-4lqp8g):
# This selector was used in the previous version of the script.
# With Selenium, the page is rendered by a real browser engine, so if this selector
# is still used by justjoin.it for its dynamically loaded job offer links, it should work.
# If it does not yield results, it means the website's frontend structure for these links
# has changed, and a new selector would need to be identified by inspecting the
# JS-rendered HTML in a developer console. The tools available in this environment
# do not allow for direct inspection of JS-rendered pages to discover a new selector.
# This script proceeds with the assumption that 'a.css-4lqp8g' is still the valid
# selector for the individual job offer anchor tags after JS rendering.
#
# The extraction of company name and precise location text within the offer card
# is also dependent on the site's structure. The current implementation uses
# a placeholder `job_element.get("data-company", "Unknown")` or relies on broad text search
# which might need refinement after inspecting the rendered HTML.
# The original script's logic for location was to check if the `location_filter_keyword`
# was in the job_element.text - this is maintained, with an attempt to check more specific
# sub-elements if the initial check fails. The returned location is still the `location_filter_keyword`.
#
# For identifying a new selector if `a.css-4lqp8g` fails:
# 1. Run this script locally (outside this environment) with headless mode OFF.
# 2. When Selenium opens the browser, manually inspect the page for job offers.
# 3. Right-click on a job offer link and "Inspect Element".
# 4. Identify a unique and stable CSS selector for the `<a>` tag or its main container.
#    Look for classes that seem specific to job listings.
# 5. Update `offer_selector_css` variable in this script.
# 6. Adjust company and location sub-element selectors as needed.
