import pytest
from datetime import datetime
from career_crawler.scrapers import ParsedResult, ParsedResultCollection

# Test for ParsedResult
def test_parsed_result():
    parsed_result = ParsedResult("Software Engineer", "New York", "www.example.com", "Test Company")
    assert parsed_result.job_name == "Software Engineer"
    assert parsed_result.job_location == "New York"
    assert parsed_result.link == "www.example.com"
    assert parsed_result.company_name == "Test Company"

    # Test __str__ and __repr__ methods
    assert str(parsed_result) == "Software Engineer - New York"
    assert repr(parsed_result) == "Software Engineer - New York"

    # Test to_dict method
    expected_dict = {"job_name": "Software Engineer", "job_location": "New York", "company_name": "Test Company"}
    assert parsed_result.to_dict() == expected_dict

    # Test to_db_record method
    db_record = parsed_result.to_db_record()
    assert db_record["job_name"] == "Software Engineer"
    assert db_record["job_location"] == "New York"
    assert db_record["company_name"] == "Test Company"
    assert db_record["link"] == "www.example.com"
    assert db_record["_id"] == "softwareengineer__testcompany__www.example.com"
    assert isinstance(db_record["last_updated"], datetime)

# Test for ParsedResultCollection
def test_parsed_result_collection():
    parsed_results = [ParsedResult("Software Engineer", "New York", "www.example.com", "Test Company"), 
                      ParsedResult("Data Scientist", "San Francisco", "www.example2.com", "Test Company2")]

    # Test _validate_results
    with pytest.raises(ValueError):
        ParsedResultCollection._validate_results(None)
    with pytest.raises(ValueError):
        ParsedResultCollection._validate_results([])
    with pytest.raises(ValueError):
        ParsedResultCollection._validate_results(["Invalid"])
    assert ParsedResultCollection._validate_results(parsed_results)

    # Test to_db_records
    db_records = ParsedResultCollection.to_db_records(parsed_results)
    assert isinstance(db_records, list)
    assert len(db_records) == 2
    for db_record in db_records:
        assert isinstance(db_record, dict)
        assert isinstance(db_record["last_updated"], datetime)
