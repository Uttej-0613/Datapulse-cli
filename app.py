import streamlit as st
import pickle
import numpy as np

# Load the trained model
@st.cache_resource
def load_model():
    with open('salary_predictor.pkl', 'rb') as f:
        return pickle.load(f)

model = load_model()

# --- UI ---
st.set_page_config(page_title="Salary Predictor AI", page_icon="💰")
st.title("💰 AI Salary Predictor")
st.markdown("Predict your salary based on your age using Machine Learning")

st.divider()

# Input
age = st.slider("Select your age:", min_value=18, max_value=80, value=25, step=1)

# Predict
if st.button("Predict Salary", type="primary"):
    prediction = model.predict([[age]])
    st.success(f"💵 Predicted Salary: **${prediction[0]:,.2f}**")
    
    # Show the formula
    st.caption(f"Formula: Salary = {model.coef_[0]:.2f} * Age + {model.intercept_:.2f}")

st.divider()
st.caption("Built with Linear Regression | DataPulse Project")
