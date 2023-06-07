from dataclasses import dataclass
from abc import abstractmethod
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from datetime import datetime

from bs4 import BeautifulSoup

@dataclass
class BaseScraper: # pragma: no cover
    soup: BeautifulSoup = None 

    @abstractmethod
    def scrape(self):
        pass

    @abstractmethod
    def parse(self):
        pass

@dataclass
class ParsedResult:
    job_name: str = None
    job_location: str = None
    link: str = None
    company_name: str = None

    def __str__(self):
        return f'{self.job_name} - {self.job_location}'
    
    def __repr__(self):
        return f'{self.job_name} - {self.job_location}'
    
    def to_dict(self):
        return {
            'job_name': self.job_name,
            'job_location': self.job_location,
            'company_name': self.company_name
        }
    
    def to_db_record(self):
        """
        Prepares a dictionary to be inserted into the database.
        """

        return {
            "_id": f"{self.job_name.lower().replace(' ', '')}__{self.company_name.lower().replace(' ', '')}__{self.link.lower().replace(' ', '')}",
            "job_name": self.job_name,
            "job_location": self.job_location,
            "company_name": self.company_name,
            "link": self.link,
            "last_updated": datetime.utcnow(),
        }
    
@dataclass
class ParsedResultCollection:

    @staticmethod
    def _validate_results(results):
        if (results is None) or (len(results) == 0):
            raise ValueError("results cannot be None or empty")
        
        if results[0].__class__ != ParsedResult:
            raise ValueError("results must be a list of ParsedResult objects")
        
        return True

    @staticmethod
    def to_db_records(results):
        """
        Prepares a list of dictionaries to be inserted into the database.
        """

        if ParsedResultCollection._validate_results(results):
            return [result.to_db_record() for result in results]