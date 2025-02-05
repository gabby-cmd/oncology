import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to get inclusion and exclusion criteria
def fetch_eligibility_criteria(nct_id):
    url = f"https://clinicaltrials.gov/study/{nct_id}#participation-criteria"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Error fetching data", []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find the participation criteria section
    criteria_section = soup.find("div", {"id": "participation-criteria"})
    if not criteria_section:
        return "No eligibility criteria found", []
    
    # Extract inclusion and exclusion criteria
    criteria_text = criteria_section.get_text("\n").split("Exclusion Criteria:")
    
    inclusion_criteria = criteria_text[0].replace("Inclusion Criteria:", "").strip().split("\n") if "Inclusion Criteria:" in criteria_text[0] else []
    exclusion_criteria = criteria_text[1].strip().split("\n") if len(criteria_text) > 1 else []
    
    return inclusion_criteria, exclusion_criteria

# Streamlit UI
st.title("Clinical Trial Eligibility Checker")

# Upload dataset
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Display dataset preview
    st.write("Dataset Preview:", df.head())

    # Select a patient ID
    patient_id = st.selectbox("Select Patient ID", df["PatientID"].unique())

    # Filter for selected patient
    patient_data = df[df["PatientID"] == patient_id]

    if not patient_data.empty:
        nct_id = str(patient_data["NCTID"].iloc[0])
        
        if pd.isna(nct_id) or nct_id.strip() == "":
            st.error("No NCT ID found for this patient.")
        else:
            st.write(f"Fetching criteria for **NCT ID: {nct_id}**")
            inclusion, exclusion = fetch_eligibility_criteria(nct_id)

            # Display results
            st.subheader("Inclusion Criteria")
            if inclusion:
                for point in inclusion:
                    st.write(f"✅ {point}")
            else:
                st.warning("No inclusion criteria found.")

            st.subheader("Exclusion Criteria")
            if exclusion:
                for point in exclusion:
                    st.write(f"❌ {point}")
            else:
                st.warning("No exclusion criteria found.")

            # Display study link
            st.markdown(f"[View Full Study Details](https://clinicaltrials.gov/study/{nct_id}#participation-criteria)", unsafe_allow_html=True)
