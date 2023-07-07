import langchain
from langchain.chat_models import ChatOpenAI
from langchain.llms import HuggingFacePipeline
import os

from langchain import PromptTemplate, LLMChain

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

        return [self.predict(job_title) for job_title in job_titles]