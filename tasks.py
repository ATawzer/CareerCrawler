from invoke import task
import sys
import time
from collections import defaultdict
from tqdm import tqdm

sys.path.append("D:\Documents\GitHub\CareerCrawler\career_crawler")
from career_crawler.scrapers import *
from career_crawler.db import CareerCrawlerDB
from career_crawler.classifiers import JobTypeClassifier

import configparser

config = configparser.ConfigParser()
config.read('careers.ini')

URL_MAP = {}

for section in config.sections():
    URL_MAP[section] = {
        "url": config.get(section, "url"),
        "scraper": globals()[config.get(section, "scraper")]
    }

@task
def status(ctx):
    print("Retrieving all new jobs...")
    
    db = CareerCrawlerDB()
    new_jobs = db.get_new_jobs(1)
    company_job_counts = defaultdict(int)

    for job in new_jobs:
        company_job_counts[job['company_name']] += 1

    # Summary
    print("\n" + "="*80)
    print(f"Total added jobs in last 8 hours: {len(new_jobs)}")
    print(f"Total companies: {len(company_job_counts)}")

    for company, count in company_job_counts.items():
        print(f"{company}: {count} job(s)")

    time.sleep(2)

    # Sorting jobs by company for printout
    new_jobs.sort(key=lambda x: (x['company_name'], x['job_category']))

    current_company = ""
    for job in new_jobs:
        if job['company_name'] != current_company:
            current_company = job['company_name']
            print("\n\n" + "="*80)
            company_header = f" Company: {current_company} "
            print(company_header.center(80, "="))
            print("="*80)
            
        
        job_name = job['job_name']
        location = job['job_location'] if job['job_location'] is not None else "Unknown"
        link = job['link']
        job_category = job['job_category']
        
        # Check if link needs to be prefixed
        if "https://" not in link:
            if current_company == 'zenimax':
                link = f"https://jobs.zenimax.com{link}"
            else:
                link = f"https://boards.greenhouse.io{link}"

        # Print the job info with hyperlink
        try:
            print(f"{job_category:40} | {job_name:80} | {location:50} | Link: {link}")
        except:
            print(f"Error printing job info for {job}")
        
        time.sleep(.5)

@task
def scrape_all(ctx):
    for name in URL_MAP:
        print(f"Currently Processing: {name}")
        scrape(ctx, name)

    print("Done!")

@task
def scrape(ctx, name):
    if name not in URL_MAP:
        print(f"Invalid company name: {name}")
        return

    scraper = URL_MAP[name]["scraper"]()

    for result in scraper.scrape_paginated(URL_MAP[name]["url"], company_name=name):
        db_recs = ParsedResultCollection.to_db_records(result)

        db = CareerCrawlerDB()
        db.update_jobs(db_recs)

@task
def test(ctx):
    #run pytest with coverage
    ctx.run("pytest --cov=career_crawler tests/ --cov-report term-missing")

@task 
def run(ctx):

    scrape_all(ctx)
    classify(ctx)
    status(ctx)

@task
def classify(ctx, classifier=None, make_classifier=True, db=None):

    if (make_classifier) & (classifier is None):
        classifier = JobTypeClassifier()

    db = CareerCrawlerDB() if db is None else db
    db_recs = db.get_new_jobs(1)

    if classifier is not None:
        print(f"Classifying {len(db_recs)} jobs...")
        for rec in tqdm(db_recs):
            if 'job_category' not in rec:
                rec['job_category'] = classifier.predict(rec['job_name'])

    db.update_jobs(db_recs)
