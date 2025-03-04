from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time

def scrape_yatra_full_text(url, output_file="yatra_package_details.txt"):
    options = Options()
    options.headless = True  # Run in headless mode
    service = Service("C://Users//manis//Downloads//geckodriver-v0.35.0-win64//geckodriver.exe")  # Update with correct path
    driver = webdriver.Firefox(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)  # Allow the page to load fully
        
        # Click "More+" buttons to expand details
        more_buttons = driver.find_elements(By.CSS_SELECTOR, ".readMore")
        for button in more_buttons:
            driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", button)
            time.sleep(1)  # Allow content to load
        
        # Extract all text content
        page_text = driver.find_element(By.TAG_NAME, "body").text

        # Save to a text file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(page_text)

        print(f"Data successfully scraped and saved to {output_file}")

    finally:
        driver.quit()

# Example Usage
url = input("Enter the link:")
scrape_yatra_full_text(url)
