from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import HuggingFacePipeline
import os
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
import numpy as np

from langchain import PromptTemplate, LLMChain
from .db import CareerCrawlerDB

class JobTypeClassifier:

    def __init__(self, model_id="google/flan-t5-xl"):
        self.llm = HuggingFacePipeline.from_model_id(model_id=model_id, task="text2text-generation", model_kwargs={"temperature":1})
        #self.llm = ChatOpenAI(openai_api_key=os.environ.get('OPENAI_API_KEY'), model_name='gpt-3.5-turbo')

        self.categories = {
            "1": "Data Science, Machine Learning and AI",
            "2": "Software Engineering",
            "3": "Marketing",
            "4": "Sales",
            "5": "Producers, Production and Project Management",
            "6": "Other"
        }

        self.template = """
            Categorize '{job_title}' as one of the following, only returning the number:
            1 Data Science, Machine Learning and AI
            2 Software Engineering
            3 Marketing
            4 Sales
            5 Producers, Production and Project Management
            6 Other
        """
        self.prompt = PromptTemplate(template=self.template, input_variables=["job_title"])

        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def predict(self, job_title):
        """
        Returns the predicted job type as a string
        """

        try:
            return self.categories[self.llm_chain.run(job_title=job_title)]
        except:
            return "Classifier Error"
        
    def bulk_predict(self, job_titles):
        """
        Returns a list of predicted job types as strings
        """

        predictions = self.llm_chain.run(job_title=job_titles)
        return [self.categories[prediction] for prediction in predictions]
    
class JobTypeSpecialist:

    def __init__(self, model_name=None):
        self.db = CareerCrawlerDB()
        self.le = LabelEncoder()

        self.model_name = model_name
        if self.model_name is not None:
            try:
                self.model = joblib.load(f"./models/{self.model_name}")
                self.le = joblib.load(f"./models/{self.model_name}_le")
            except:
                self.model = None
        else:
            self.model = None

    def _build(self):
        """
        Builds a model to predict job type from job title
        """
        if self.model is None:
            self.model_name = "job_type_assistant"+datetime.now().strftime("%Y%m%d%H%M%S")
            self.model = Pipeline([
                ("tfidf", TfidfVectorizer()),
                ("clf", SGDClassifier())
            ])

            job_titles, job_types = self._get_train_data()
            job_types_encoded = self.le.fit_transform(job_types)

            self.model.fit(job_titles, job_types_encoded)

            # Save the trained model and LabelEncoder
            joblib.dump(self.model, f"./models/{self.model_name}")
            joblib.dump(self.le, f"./models/{self.model_name}_le")
        else:
            print(f"Model {self.model_name} already loaded.")

    def _get_train_data(self):
        """
        Returns a list of tuples of the form (job_title, job_type)
        """
        result = self.db.get_jobs(fields=["job_name", "job_category"])
        job_titles = [x['job_name'] for x in result if ('job_category' in x) and (x['job_category'] != 'Classifier Error')]
        job_types = [x['job_category'] for x in result if ('job_category' in x) and (x['job_category'] != 'Classifier Error')]
        self.le.fit(job_types)
        return job_titles, job_types

    def predict(self, job_title):
        """
        Predicts the job type based on the job title.
        """
        if self.model is None:
            print("Model not built or loaded.")
            return None
        
        # Predict the encoded label
        encoded_label = self.model.predict([job_title])

        # Convert the encoded label to the original readable label using inverse_transform
        readable_label = self.le.inverse_transform(encoded_label)
        
        return readable_label[0]

    
    def evaluate(self):
        """
        Evaluates the model's performance using a confusion matrix.
        """
        self._build()

        # Split the data into training and testing sets
        job_titles, job_types = self._get_train_data()
        job_types_encoded = self.le.fit_transform(job_types)
        X_train, X_test, y_train, y_test = train_test_split(job_titles, job_types_encoded, test_size=0.2, random_state=42)

        # Fit the model on the training set
        self.model.fit(X_train, y_train)

        # Make predictions on the testing set
        y_pred = self.model.predict(X_test)

        # Display a classification report
        print(classification_report(y_test, y_pred, target_names=self.le.classes_))

        # Display a random sample of examples for each category
        df = pd.DataFrame({
            'job_title': X_test,
            'true_job_type': self.le.inverse_transform(y_test),
            'pred_job_type': self.le.inverse_transform(y_pred)
        })

        random_samples = df.groupby('true_job_type').apply(lambda x: x.sample(n=5, random_state=np.random.RandomState(42))).reset_index(drop=True)
        print("\nRandom samples for each category:")
        print(random_samples)