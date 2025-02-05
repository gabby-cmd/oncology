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
        return f"Error fetching data (Status code: {response.status_code})", "", [], []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Debugging: Print the full page text to see what is being fetched
    print(soup.prettify()[:2000])  # Print first 2000 characters to check structure
    
    # Find the participation criteria section
    criteria_section = soup.find("div", {"id": "participation-criteria"})
    
    if not criteria_section:
        return "No eligibility criteria section found", "", [], []

    # Debugging: Print extracted text
    print("\nExtracted Participation Criteria Section:\n", criteria_section.get_text("\n"))

    # Extract the entire raw text
    criteria_text = criteria_section.get_text("\n").strip()

    # Ensure inclusion and exclusion criteria are properly parsed
    inclusion_text = ""
    exclusion_text = ""
    inclusion_criteria = []
    exclusion_criteria = []

    if "Inclusion Criteria" in criteria_text:
        inclusion_start = criteria_text.index("Inclusion Criteria") + len("Inclusion Criteria")
        exclusion_start = criteria_text.index("Exclusion Criteria") if "Exclusion Criteria" in criteria_text else len(criteria_text)

        inclusion_text = criteria_text[inclusion_start:exclusion_start].strip()
        exclusion_text = criteria_text[exclusion_start:].strip() if "Exclusion Criteria" in criteria_text else ""

        inclusion_criteria = [line.strip() for line in inclusion_text.split("\n") if line.strip()]
        exclusion_criteria = [line.strip() for line in exclusion_text.split("\n") if line.strip()]

    return inclusion_text, exclusion_text, inclusion_criteria, exclusion_criteria

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
            inclusion_text, exclusion_text, inclusion, exclusion = fetch_eligibility_criteria(nct_id)

            # Display raw parsed text before points
            st.subheader("Raw Inclusion Criteria Text")
            st.write(inclusion_text if inclusion_text else "No inclusion criteria found.")

            st.subheader("Raw Exclusion Criteria Text")
            st.write(exclusion_text if exclusion_text else "No exclusion criteria found.")

            # Display results as bullet points
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
