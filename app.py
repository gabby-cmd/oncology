import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# Streamlit UI to upload CSV
st.title("Oncology Clinical Trial Inclusion/Exclusion Criteria")
st.sidebar.header("Upload your patient dataset")

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload Patient CSV", type=["csv"])

# Placeholder for displaying criteria
criteria_display = st.empty()

# Function to display patient details
def display_patient_data(patient_name, df):
    # Filter patient data based on the input name
    patient_data = df[df['Patient'].str.contains(patient_name, case=False, na=False)]
    
    if patient_data.empty:
        st.write(f"No patient found with the name {patient_name}.")
        return None
    else:
        # Display relevant patient details
        relevant_columns = ['PatientID', 'Primarydiag', 'SecondaryDiag', 'PrimaryInsurance']
        st.write("### Patient Details")
        st.write(patient_data[relevant_columns])
        return patient_data

# Function to fetch NCT ID from ClinicalTrials.gov API
def fetch_first_nct_id(condition):
    url = f"https://clinicaltrials.gov/api/query/study_fields?expr={condition}&fields=NCTId&max_rnk=1&fmt=json"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        studies = data.get("StudyFieldsResponse", {}).get("StudyFields", [])
        
        if studies and "NCTId" in studies[0] and studies[0]["NCTId"]:
            return studies[0]["NCTId"][0]  # Get the first available NCT ID

    return None  # Return None if no NCT ID is found

# Function to fetch clinical trial criteria based on NCT ID
def fetch_trial_criteria(nct_id):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={nct_id}&max_rnk=1&fmt=xml"
    response = requests.get(url)

    if response.status_code == 200:
        # Parse XML response
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        inclusion_criteria = []
        exclusion_criteria = []

        for study in root.iter('clinical_study'):
            for eligibility in study.iter('eligibility'):
                criteria_text = eligibility.find('criteria/textblock')
                
                if criteria_text is not None:
                    # Split criteria into points
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

    return {
        'inclusion': ["Error fetching inclusion criteria"],
        'exclusion': ["Error fetching exclusion criteria"]
    }

# CSV processing logic
if uploaded_file is not None:
    # Read the dataset
    df = pd.read_csv(uploaded_file)
    
    # Text input for patient name
    patient_name = st.text_input("Enter Patient Name:")

    if patient_name:
        patient_data = display_patient_data(patient_name, df)

        if patient_data is not None and not patient_data.empty:
            condition = patient_data['Primarydiag'].iloc[0]  # Get the primary diagnosis
            st.write(f"**Patient's Condition (Primary Diagnosis):** {condition}")
            
            # Fetch first NCT ID related to the condition
            nct_id = fetch_first_nct_id(condition)

            if nct_id:
                st.write(f"**First Clinical Trial NCT ID:** [{nct_id}](https://clinicaltrials.gov/study/{nct_id})")
                
                # Fetch inclusion/exclusion criteria
                criteria = fetch_trial_criteria(nct_id)

                # Display Inclusion Criteria
                criteria_display.write("### ✅ Inclusion Criteria")
                for point in criteria['inclusion']:
                    criteria_display.write(f"- {point}")

                # Display Exclusion Criteria
                criteria_display.write("### ❌ Exclusion Criteria")
                for point in criteria['exclusion']:
                    criteria_display.write(f"- {point}")

            else:
                st.error("No clinical trials found for this condition.")

