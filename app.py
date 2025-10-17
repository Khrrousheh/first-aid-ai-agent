import streamlit as st
import pandas as pd
from utils.map_helper import find_nearby_facilities, show_facilities_map
from utils.ai_helpers import analyze_image, generate_first_aid_steps


st.set_page_config(page_title="🩹 First Aid Assistant", layout="wide")

st.title("🩹 AI-Powered First Aid Assistant")
st.markdown(
    "Upload an image of an injury or describe it in text, and I’ll help you with immediate first aid steps. "
    "You can also find nearby hospitals."
)

# Sidebar options
with st.sidebar:
    st.header("Navigation")
    page = st.radio("Go to:", ["First Aid Guide", "Find Nearby Hospitals"])

# --- PAGE 1: First Aid Guide ---
if page == "First Aid Guide":
    st.subheader("Analyze Injury")

    uploaded_image = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
    injury_description = st.text_area("Or describe the injury:")

    if st.button("Analyze"):
        if uploaded_image:
            with st.spinner("Analyzing image..."):
                analysis = analyze_image(uploaded_image)
                st.success("✅ Image analyzed successfully.")
                st.markdown(f"**Analysis Result:** {analysis}")
                st.markdown("### 🩹 First Aid Steps")
                st.write(generate_first_aid_steps(analysis))
        elif injury_description:
            with st.spinner("Analyzing text..."):
                steps = generate_first_aid_steps(injury_description)
                st.success("✅ First aid advice ready.")
                st.markdown("### 🩹 First Aid Steps")
                st.write(steps)
        else:
            st.warning("Please upload an image or describe the injury.")

# --- PAGE 2: Find Nearby Hospitals ---
elif page == "Find Nearby Hospitals":
    st.subheader("🏥 Find Nearby Healthcare Facilities")

    location_query = st.text_input("Enter your city or address:", placeholder="e.g., Austin, TX")

    if st.button("Search Hospitals"):
        if location_query.strip():
            with st.spinner("🔍 Searching nearby hospitals..."):
                results_text = find_nearby_facilities(location_query)
                st.markdown("### 🏥 Nearby Hospitals")
                st.markdown(results_text)
        else:
            st.warning("Please enter a valid location.")

    # Optional mock map section for future expansion
    st.markdown("---")
    st.caption("If latitude/longitude data is available, hospitals will appear on the map below.")
    empty_df = pd.DataFrame(columns=["name", "lat", "lon"])
    show_facilities_map(empty_df)
