from .base import BaseScraper, ParsedResult, SeleniumBaseScraper

import requests
from bs4 import BeautifulSoup
import time, random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ActivisionJobBoard(SeleniumBaseScraper): # pragma: no cover

    def scrape_paginated(self, url, company_name=None): 
        self.start_browser()

        counter = 1
        while url is not None:
            self.load_page(url, wait_by=By.CLASS_NAME, wait_for_element='searchresults-page')
            yield self.parse(company_name=company_name)

            # Check for the "next" button
            next_button = self.soup.find('a', {'data-ph-at-id': 'pagination-next-link'})
            if next_button:
                # Check if 'disabled' is in the class list
                class_list = next_button.get('class', [])
                if 'disabled' not in class_list:
                    url = next_button.get('href')
                else:
                    url = None
            else:
                url = None
            
            # Pause for a random number of seconds between 1 and 5
            pause = random.randint(1, 5)
            print(f'Pausing for {pause} seconds..., {counter} pages scraped, next url: {url}')
            time.sleep(pause)
            counter += 1

        self.close_browser()

    def scrape(self, url, company_name=None):
        self.start_browser()
        self.load_page(url)
        parsed_results = self.parse(company_name=company_name)
        self.close_browser()
        return parsed_results
    
    def parse(self, company_name):
        parsed_results = []
    
        # find the job entries
        for job_entry in self.soup.find_all('div', attrs={'class': 'information'}):
            # job title and link
            job_tag = job_entry.find('a', attrs={'data-ph-at-id': 'job-link'})
            if job_tag:
                job_title = job_tag.get('data-ph-at-job-title-text')
                job_link = job_tag.get('href')

            # job location
            job_location_tag = job_entry.find('span', attrs={'class': 'cityStateCountry'})
            if job_location_tag:
                job_location = job_location_tag.text.strip()

            parsed_results.append(ParsedResult(
                job_name=job_title,
                link=job_link,
                job_location=job_location,
                company_name=company_name
            ))
            
        return parsed_results
    
class ZenimaxJobBoard(SeleniumBaseScraper):

    def scrape_paginated(self, url, local=False, company_name=None):
        self.start_browser()
        self.load_page(url, wait_by=By.CLASS_NAME, wait_for_element='job-listings')
        parsed_results = self.parse(company_name=company_name)
        self.close_browser()
        yield parsed_results

    def scrape(self, url, local=False): # pragma: no cover
        if not local:
            response = requests.get(url).content
        else:
            with open(url, 'r', encoding='utf-8') as file:
                response = file.read()

        self.soup = BeautifulSoup(response, 'html.parser')

    def parse(self, company_name):
        parsed_results = []

        # Find <a> tags with certain attributes
        for a in self.soup.find_all('a', attrs={'class': 'job-link'}):

            # Find divs for job title, job department, job location within the <a> tag
            job_title_div = a.find('div', attrs={'class': 'job-title'})
            job_location_div = a.find_all('div', attrs={'class': 'job-department pl-md-3'})[1]

            # If all necessary information exists
            if job_title_div and job_location_div:
                parsed_results.append(ParsedResult(
                    job_name=job_title_div.get_text().strip(),
                    job_location=job_location_div.get_text().strip(),
                    link=a.get('href'),
                    company_name=company_name
                ))
        
        return parsed_results

class MicrosoftJobBoard(SeleniumBaseScraper):
    
    def scrape_paginated(self, url, local=False, company_name=None):
        self.start_browser()
        self.url_base = url.split('/')[2]

        # Load the first page
        self.load_page(url, wait_by=By.CSS_SELECTOR, wait_for_element='button[title="Next"]')

        while True:
            self.reload_content()
            parsed_results = self.parse(company_name=company_name)
            yield parsed_results

            try:
                # Wait for the "Next" button to be clickable, and then click it
                next_button = WebDriverWait(self.browser, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[title="Next"]'))
                )
                next_button.click()

                pause = random.randint(1, 5)
                time.sleep(pause)
                print(f'Pausing for {pause} seconds...')
            except Exception as e:
                print("No more pages left to scrape.")
                break

        self.close_browser()

        
    def scrape(self, url, local=False): # pragma: no cover
        if not local:
            response = requests.get(url).content
        else:
            with open(url, 'r', encoding='utf-8') as file:
                response = file.read()

        self.soup = BeautifulSoup(response, 'html.parser')

    def parse(self, company_name='microsoft'):
        parsed_results = []

        # Find div tags with certain attributes
        for div in self.soup.find_all('div', attrs={'role': 'listitem', 'class': 'ms-List-cell'}):

            # Find the <h2> tag for job title within the div tag
            job_title_h2 = div.find('h2') # should be the only h2 tag

            # Find the span tag for job location within the div tag
            job_location_span = div.find_all('span')[1] # Should be the second span tag

            # Find the link for the job
            job_id = div.find('div').get('aria-label').split(' ')[-1]
            job_link = f'https://jobs.careers.microsoft.com/global/en/job/{job_id}/' if job_id else None

            # If all necessary information exists
            if job_title_h2 and job_location_span and job_link:
                parsed_results.append(ParsedResult(
                    job_name=job_title_h2.get_text().strip(),
                    job_location=job_location_span.get_text().strip(),
                    link=job_link,
                    company_name=company_name
                ))

        return parsed_results
        
        
