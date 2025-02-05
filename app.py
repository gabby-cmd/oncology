import streamlit as st
import pandas as pd

def check_eligibility(patient_data):
    """
    Check patient eligibility based on adapted criteria:
      - Inclusion criteria:
          1. Primary diagnosis should indicate type 1 diabetes.
          2. Prescription should mention CSII usage (e.g., "insulin pump" or "csii").
          3. Prescription should indicate use of a closed-loop device (e.g., "closed-loop" or "closed loop").
      - Exclusion criteria:
          1. Presence of "pregnancy" in either the diagnosis or prescription.
    """
    criteria = {}
    
    # Inclusion checks:
    primary_diag = patient_data.get("Primarydiag", "").lower()
    prescription = patient_data.get("Prescription", "").lower()
    
    # 1. Check if primary diagnosis indicates type 1 diabetes
    criteria["Diabetes Type 1"] = ("type 1" in primary_diag and "diabetes" in primary_diag)
    
    # 2. Check for evidence of CSII usage (for example, by looking for 'insulin pump' or 'csii' keywords)
    criteria["CSII Usage"] = ("insulin pump" in prescription or "csii" in prescription)
    
    # 3. Check for evidence of closed-loop device usage (look for 'closed-loop' or 'closed loop')
    criteria["Closed-Loop Device"] = ("closed-loop" in prescription or "closed loop" in prescription)
    
    # Calculate inclusion percentage based on available inclusion criteria.
    inclusion_count = sum(criteria.values())
    total_inclusion_criteria = len(criteria)
    inclusion_percentage = (inclusion_count / total_inclusion_criteria) * 100 if total_inclusion_criteria > 0 else 0
    
    # Exclusion check:
    exclusions = {}
    # For example, if the prescription or primary diagnosis mentions pregnancy, mark it as an exclusion.
    exclusions["Pregnancy"] = ("pregnancy" in primary_diag or "pregnancy" in prescription)
    
    exclusion_count = sum(exclusions.values())
    total_exclusion_criteria = len(exclusions)
    exclusion_percentage = (exclusion_count / total_exclusion_criteria) * 100 if total_exclusion_criteria > 0 else 0

    return inclusion_percentage, exclusion_percentage, criteria, exclusions

# Streamlit UI
st.title("Clinical Trial Eligibility Checker")

uploaded_file = st.file_uploader("Upload Patient Data (CSV)", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
    
    st.write("Data Preview:", df.head())

    # Check if the CSV has the required "Patient" column
    if "Patient" not in df.columns:
        st.error(f"CSV file is missing a 'Patient' column. Available columns: {', '.join(df.columns)}")
    else:
        patient_name = st.text_input("Enter Patient Name:")
        if patient_name:
            patient_row = df[df["Patient"] == patient_name]
            
            if not patient_row.empty:
                patient_data = patient_row.iloc[0].to_dict()
                st.write("Patient Details:")
                st.json(patient_data)
                
                inclusion_pct, exclusion_pct, inclusion_checks, exclusion_checks = check_eligibility(patient_data)
                
                st.write(f"*Inclusion Percentage:* {inclusion_pct:.2f}%")
                st.write(f"*Exclusion Percentage:* {exclusion_pct:.2f}%")
                
                st.write("### Inclusion Criteria Checks")
                for crit, passed in inclusion_checks.items():
                    st.write(f"- *{crit}:* {'Passed' if passed else 'Not passed'}")
                
                st.write("### Exclusion Criteria Checks")
                for crit, failed in exclusion_checks.items():
                    st.write(f"- *{crit}:* {'Found (Not eligible)' if failed else 'Not found'}")
                
                # Determine eligibility based on the adapted logic:
                if inclusion_pct >= 50 and exclusion_pct == 0:
                    st.success("Patient is likely eligible for the trial.")
                else:
                    st.error("Patient may not qualify for the trial.")
            else:
                st.warning("Patient not found in the dataset.")
