# MongoDB Functionality
import os

from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB Connection
client = MongoClient(
    os.getenv("mongo_host"),
    username=os.getenv("mongo_user"),
    password=os.getenv("mongo_pass"),
    authSource=os.getenv("mongo_db"),
    authMechanism="SCRAM-SHA-256",
)

class CareerCrawlerDB:
    mongo_client = client

    def __init__(self):
        self.db = self.mongo_client["career_crawler"]
        self.collection = self.db["jobs"]

    def update_jobs(self, jobs):
        """
        Updates found jobs.

        :param jobs: List of jobs (Dictionaries) to update.
        :return: None
        """

        for job in jobs:
            self.collection.update_one(
                {"_id": job["_id"]},
                {
                    "$set": {k:v for k, v in job.items() if k != "create_date"},
                    "$setOnInsert": {"create_date": datetime.utcnow()},
                },
                upsert=True,
            )

    def get_jobs(self, company_name=None, job_category=None, fields=None):
        """
        Fetches jobs from the database.

        :param company_name: The company name to fetch jobs for.
        :param job_category: The job category to fetch jobs for.
        :param fields: The fields to return.
        :return: A list of the results.
        """

        query = {}

        if company_name is not None:
            query["company_name"] = company_name

        if job_category is not None:
            query["job_category"] = job_category

        if fields is None:
            fields = ["company_name", "job_name", "job_category", "job_url", "last_updated"]

        return list(self.collection.find(query, fields))

    def get_new_jobs(self, window_hours=24):
        """
        Fetches jobs where the difference between create_date and last_updated is less than a given window of hours.

        :param window_hours: Window of hours within which the job was added or updated.
        :return: A list of the results.
        """

        window_date = datetime.now() - timedelta(hours=window_hours)
        
        return list(self.collection.find({
            "create_date": {"$gt": window_date}
        }))
    
    def remove_jobs_by_company_name(self, company_name):
        """
        Removes jobs by company name.

        :param company_name: The company name to remove jobs for.
        :return: None
        """

        self.collection.delete_many({"company_name": company_name})
