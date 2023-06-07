from .base import BaseScraper, ParsedResult

import requests
from bs4 import BeautifulSoup

class GreenhouseJobBoard(BaseScraper):

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