import pytest
import sys

from career_crawler.scrapers import GR8PeopleJobBoard


def test_gr8_people_job_board_parse():

    ea_job_board = GR8PeopleJobBoard() 

    parsed_results = []
    for results in ea_job_board.scrape_paginated(url="file:///" + sys.path[0] + "/tests/pages/ea.html", company_name="Electronic Arts"):
        assert len(results) > 0
        parsed_results.extend(results)


    assert len(parsed_results) > 0
    assert parsed_results[0].job_name == "Manager, Corporate Development"
    assert parsed_results[0].link == "https://ea.gr8people.com/jobs/173976/manager-corporate-development"
    assert parsed_results[0].job_location == "Redwood City, CA, USA"
    assert parsed_results[0].company_name == "Electronic Arts"
