[8:31 PM, 2/4/2025] michu 🐩: import streamlit as st
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

# Patient Data logic
def display_patient_data(patient_name, df):
    # Filter patient data based on the input name
    patient_data = df[df['Patient'].str.contains(patient_name, case=False, na=False)]
    
    if patient_data.empty:
        st.write(f"No patient found with the name {patient_name}.")
    else:
        st.write(f"Patient Data: {patient_data}")
     …
[8:40 PM, 2/4/2025] michu 🐩: import streamlit as st
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

# Patient Data logic
def display_patient_data(patient_name, df):
    # Filter patient data based on the input name
    patient_data = df[df['Patient'].str.contains(patient_name, case=False, na=False)]
    
    if patient_data.empty:
        st.write(f"No patient found with the name {patient_name}.")
    else:
        st.write(f"Patient Data: {patient_data}")
        return patient_data

# Function to fetch clinical trial criteria from ClinicalTrials.gov API
def fetch_clinical_trial_criteria(condition):
    url = f'https://clinicaltrials.gov/api/query/full_studies?expr={condition}&max_rnk=1&fmt=xml'
    response = requests.get(url)

    if response.status_code == 200:
        # Parse XML response
        tree = ET.ElementTree(ET.fromstring(response.content))
        root = tree.getroot()

        # Extract inclusion and exclusion criteria
        inclusion_criteria = None
        exclusion_criteria = None

        # Find the relevant sections in the XML (these tags may vary, you need to inspect the XML structure)
        for study in root.iter('clinical_study'):
            for arm in study.iter('arm_group'):
                if arm.find('arm_group_label') is not None:
                    arm_label = arm.find('arm_group_label').text
                    if 'Inclusion' in arm_label:
                        inclusion_criteria = arm.find('description').text
                    elif 'Exclusion' in arm_label:
                        exclusion_criteria = arm.find('description').text

        # Return the criteria if found
        return {
            'inclusion': inclusion_criteria or "No inclusion criteria found",
            'exclusion': exclusion_criteria or "No exclusion criteria found"
        }
    else:
        return {
            'inclusion': "Error fetching inclusion criteria",
            'exclusion': "Error fetching exclusion criteria"
        }

# CSV processing logic
if uploaded_file is not None:
    # Read the dataset
    df = pd.read_csv(uploaded_file)
    st.write(df.head())  # Displaying the first few rows for reference

    # Text input for patient name
    patient_name = st.text_input("Enter Patient Name:")

    if patient_name:
        patient_data = display_patient_data(patient_name, df)

        if not patient_data.empty:
            # Assuming the diagnosis code is in the 'Primarydiag' column (adjust accordingly)
            condition = patient_data['Primarydiag'].iloc[0]  # Modify this logic based on your dataset
            st.write(f"Patient's Condition (Primary Diagnosis): {condition}")
            
            # Fetch clinical trial criteria based on the condition (diagnosis)
            criteria = fetch_clinical_trial_criteria(condition)
            
            # Display the inclusion and exclusion criteria
            criteria_display.write("### Inclusion Criteria")
            criteria_display.write(criteria['inclusion'])
            criteria_display.write("### Exclusion Criteria")
            criteria_display.write(criteria['exclusion'])

            # Criteria Matching Logic
            inclusion_criteria = criteria['inclusion']
            exclusion_criteria = criteria['exclusion']
            
            # Example logic to compare
            if inclusion_criteria and inclusion_criteria.lower() in patient_data['Primarydiag'].iloc[0].lower():
                st.write("Patient meets the inclusion criteria!")
            else:
                st.write("Patient does not meet the inclusion criteria.")
            
            if exclusion_criteria and exclusion_criteria.lower() in patient_data['Primarydiag'].iloc[0].lower():
                st.write("Patient meets the exclusion criteria!")
            else:
                st.write("Patient does not meet the exclusion criteria.")
