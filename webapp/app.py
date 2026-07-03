import streamlit as st
import pickle
import numpy as np
import os

# --- Page Configuration (Makes it look professional) ---
st.set_page_config(
    page_title="DataPulse - Salary Predictor",
    page_icon="📊",
    layout="centered"
)

# --- Load the trained model (with caching for speed) ---
@st.cache_resource
def load_model():
    model_path = "salary_predictor.pkl"
    if not os.path.exists(model_path):
        st.error("❌ Model not found! Please run 'datapulse samples/big_data.csv --train' first.")
        return None
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

# --- Main UI ---
st.title("📊 DataPulse Salary Predictor")
st.markdown("*Enter an age to predict the market salary based on our ML model.*")

# Load the model
model = load_model()

if model is not None:
    # --- User Input (Slider) ---
    age = st.slider(
        "Select Age (Years)",
        min_value=18,
        max_value=70,
        value=30,
        step=1
    )
    
    # --- Predict Button ---
    if st.button("🚀 Predict Salary", type="primary"):
        # Convert to numpy array and predict
        input_array = np.array([[age]])
        prediction = model.predict(input_array)[0]
        
        # Display the result beautifully
        st.success(f"### 💰 Predicted Salary: **${prediction:,.2f}**")
        
        # Show the formula used
        st.caption(f"*Formula used: Salary = 2989.95 * Age - 25613.31*")
        
        # Extra: Display a gauge or mini table
        st.metric(label="Age", value=f"{age} years")
        st.metric(label="Predicted Salary", value=f"${prediction:,.2f}")
        
        # Show a fun fact
        if age < 25:
            st.info("💡 Tip: Entry-level salaries typically range around $40K-$55K.")
        elif 25 <= age < 40:
            st.info("💡 Tip: Mid-career professionals with this experience usually earn $60K-$100K.")
        else:
            st.info("💡 Tip: Senior-level positions with this experience often exceed $120K.")
else:
    st.warning("⚠️ Please train the model first using the CLI.")
