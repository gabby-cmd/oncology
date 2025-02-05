import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# Function to extract inclusion & exclusion criteria from ClinicalTrials.gov API
def fetch_trial_criteria(nct_id):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={nct_id}&max_rnk=1&fmt=xml"
    response = requests.get(url)

    if response.status_code == 200:
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        inclusion_criteria = []
        exclusion_criteria = []

        for study in root.iter('clinical_study'):
            for eligibility in study.iter('eligibility'):
                criteria_text = eligibility.find('criteria/textblock')
                
                if criteria_text is not None:
                    criteria_lines = criteria_text.text.split("\n")
                    inclusion_section = False
                    exclusion_section = False

                    for line in criteria_lines:
                        line = line.strip()
                        if "Inclusion Criteria" in line:
                            inclusion_section = True
                            exclusion_section = False
                            continue
                        elif "Exclusion Criteria" in line:
                            inclusion_section = False
                            exclusion_section = True
                            continue
                        
                        if inclusion_section and line:
                            inclusion_criteria.append(line)
                        elif exclusion_section and line:
                            exclusion_criteria.append(line)

        return {
            'inclusion': inclusion_criteria if inclusion_criteria else ["No inclusion criteria found"],
            'exclusion': exclusion_criteria if exclusion_criteria else ["No exclusion criteria found"]
        }

    return {'inclusion': ["Error fetching inclusion criteria"], 'exclusion': ["Error fetching exclusion criteria"]}

# Streamlit UI
st.title("Clinical Trial Eligibility Parser")
uploaded_file = st.sidebar.file_uploader("Upload Patient CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    patient_name = st.text_input("Enter Patient Name:")
    
    if patient_name:
        patient_data = df[df['Patient'].str.contains(patient_name, case=False, na=False)]
        
        if patient_data.empty:
            st.write(f"No patient found with the name {patient_name}.")
        else:
            primary_diagnosis = patient_data['Primarydiag'].iloc[0]
            nct_id = str(patient_data['NCTID'].iloc[0])  # Ensure it's a string

            st.write(f"**Patient's Condition:** {primary_diagnosis}")
            st.write(f"**Clinical Trial NCT ID:** [{nct_id}](https://clinicaltrials.gov/study/{nct_id})")

            criteria = fetch_trial_criteria(nct_id)

            st.write("### ✅ Inclusion Criteria")
            for point in criteria['inclusion']:
                st.write(f"- {point}")

            st.write("### ❌ Exclusion Criteria")
            for point in criteria['exclusion']:
                st.write(f"- {point}")
