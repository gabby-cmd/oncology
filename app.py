import streamlit as st
import requests
from bs4 import BeautifulSoup

# Function to scrape inclusion and exclusion criteria from clinicaltrials.gov
def fetch_criteria(nct_id):
    url = f"https://clinicaltrials.gov/ct2/show/{nct_id}?term={nct_id}&rank=1"
    response = requests.get(url)

    if response.status_code != 200:
        st.error(f"Failed to retrieve data for NCT ID: {nct_id}. Please check the ID and try again.")
        return None, None
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Scrape Inclusion and Exclusion Criteria (located under <div class="inclusion"> and <div class="exclusion">)
    inclusion_criteria = []
    exclusion_criteria = []

    # Try to find inclusion criteria
    inclusion_section = soup.find("div", {"class": "inclusion"})
    if inclusion_section:
        for li in inclusion_section.find_all("li"):
            inclusion_criteria.append(li.get_text(strip=True))
    else:
        st.warning("No inclusion criteria found for this trial.")

    # Try to find exclusion criteria
    exclusion_section = soup.find("div", {"class": "exclusion"})
    if exclusion_section:
        for li in exclusion_section.find_all("li"):
            exclusion_criteria.append(li.get_text(strip=True))
    else:
        st.warning("No exclusion criteria found for this trial.")

    return inclusion_criteria, exclusion_criteria

# Function to check eligibility based on patient data and criteria
def check_eligibility(patient_data, inclusion_criteria, exclusion_criteria):
    inclusion_matches = 0
    exclusion_matches = 0

    # Check for Inclusion Criteria
    for criterion in inclusion_criteria:
        if criterion.lower() in patient_data.lower():
            inclusion_matches += 1

    # Check for Exclusion Criteria
    for criterion in exclusion_criteria:
        if criterion.lower() in patient_data.lower():
            exclusion_matches += 1

    # Calculate percentages
    inclusion_percentage = (inclusion_matches / len(inclusion_criteria)) * 100 if inclusion_criteria else 0
    exclusion_percentage = (exclusion_matches / len(exclusion_criteria)) * 100 if exclusion_criteria else 0

    # Determine eligibility
    if exclusion_matches > 0:
        result = "Exclusion"
    else:
        result = "Inclusion"
    
    return result, inclusion_percentage, exclusion_percentage

# Streamlit UI
st.title('Clinical Trial Eligibility Check')

# Input for the NCT ID and patient data
nct_id = st.text_input('Enter NCT ID of Clinical Trial')

# Refining patient input fields
patient_name = st.text_input('Enter Patient Name')
patient_age = st.number_input('Enter Patient Age', min_value=0, max_value=120, value=30)
patient_gender = st.selectbox('Select Patient Gender', ['Male', 'Female', 'Other'])
patient_medical_conditions = st.text_area('Enter Patient Medical Conditions (e.g., Diabetes, Hypertension, etc.)')

# Ensure all fields are filled in before proceeding
if st.button('Check Eligibility'):
    if nct_id and patient_name and patient_age and patient_gender and patient_medical_conditions:
        # Fetch inclusion/exclusion criteria for the provided NCT ID
        inclusion_criteria, exclusion_criteria = fetch_criteria(nct_id)
        
        if inclusion_criteria is not None and exclusion_criteria is not None:
            # Process patient data (combine structured fields for matching)
            patient_data = f"Age: {patient_age}, Gender: {patient_gender}, Conditions: {patient_medical_conditions}"
            
            # Check eligibility based on inclusion/exclusion criteria
            result, inclusion_percentage, exclusion_percentage = check_eligibility(patient_data, inclusion_criteria, exclusion_criteria)
            
            # Display results
            st.subheader(f"Patient: {patient_name}")
            st.write(f"Eligibility: {result}")
            st.write(f"Inclusion Criteria Match: {inclusion_percentage:.2f}%")
            st.write(f"Exclusion Criteria Match: {exclusion_percentage:.2f}%")
        else:
            st.error("Failed to retrieve inclusion/exclusion criteria from clinicaltrials.gov.")
    else:
        st.error("Please fill in all fields.")
