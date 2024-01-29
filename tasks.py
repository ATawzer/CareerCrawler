from invoke import task
import sys
import time
from collections import defaultdict
from tqdm import tqdm

from dotenv import load_dotenv
load_dotenv()

#sys.path.append("D:\Documents\GitHub\CareerCrawler\career_crawler")
from career_crawler.scrapers import *
from career_crawler.db import CareerCrawlerDB
from career_crawler.classifiers import JobTypeClassifier, JobTypeSpecialist

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

    # Sorting jobs by job_category and then by company for printout
    new_jobs.sort(key=lambda x: (x['job_category'], x['company_name']))

    current_category = ""
    for job in new_jobs:
        if job['job_category'] != current_category:
            current_category = job['job_category']
            print("\n\n" + "="*80)
            category_header = f" Category: {current_category} "
            print(category_header.center(80, "="))
            print("="*80)

        job_name = job['job_name']
        location = job['job_location'] if job['job_location'] is not None else "Unknown"
        link = job['link']
        company_name = job['company_name']

        # Check if link needs to be prefixed
        if "https://" not in link:
            if company_name == 'zenimax':
                link = f"https://jobs.zenimax.com{link}"
            else:
                link = f"https://boards.greenhouse.io{link}"

        # Print the job info with hyperlink
        try:
            print(f"{company_name:40} | {job_name:80} | {location:50} | Link: {link}")
        except:
            print(f"Error printing job info for {job}")

        time.sleep(.5)

@task
def scrape_all(ctx):
    for name in URL_MAP:
        print(f"Currently Processing: {name}")
        try:
            scrape(ctx, name)
        except Exception as e:
            print(f"Error scraping {name}: {e}")
            continue

    print("Done!")

@task
def scrape(ctx, name, classify=False):
    if name not in URL_MAP:
        print(f"Invalid company name: {name}")
        return

    scraper = URL_MAP[name]["scraper"]()

    for result in scraper.scrape_paginated(URL_MAP[name]["url"], company_name=name):
        db_recs = ParsedResultCollection.to_db_records(result)

        db = CareerCrawlerDB()
        db.update_jobs(db_recs)

    if classify:
        spec_classify(ctx)

@task
def test(ctx):
    """ Tests all files in the tests directory"""
    #run pytest with coverage
    ctx.run("pytest --cov=career_crawler tests/ --cov-report term-missing")

@task
def test_file(ctx, filename):
    """ Tests a specific file in the tests directory"""
    #run pytest with coverage
    ctx.run(f"pytest --cov=career_crawler tests/test_{filename}.py --cov-report term-missing")

@task 
def run(ctx):

    scrape_all(ctx)
    spec_classify(ctx)
    #status(ctx)
    app(ctx)

@task
def app(ctx):
    ctx.run("streamlit run app.py")

@task
def classify(ctx, classifier=None, make_classifier=True, db=None):

    if (make_classifier) & (classifier is None):
        classifier = JobTypeClassifier()

    db = CareerCrawlerDB() if db is None else db
    db_recs = db.get_new_jobs(2)

    if classifier is not None:
        print(f"Classifying {len(db_recs)} jobs...")
        for rec in tqdm(db_recs):
            if ('job_category' not in rec) or (rec['job_category'] == 'Classifier Error'):
                rec['job_category'] = classifier.predict(rec['job_name'])
                db.update_jobs([rec])

    #db.update_jobs(db_recs)

@task
def spec_classify(ctx, model_name="job_type_assistant20230714113155"):
    jts = JobTypeSpecialist(model_name=model_name)
    db = CareerCrawlerDB()
    db_recs = db.get_new_jobs(2)

    if jts is not None:
        print(f"Classifying {len(db_recs)} jobs...")
        for rec in tqdm(db_recs):
            if ('job_category' not in rec) or (rec['job_category'] == 'Classifier Error'):
                rec['job_category'] = jts.predict(rec['job_name'])
    
                db.update_jobs([rec])

@task
def reset_company(ctx, company_name):
    db = CareerCrawlerDB()
    db.remove_jobs_by_company_name(company_name)

    scrape(ctx, company_name)
    spec_classify(ctx)

@task
def train_model(c):
    jts = JobTypeSpecialist()
    jts._build()
    print(f"Model has been successfully built and saved as {jts.model_name}.")

@task
def evaluate_model(c):
    jts = JobTypeSpecialist(model_name='your_model_name_here')  # replace with your actual model name
    jts.evaluate()
    print("Model has been successfully evaluated. The confusion matrix is displayed above.")

