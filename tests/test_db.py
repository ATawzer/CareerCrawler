import os
import pytest

from career_crawler import CareerCrawlerDB, ParsedResult, ParsedResultCollection

from datetime import datetime, timedelta


@pytest.fixture(scope="module")
def db():
    # Setup : connect to DB
    db = CareerCrawlerDB()

    # yield the DB connection for testing
    yield db

    # Teardown : Disconnect from DB
    db.mongo_client.close()


@pytest.fixture(scope="module")
def parsed_results(db):
    # Set up test data
    parsed_results = [ParsedResult("Software Engineer", "New York", "www.example.com", "Test Company"),
                      ParsedResult("Data Scientist", "San Francisco", "www.example2.com", "Test Company2")]

    yield parsed_results

    # Teardown : clean up the test data
    db.collection.delete_many({"_id": {"$in": [result.to_db_record()["_id"] for result in parsed_results]}})


def test_update_jobs(db, parsed_results):
    # Convert parsed_results to db_records
    db_records = ParsedResultCollection.to_db_records(parsed_results)

    # Insert test data into the database
    db.update_jobs(db_records)

    # Verify that the data was inserted correctly
    for record in db_records:
        assert db.collection.find_one({"_id": record["_id"]}) is not None

    # Remove test data from the database
    db.collection.delete_many({"_id": {"$in": [record["_id"] for record in db_records]}})

def test_get_new_jobs(db):
    # Create test data with explicit create_date and last_updated
    current_time = datetime.utcnow()
    one_hour_ago = current_time - timedelta(hours=1)
    db_records = [
        {
            "_id": "softwareengineer__testcompany__www.example.com",
            "job_name": "Software Engineer",
            "job_location": "New York",
            "company_name": "Test Company",
            "link": "www.example.com",
            "last_updated": current_time,
            "create_date": one_hour_ago,
        },
        {
            "_id": "datascientist__testcompany2__www.example2.com",
            "job_name": "Data Scientist",
            "job_location": "San Francisco",
            "company_name": "Test Company2",
            "link": "www.example2.com",
            "last_updated": current_time,
            "create_date": one_hour_ago,
        },
    ]

    # Insert test data into the database
    db.collection.insert_many(db_records)

    # Check if get_new_jobs() returns jobs within the correct window (e.g., 2 hours)
    new_jobs = list(db.get_new_jobs(2))
    assert len(new_jobs) >= len(db_records)

    # Verify that the data returned by get_new_jobs() is correct
    for job in db_records:
        assert job["_id"] in [new_job["_id"] for new_job in new_jobs]

    # Remove test data from the database
    db.collection.delete_many({"_id": {"$in": [record["_id"] for record in db_records]}})

