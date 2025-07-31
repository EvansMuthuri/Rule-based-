
import streamlit as st
import pandas as pd # Still useful for organizing input, but not for training
import os

# --- Helper Function for Text Symptom Parsing ---
def parse_text_symptoms(text_input, all_symptoms_list):
    """
    Parses free-form text input to identify presence of symptoms.
    Returns a dictionary of symptoms (0 or 1).
    """
    detected_symptoms = {s: 0 for s in all_symptoms_list}
    text_input_lower = text_input.lower()

    # Define keywords for each symptom. Expand this list for better accuracy.
    symptom_keywords = {
        'fever': ['fever', 'hot', 'temperature', 'warm', 'febrile'],
        'headache': ['headache', 'head ache', 'head pain', 'cephalgia'],
        'chills': ['chills', 'shivering', 'cold sweats', 'rigors'],
        'fatigue': ['fatigue', 'tired', 'weary', 'exhausted', 'lack of energy', 'weakness', 'lethargy'],
        'nausea': ['nausea', 'sick to stomach', 'feeling sick'],
        'vomiting': ['vomiting', 'throwing up', 'puking', 'emesis'],
        'joint_pain': ['joint pain', 'joint aches', 'aching joints', 'arthralgia'],
        'sweating': ['sweating', 'night sweats', 'diaphoresis'],
        'muscle_pain': ['muscle pain', 'body aches', 'muscle aches', 'myalgia'],
        'diarrhea': ['diarrhea', 'loose stools', 'runny stomach'],
        'abdominal_pain': ['abdominal pain', 'stomach pain', 'belly ache', 'tummy ache'],
        'convulsions': ['convulsions', 'seizures', 'fits', 'epileptic'],
        'coma': ['coma', 'unconscious', 'unresponsive'],
        'impaired_consciousness': ['impaired consciousness', 'confused', 'dizzy', 'drowsy', 'disoriented', 'altered mental state'],
        'anemia': ['anemia', 'pale', 'weak blood', 'low blood'],
        'loss_of_appetite': ['loss of appetite', 'no appetite', 'don\'t want to eat', 'anorexia'],
        'cough': ['cough', 'coughing'],
        'jaundice': ['jaundice', 'yellow skin', 'yellow eyes', 'icterus'],
        'dark_urine': ['dark urine', 'dark pee', 'tea-colored urine'],
        'rapid_breathing': ['rapid breathing', 'fast breathing', 'shortness of breath', 'tachypnea'],
        'rapid_heart_rate': ['rapid heart rate', 'fast heartbeat', 'palpitations', 'tachycardia'],
        'spleen_enlargement': ['spleen enlargement', 'enlarged spleen', 'splenomegaly'],
        'liver_enlargement': ['liver enlargement', 'enlarged liver', 'hepatomegaly'],
        'head_spinning': ['head spinning', 'lightheadedness'],
        'general_malaise': ['general malaise', 'feeling unwell', 'malaise'],
        'body_aches': ['body aches', 'body pain'], # Added explicitly
        'weakness': ['weakness', 'feeling weak', 'lack of strength'] # Added explicitly
    }

    for symptom, keywords in symptom_keywords.items():
        for keyword in keywords:
            if keyword in text_input_lower:
                detected_symptoms[symptom] = 1
                break # Move to next symptom once a keyword is found

    return detected_symptoms

# --- Streamlit App Layout ---
st.set_page_config(
    page_title="Malaria Diagnosis for Kids: Empowering Health in Kenya", # Updated Title
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for a better look (Orange theme)
st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 3.2em;
        color: #FF6F00; /* Vibrant Orange */
        text-align: center;
        margin-bottom: 0.2em;
        font-weight: bold;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    /* Subheader styling */
    .subheader {
        font-size: 1.6em;
        color: #666666;
        text-align: center;
        margin-bottom: 1.8em;
        font-weight: normal;
    }
    /* Banner/Hero section styling */
    .hero-banner {
        background: linear-gradient(135deg, #FFA000 0%, #FF6F00 100%); /* Orange gradient */
        padding: 40px 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2em;
        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    }
    .hero-banner h1 {
        color: white;
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    .hero-banner p {
        font-size: 1.1em;
        opacity: 0.9;
    }

    /* Button styling */
    .stButton>button {
        background-color: #4CAF50; /* Green for action */
        color: white;
        padding: 12px 25px;
        border-radius: 8px;
        border: none;
        font-size: 1.2em;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        transition: all 0.3s ease-in-out;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    /* Diagnosis box styling */
    .diagnosis-box {
        border-radius: 12px;
        padding: 25px;
        margin-top: 25px;
        font-size: 1.4em;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .diagnosis-positive {
        background-color: #ffebeb; /* Lighter red tint */
        color: #d90000; /* Stronger red */
        border: 2px solid #ff3333;
    }
    .diagnosis-negative {
        background-color: #ebffeb; /* Lighter green tint */
        color: #009900; /* Stronger green */
        border: 2px solid #33cc33;
    }
    .diagnosis-uncertain {
        background-color: #fff3cd; /* Light yellow */
        color: #856404; /* Darker yellow */
        border: 2px solid #ffc107;
    }
    .stCheckbox {
        font-size: 1.1em;
        margin-bottom: 0.5em;
    }
    .stInfo {
        background-color: #e0f2f7;
        border-left: 5px solid #2196F3;
        padding: 10px;
        border-radius: 5px;
        margin-top: 15px;
        font-size: 0.95em;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown("<p class='main-header'>Malaria Diagnosis Application</p>", unsafe_allow_html=True)
# st.markdown("<p class='subheader'>A Rule-Based Symptom Checker for Kenyan High Schools</p>", unsafe_allow_html=True)

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <h1>Empowering Health Decisions with Knowledge</h1>
    <p>Join us in using technology to make a difference in our community's health!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
We are Machakos Girls High School, and this is our Rule-Based Symptom Diagnosis Application designed to predict whether a patient may be suffering from malaria. This project 
aims to contribute towards reducing malaria-related mortality in Kenya by enabling early detection and encouraging timely medical intervention.
""")

st.markdown("---")

# Define all possible symptoms (expanded list)
all_symptoms = [
    'fever', 'headache', 'chills', 'fatigue', 'nausea',
    'vomiting', 'joint_pain', 'sweating', 'muscle_pain',
    'diarrhea', 'abdominal_pain', 'convulsions', 'coma',
    'impaired_consciousness', 'anemia', 'loss_of_appetite',
    'cough', 'jaundice', 'dark_urine', 'rapid_breathing',
    'rapid_heart_rate', 'spleen_enlargement', 'liver_enlargement',
    'head_spinning', 'general_malaise',
    'body_aches', # Added missing symptom
    'weakness'    # Added missing symptom
]

# --- Input Method Selection ---
st.header("1. Choose How to Input Symptoms")
input_method = st.radio(
    "Select your preferred method:",
    ("Select from List (Checkboxes)", "Describe Symptoms (Text Input)"),
    key="input_method_radio"
)

# Initialize patient_symptoms dictionary
patient_symptoms = {s: 0 for s in all_symptoms}

# --- Functionality 1: Checkbox Selection ---
if input_method == "Select from List (Checkboxes)":
    st.markdown("---")
    st.header("2. Tick the Symptoms You See")
    st.markdown("Please check all symptoms that apply to the patient:")

    num_cols = len(all_symptoms)
    cols = st.columns(3) # Use 3 columns for better layout

    for i, symptom in enumerate(all_symptoms):
        with cols[i % 3]: # Distribute checkboxes across 3 columns
            patient_symptoms[symptom] = int(st.checkbox(symptom.replace('_', ' ').title(), value=False, key=f"cb_{symptom}"))

# --- Functionality 2: Text Input ---
elif input_method == "Describe Symptoms (Text Input)":
    st.markdown("---")
    st.header("2. Describe the Patient's Symptoms")
    st.markdown("Please list the symptoms the patient is experiencing in your own words (e.g., 'They have a high fever, a bad headache, and feel very tired.').")
    text_symptom_input = st.text_area("Type symptoms here:", height=100, key="text_symptom_area")

    if text_symptom_input:
        # Parse text input to update patient_symptoms
        parsed_symptoms = parse_text_symptoms(text_symptom_input, all_symptoms)
        # Update patient_symptoms with detected ones
        patient_symptoms.update(parsed_symptoms)

        st.markdown("**Symptoms detected from your description:**")
        detected_count = 0
        for s, present in patient_symptoms.items():
            if present == 1:
                st.write(f"- {s.replace('_', ' ').title()}")
                detected_count += 1
        if detected_count == 0:
            st.write("No specific symptoms detected from text. Please try different wording or use checkboxes.")

# --- Diagnosis Button ---
st.markdown("---")
st.header("3. Get Your Diagnosis")
diagnose_button = st.button("Diagnose Malaria Likelihood")

# --- Rule-Based Diagnosis Logic ---
if diagnose_button:
    malaria_likelihood = "Uncertain" # Default
    diagnosis_reason = []

    # Convert patient_symptoms dict to a more readable format for rules
    s = patient_symptoms

    # --- Define Diagnosis Rules (Illustrative and Simplified) ---
    # These rules are ordered from most indicative to least indicative.
    # Severity is considered.

    # Rule 1: Severe Malaria Symptoms (Highest Priority)
    if s['convulsions'] or s['coma'] or s['impaired_consciousness'] or s['rapid_breathing'] or s['anemia'] or s['jaundice']:
        malaria_likelihood = "High Probability of Severe Malaria"
        diagnosis_reason.append("Presence of severe symptoms (like convulsions, coma, impaired consciousness, rapid breathing, severe anemia, or jaundice) indicates a **high probability of severe malaria**. This requires **immediate medical attention**.")
    # Rule 2: Classic Malaria Triad + Fatigue/Muscle Pain
    elif s['fever'] and s['chills'] and s['sweating'] and (s['fatigue'] or s['muscle_pain'] or s['body_aches']):
        malaria_likelihood = "High Probability of Malaria"
        diagnosis_reason.append("The classic malaria triad (fever, chills, sweating) combined with significant fatigue or muscle aches strongly suggests malaria.")
    # Rule 3: Fever + Multiple Other Common Symptoms
    elif s['fever'] and (s['headache'] + s['nausea'] + s['vomiting'] + s['joint_pain'] + s['loss_of_appetite'] + s['diarrhea'] >= 2):
        malaria_likelihood = "Moderate to High Probability of Malaria"
        diagnosis_reason.append("Fever combined with two or more other common symptoms (like headache, nausea, vomiting, joint pain, loss of appetite, or diarrhea) indicates a moderate to high probability of malaria.")
    # Rule 4: Fever + Headache + General Malaise/Weakness
    elif s['fever'] and s['headache'] and (s['general_malaise'] or s['weakness']):
        malaria_likelihood = "Moderate Probability of Malaria"
        diagnosis_reason.append("Fever, headache, and general feeling unwell or weakness are common indicators of malaria.")
    # Rule 5: Fever + Chills (even without sweating)
    elif s['fever'] and s['chills']:
        malaria_likelihood = "Moderate Probability of Malaria"
        diagnosis_reason.append("Fever and chills are strong indicators, even if sweating is not prominent.")
    # Rule 6: Fever with some GI issues
    elif s['fever'] and (s['diarrhea'] or s['abdominal_pain'] or s['vomiting']):
        malaria_likelihood = "Possible Malaria (with GI Symptoms)"
        diagnosis_reason.append("Fever accompanied by gastrointestinal symptoms (diarrhea, abdominal pain, or vomiting) suggests possible malaria.")
    # Rule 7: Only Fever
    elif s['fever']:
        malaria_likelihood = "Possible Malaria (Fever Only)"
        diagnosis_reason.append("Fever is present, which is a primary malaria symptom. Further investigation is recommended as fever can be due to many causes.")
    # Rule 8: No Fever but other significant symptoms (e.g., body aches, fatigue, chills)
    elif (s['chills'] or s['sweating'] or s['fatigue'] or s['muscle_pain'] or s['joint_pain'] or s['body_aches'] or s['general_malaise']) and not s['fever']:
        malaria_likelihood = "Low Probability of Malaria / Consider Other Causes"
        diagnosis_reason.append("Malaria is less likely without fever, but other general symptoms are present. Consider other diagnoses or atypical malaria presentation. Seek medical advice if symptoms persist.")
    # Rule 9: No symptoms selected
    else:
        malaria_likelihood = "Malaria Unlikely Based on Symptoms"
        diagnosis_reason.append("No strong indicators of malaria were selected or detected from your input. If you are concerned, please consult a healthcare professional.")

    # --- Display Diagnosis Result ---
    st.subheader("Diagnosis Result:")
    if "High Probability" in malaria_likelihood or "Severe Malaria" in malaria_likelihood:
        st.markdown(f"<div class='diagnosis-box diagnosis-positive'>{malaria_likelihood}</div>", unsafe_allow_html=True)
    elif "Moderate Probability" in malaria_likelihood or "Possible Malaria" in malaria_likelihood or "Requires Medical Evaluation" in malaria_likelihood:
        st.markdown(f"<div class='diagnosis-box diagnosis-uncertain'>{malaria_likelihood}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='diagnosis-box diagnosis-negative'>{malaria_likelihood}</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Reasoning for this Diagnosis:")
    for reason in diagnosis_reason:
        st.write(f"- {reason}")

    st.markdown("---")
    st.info("Disclaimer: This tool is for educational purposes only and provides a diagnosis based on predefined rules. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for any health concerns.")


