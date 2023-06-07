from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

from .base import BaseScraper, ParsedResult
from dataclasses import dataclass
from bs4 import BeautifulSoup

class RespawnJobBoard(BaseScraper):

    def scrape(self, url):

         # Setup webdriver
        webdriver_service = Service(ChromeDriverManager().install())
        options = Options()
        options.add_argument("--headless")  # Ensure GUI is off
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(service=webdriver_service, options=options)

        # Get page
        driver.get(url)
        # Wait for JavaScript to load
        driver.implicitly_wait(5) # Wait for 10 seconds

        self.soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Clean up
        driver.quit()

    def parse(self, company_name="Respawn Entertainment", base_url='https://www.respawn.com'):
        parsed_results = []

        # Find <div> tags with certain attributes
        for div in self.soup.find_all('div', attrs={'class': 'row'}):

            # Find respective tags within this <div>
            role = div.find('p', text='Role:').find_next_sibling('p').get_text()
            location = div.find('p', text='Location:').find_next_sibling('p').get_text()
            link = div.find('a').get('href')

            if role and location and link:
                parsed_results.append(ParsedResult(
                    job_name=role,
                    link=f"{base_url}{link}",
                    job_location=location,
                    company_name=company_name
                ))

        return parsed_results
