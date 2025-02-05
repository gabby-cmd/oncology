import streamlit as st
import pandas as pd

# Define trial inclusion and exclusion criteria
INCLUSION_CRITERIA = {
    "Condition": "Diabetes type 1",
    "CSII_Usage_Months": 6,
    "HbA1c_Max": 11,
    "CGM_Usage_Months": 6,
    "Device": "Tandem t:slim X2"
}

EXCLUSION_CRITERIA = [
    "Pregnancy or Lactation",
    "Uncontrolled diabetic retinopathy",
    "Disease affecting glucose metabolism"
]

def check_eligibility(patient_data):
    """Check patient eligibility based on inclusion/exclusion criteria."""
    inclusion_checks = {
        "Condition": patient_data.get("Condition") == INCLUSION_CRITERIA["Condition"],
        "CSII Usage": patient_data.get("CSII_Usage_Months", 0) >= INCLUSION_CRITERIA["CSII_Usage_Months"],
        "HbA1c": patient_data.get("HbA1c", 0) <= INCLUSION_CRITERIA["HbA1c_Max"],
        "CGM Usage": patient_data.get("CGM_Usage_Months", 0) >= INCLUSION_CRITERIA["CGM_Usage_Months"],
        "Device": patient_data.get("Device") == INCLUSION_CRITERIA["Device"]
    }
    
    # Handle exclusions - check if 'Exclusions' is a string before splitting
    exclusions = patient_data.get("Exclusions", "")
    exclusion_list = []
    if isinstance(exclusions, str):  # Only split if it's a string
        exclusion_list = [exclusion.strip() for exclusion in exclusions.split(",")]
    
    # Check if any exclusion matches the defined exclusion criteria
    exclusion_checks = [exclusion in exclusion_list for exclusion in EXCLUSION_CRITERIA]
    
    inclusion_percentage = sum(inclusion_checks.values()) / len(inclusion_checks) * 100
    exclusion_percentage = sum(exclusion_checks) / len(EXCLUSION_CRITERIA) * 100
    
    return inclusion_percentage, exclusion_percentage

# Streamlit UI
st.title("Clinical Trial Eligibility Checker")

uploaded_file = st.file_uploader("Upload Patient Data (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())

    patient_name = st.text_input("Enter Patient Name:")
    if patient_name:
        patient_row = df[df["Name"] == patient_name]
        
        if not patient_row.empty:
            patient_data = patient_row.iloc[0].to_dict()
            inclusion_pct, exclusion_pct = check_eligibility(patient_data)
            
            st.write(f"*Inclusion Percentage:* {inclusion_pct:.2f}%")
            st.write(f"*Exclusion Percentage:* {exclusion_pct:.2f}%")
            
            if inclusion_pct >= 50 and exclusion_pct == 0:
                st.success("Patient is likely eligible for the trial.")
            else:
                st.error("Patient may not qualify for the trial.")
        else:
            st.warning("Patient not found in the dataset.")
