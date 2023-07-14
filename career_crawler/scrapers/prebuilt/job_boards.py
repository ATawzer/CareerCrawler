from .base import BaseScraper, ParsedResult, SeleniumBaseScraper

import requests
from bs4 import BeautifulSoup
import time, random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GreenhouseJobBoard(BaseScraper):

    def scrape_paginated(self, url, local=False, company_name=None):
        """
        A Higher level function that orchestrates the scraping of a paginated job board.
        For Greenhouse, for now, there is no pagination
        """

        self.scrape(url, local)
        
        for i in range(0, 1):
            yield self.parse(company_name=company_name)

    def scrape(self, url, local=False):
            
        if not local:
            response = requests.get(url).content # pragma: no cover
        else:
            response = open(url, 'r')

        self.soup = BeautifulSoup(response, 'html.parser')

    def parse(self, company_name):
            
        parsed_results = []
    
        # Find <div> tags with certain attributes
        for div in self.soup.find_all('div', attrs={'class': 'opening'}):

            # Find <a> and <span> tags within this <div>
            a = div.find('a', attrs={'data-mapped': 'true'})
            span = div.find('span', attrs={'class': 'location'})

            if a and span:
                parsed_results.append(ParsedResult(
                    job_name=a.get_text(),
                    link=a.get('href'),
                    job_location=span.get_text(),
                    company_name=company_name
            ))
        
        return parsed_results
    
class GR8PeopleJobBoard(SeleniumBaseScraper):

    def scrape_paginated(self, url, company_name=None): 
        self.start_browser()

        counter = 1
        while url is not None:
            self.load_page(url, wait_by=By.CLASS_NAME, wait_for_element='search-results-column-left')
            yield self.parse(company_name=company_name)

            # Check for the "next" button
            next_button = self.soup.find('a', {'rel': 'next'})
            if next_button and not 'disabled' in next_button.get('class', []):
                url = next_button.get('href')
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
        
        # Find <tr> tags with certain attributes
        for row in self.soup.find_all('tr', attrs={'data-result': True}):
            
            # Find the columns within this <tr>
            cols = row.find_all('td', attrs={'class': 'search-results-column-left'})
            
            # Check if we found the right number of columns
            if len(cols) >= 4:
                link_tag = cols[0].find('a')
                if link_tag:
                    parsed_results.append(ParsedResult(
                        job_name=cols[1].get('title'),
                        link=link_tag.get('href'),
                        job_location=cols[3].get('title'),
                        company_name=company_name
                    ))
        
        return parsed_results

class LeverJobBoard(BaseScraper):
    def scrape_paginated(self, url, local=False, company_name=None):
        """
        A Higher level function that orchestrates the scraping of a paginated job board.
        For Lever, for now, there is no pagination
        """
        self.scrape(url, local)
        yield self.parse(company_name=company_name)

    def scrape(self, url, local=False):
        if local:
            with open(url, 'r') as f:
                response = f.read()
        else:
            response = requests.get(url).content
        self.soup = BeautifulSoup(response, 'html.parser')

    def parse(self, company_name):
        parsed_results = []
        # Find <a> tags with certain attributes
        for a in self.soup.find_all('a', attrs={'class': 'posting-title'}):
            # Find <h5> and <div> tags within this <a>
            h5 = a.find('h5', attrs={'data-qa': 'posting-name'})
            div = a.find('div', attrs={'class': 'posting-categories'})
            location_span = div.find('span', attrs={'class': 'sort-by-location posting-category small-category-label location'})
            if h5 and div and location_span:
                parsed_results.append(ParsedResult(
                    job_name=h5.get_text(),
                    link=a.get('href'),
                    job_location=location_span.get_text(),
                    company_name=company_name
            ))
        return parsed_results

class WorkdayJobBoard(SeleniumBaseScraper):

    def scrape_paginated(self, url, company_name=None): 
        self.start_browser()
        self.url_base = url.split('/')[2]
        
        # Load the first page
        self.load_page(url, wait_by=By.CSS_SELECTOR, wait_for_element='button[aria-label="next"]')
        
        while True:
            self.reload_content()
            parsed_results = self.parse(company_name=company_name)
            yield parsed_results
            
            try:
                # Wait for the "next" button to be clickable, and then click it
                next_button = WebDriverWait(self.browser, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="next"]'))
                )
                next_button.click()

                pause = random.randint(1, 5)
                time.sleep(pause)
                print(f'Pausing for {pause} seconds...')
            except Exception as e:
                print("No more pages left to scrape.")
                break
        
        self.close_browser()


    def scrape(self, url, company_name=None):
        self.start_browser()
        self.load_page(url)
        parsed_results = self.parse(company_name=company_name)
        self.close_browser()
        return parsed_results
    
    def parse(self, company_name):
        parsed_results = []

        # Find <li> tags with certain attributes
        for row in self.soup.find_all('li'):

            # Find the link tag within this <li>
            link_tag = row.find('a', {'data-automation-id': 'jobTitle'})
            if not link_tag:
                continue
            location_tag = row.find('div', {'data-automation-id': 'locations'}).find('dd')


            if link_tag and location_tag:
                parsed_results.append(ParsedResult(
                    job_name=link_tag.text,
                    link=self.url_base+link_tag['href'],
                    job_location=location_tag.text,
                    company_name=company_name
                ))

        return parsed_results