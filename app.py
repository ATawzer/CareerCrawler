import streamlit as st
import pandas as pd
from career_crawler.db import CareerCrawlerDB
import os
from dotenv import load_dotenv

load_dotenv()

def status(n_hours):
    db = CareerCrawlerDB()
    new_jobs = db.get_new_jobs(n_hours)

    # Create DataFrame from job data
    jobs_df = pd.DataFrame(new_jobs)

    # Check for missing 'https://' in link and add if necessary
    jobs_df.loc[jobs_df['link'].str.contains("https://") == False, 'link'] = "https://boards.greenhouse.io" + jobs_df['link']

    # Convert 'job_location' None values to "Unknown"
    jobs_df['job_location'].fillna('Unknown', inplace=True)

    # Sort jobs by job_category and then by company_name
    jobs_df.sort_values(by=['job_category', 'company_name'], inplace=True)

    return jobs_df

def main():
    st.title('Career Crawler Streamlit App')

    # Refresh button
    if st.button('Refresh'):
        with st.spinner('Retrieving jobs...'):
            # Retrieve jobs
            jobs_df = status(7)

            # Create separate tables for each job_category
            for category, df in jobs_df.groupby('job_category'):
                st.subheader(category)
                for idx, row in df.iterrows():
                    st.write(f"{row['company_name']:40} - [{row['job_name']:80}]({row['link']}) - {row['job_location']:40}")

        st.success('Updated!')

if __name__ == "__main__":
    main()
