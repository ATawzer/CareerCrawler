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
                    "$set": job,
                    "$setOnInsert": {"create_date": datetime.utcnow()},
                },
                upsert=True,
            )

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
