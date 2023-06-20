from career_crawler.scrapers import LeverJobBoard, ParsedResult

def test_scrape_inworld():
    scraper = LeverJobBoard()
    results_generator = scraper.scrape_paginated("./tests/pages/inworld.html", local=True, company_name="Inworld AI")
    results = next(results_generator)
    
    assert isinstance(results, list)
    assert len(results) > 0
    
    for result in results:
        assert isinstance(result, ParsedResult)
        assert result.company_name == "Inworld AI"
        assert result.link.startswith("https://jobs.lever.co/inworld")
        assert result.job_name is not None
        assert result.job_location is not None
