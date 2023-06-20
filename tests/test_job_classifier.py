import pytest
import sys

from career_crawler.classifiers import JobTypeClassifier

@pytest.fixture
def job_type_classifier():
    return JobTypeClassifier()

def test_job_type_classifier_predict(job_type_classifier):

    assert job_type_classifier.predict("data scientist") == "Data Science, Machine Learning and AI"
    assert job_type_classifier.predict("machine learning engineer") == "Data Science, Machine Learning and AI"
    assert job_type_classifier.predict("ai engineer") == "Data Science, Machine Learning and AI"
    assert job_type_classifier.predict("ai scientist") == "Data Science, Machine Learning and AI"
    assert job_type_classifier.predict("ai researcher") == "Data Science, Machine Learning and AI"
    assert job_type_classifier.predict("software engineer") == "Software Engineering"
    assert job_type_classifier.predict("marketing manager") == "Marketing"
    assert job_type_classifier.predict("marketing director") == "Marketing"
    assert job_type_classifier.predict("email marketing specialist") == "Marketing"
    assert job_type_classifier.predict("sales director") == "Sales"
    assert job_type_classifier.predict("sales rep") == "Sales"
    assert job_type_classifier.predict("sales manager") == "Sales"
    assert job_type_classifier.predict("rvp - sales") == "Sales"
    assert job_type_classifier.predict("legal counzel") == "Other"
    assert job_type_classifier.predict("customer support") == "Other"
    assert job_type_classifier.predict("customer service") == "Other"
    assert job_type_classifier.predict("finance analyst") == "Other"
    assert job_type_classifier.predict("production manager") == "Producers, Production and Project Management"
    assert job_type_classifier.predict("project manager") == "Producers, Production and Project Management"
    assert job_type_classifier.predict("project coordinator") == "Producers, Production and Project Management"
    assert job_type_classifier.predict("project director") == "Producers, Production and Project Management"
    assert job_type_classifier.predict("associate producer") == "Producers, Production and Project Management"
