import pytest
import sys

from career_crawler.scrapers import GreenhouseJobBoard

def test_greenhouse_job_board_parse():

    greenhouse_job_board = GreenhouseJobBoard()
    greenhouse_job_board.scrape(url = "D:/Documents/Github/CareerCrawler/tests/pages/thatgamecompany.html", local=True)
    parsed_results = greenhouse_job_board.parse(company_name="thatgamecompany")

    assert len(parsed_results) > 0
    assert parsed_results[0].job_name == "Animator"
    assert parsed_results[0].link is not None
    assert parsed_results[0].job_location == "Main"
    assert parsed_results[0].company_name == "thatgamecompany"


def test_edmentum():
    greenhouse_job_board = GreenhouseJobBoard()
    greenhouse_job_board.scrape(url = "D:/Documents/Github/CareerCrawler/tests/pages/edmentum.html", local=True)
    parsed_results = greenhouse_job_board.parse(company_name="edmentum")

    assert len(parsed_results) > 0
    assert parsed_results[0].job_name == "Financial Analyst "
    assert parsed_results[0].link is not None
    assert parsed_results[0].job_location == "United States"
    assert parsed_results[0].company_name == "edmentum"