[7:15 PM, 2/4/2025] michu 🐩: import streamlit as st
import pandas as pd
import json

# Load clinical trial data (replace this with actual data retrieval)
clinical_trial_data = {
    "nctId": "NCT04939766",
    "title": "Impact of the Use of a Closed-loop Insulin Therapy on the Burden of Diabetes and the Quality of Life",
    "sponsor": "VitalAire",
    "eligibilityCriteria": {
        "inclusion": [
            "Type 1 diabetic patients undergoing a CSII therapy for at least 6 months",
            "Using Tandem t:slim X2 for at least 4 weeks",
            "Using CGM for 6 months including Dexcon G6 for at least 4 weeks",
            "Eligible according to French Society recommendations",
            "HbA1c below 11%"
        ],
        "exclusion": [
            "Pregnancy or lactation",
            "Diabetic retinopathy not controlled by laser",
            "Disease or treatment altering glucose metabolism"
        ]
    }
}

# Streamlit UI
st.title("Clinical Trial Eligibility Checker")
st.write("Upload a CSV file containing patient data and input a patient’s name to check their eligibility.")

# File uploader
uploaded_file = st.file_uploader("Upload Patient Data (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Patient Data Preview:")
    st.dataframe(df)

    # Input patient name
    patient_name = st.text_input("Enter Patient Name:")

    if patient_name:
        # Find patient data
        patient_row = df[df['Name'] == patient_name]

        if not patient_row.empty:
            st.write(f"Details for {patient_name}:")
            st.write(patient_row)

            # Extract patient criteria
            patient_criteria = {
                "diabetes_type": "Type 1" in patient_row["Condition"].values[0],
                "csii_usage": patient_row["CSII_Usage_Months"].values[0] >= 6,
                "tandem_usage": patient_row["Tandem_Usage_Weeks"].values[0] >= 4,
                "cgm_usage": patient_row["CGM_Usage_Months"].values[0] >= 6 and "Dexcom G6" in patient_row["CGM_Type"].values[0],
                "hba1c": patient_row["HbA1c"].values[0] < 11,
                "pregnancy": patient_row["Pregnant"].values[0] == "No",
                "retinopathy": patient_row["Retinopathy_Controlled"].values[0] == "Yes",
                "glucose_altering_disease": patient_row["Glucose_Altering_Disease"].values[0] == "No"
            }

            # Calculate inclusion/exclusion percentage
            inclusion_matches = sum([
                patient_criteria["diabetes_type"],
                patient_criteria["csii_usage"],
                patient_criteria["tandem_usage"],
                patient_criteria["cgm_usage"],
                patient_criteria["hba1c"]
            ])
            exclusion_matches = sum([
                not patient_criteria["pregnancy"],
                not patient_criteria["retinopathy"],
                not patient_criteria["glucose_altering_disease"]
            ])

            total_criteria = len(patient_criteria)
            inclusion_percentage = (inclusion_matches / total_criteria) * 100
            exclusion_percentage = (exclusion_matches / total_criteria) * 100

            st.write(f"Inclusion Percentage: {inclusion_percentage:.2f}%")
            st.write(f"Exclusion Percentage: {exclusion_percentage:.2f}%")

            if inclusion_percentage > 50 and exclusion_percentage == 0:
                st.success(f"{patient_name} is likely eligible for the clinical trial.")
            else:
                st.warning(f"{patient_name} may not be eligible based on the provided criteria.")

        else:
            st.error("Patient not found in the uploaded file.")
[7:21 PM, 2/4/2025] michu 🐩: import streamlit as st
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
    
    exclusion_checks = [exclusion in patient_data.get("Exclusions", "") for exclusion in EXCLUSION_CRITERIA]
    
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
