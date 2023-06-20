import pytest
import sys

from career_crawler.scrapers import ZenimaxJobBoard

def test_zenimax_job_board_parse():
    zenimax_job_board = ZenimaxJobBoard()
    parsed_results = list(zenimax_job_board.scrape_paginated(url =  "file:///" + sys.path[0] + "/tests/pages/zenimax.html", local=True, company_name="Zenimax"))[0]

    assert len(parsed_results) > 0
    assert parsed_results[0].job_name == "AI Programmer (all levels)"
    assert parsed_results[0].link is not None
    assert parsed_results[0].job_location == "Dallas, TX, US"
    assert parsed_results[0].company_name == "Zenimax"