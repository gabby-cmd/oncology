import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# Function to fetch inclusion/exclusion criteria from clinicaltrials.gov API
def fetch_trial_criteria(nct_id):
    # Construct API URL
    url = f'https://api.clinicaltrials.gov/v1/studies/{nct_id}'
    
    # Send GET request to fetch data
    response = requests.get(url)
    
    if response.status_code == 200:
        trial_data = response.json()
        inclusion_criteria = trial_data.get('inclusionCriteria', 'No inclusion criteria found')
        exclusion_criteria = trial_data.get('exclusionCriteria', 'No exclusion criteria found')
        return inclusion_criteria, exclusion_criteria
    else:
        return None, None

# Function to check if the patient's data matches inclusion/exclusion criteria
def check_inclusion_exclusion(patient_data, criteria_data):
    inclusion_count = 0
    exclusion_count = 0
    total_trials = len(criteria_data)

    # Loop through each patient and compare with trial criteria
    for _, patient_row in patient_data.iterrows():
        for _, criteria_row in criteria_data.iterrows():
            nct_id = criteria_row['NCT ID']
            inclusion_criteria, exclusion_criteria = fetch_trial_criteria(nct_id)
            
            if inclusion_criteria and exclusion_criteria:
                # Combine inclusion and exclusion criteria
                patient_diag = patient_row['Primarydiag'] + " " + str(patient_row['SecondaryDiag'])
                
                # Inclusion check
                if any(keyword.lower() in patient_diag.lower() for keyword in inclusion_criteria.split(";")):
                    inclusion_count += 1

                # Exclusion check
                if any(keyword.lower() in patient_diag.lower() for keyword in exclusion_criteria.split(";")):
                    exclusion_count += 1

    inclusion_percentage = (inclusion_count / total_trials) * 100 if total_trials else 0
    exclusion_percentage = (exclusion_count / total_trials) * 100 if total_trials else 0
    return inclusion_percentage, exclusion_percentage

# Streamlit UI
st.title("Patient Eligibility for Clinical Trials")

# File Uploads
sample_data = st.file_uploader("Upload the sample data CSV", type=["csv"])
master_file = st.file_uploader("Upload the master file CSV", type=["csv"])

if sample_data and master_file:
    # Load CSV files
    patient_data = pd.read_csv(sample_data)
    criteria_data = pd.read_csv(master_file)

    st.write("Sample Data:")
    st.dataframe(patient_data.head())

    st.write("Master File Data (Clinical Trial Criteria):")
    st.dataframe(criteria_data.head())

    # Input patient name for selection
    patient_name = st.text_input("Enter Patient Name to check eligibility:")

    if patient_name:
        # Filter data based on patient name
        selected_patient = patient_data[patient_data['Patient'].str.contains(patient_name, case=False, na=False)]
        
        if not selected_patient.empty:
            st.write(f"Selected Patient: {patient_name}")
            st.write(selected_patient)

            # Analyze eligibility based on clinicaltrials.gov inclusion/exclusion criteria
            inclusion_percentage, exclusion_percentage = check_inclusion_exclusion(selected_patient, criteria_data)

            # Display Results
            st.write(f"Inclusion Percentage: {inclusion_percentage:.2f}%")
            st.write(f"Exclusion Percentage: {exclusion_percentage:.2f}%")

            # Show Results in a Chart
            labels = ['Inclusion', 'Exclusion']
            values = [inclusion_percentage, exclusion_percentage]

            fig, ax = plt.subplots()
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
            st.pyplot(fig)

        else:
            st.warning("Patient not found in the sample data.")
