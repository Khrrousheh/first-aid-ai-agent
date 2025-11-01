import streamlit as st
import google.generativeai as genai
import pandas as pd
import re


def find_nearby_facilities(location_query: str):
    """
    Finds nearby healthcare facilities using Gemini's grounded search tool
    based on a text-based location query (e.g., "Austin, TX").
    """
    try:
        # 1. Configure Gemini API
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        # 2. Use the grounded (Google search) mode
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            # generation_config={"mode": "google_search_retrieval"}
        )

        # 3. Build prompts
        system_prompt = (
            "You are a helpful emergency assistant. "
            "Use Google Search to find the top 3 nearest public or general hospitals "
            "near the user's requested location. "
            "Return results as a numbered list with the hospital name and full address."
            "return latitude/longitude for each hospital"
        )

        user_prompt = (
            f"Find the 3 closest hospitals near: {location_query}. "
            "Provide only the hospital name and full address, formatted as a numbered list."
        )

        # 4. Generate response
        response = model.generate_content([system_prompt, user_prompt])

        # 5. Return formatted text
        if response and hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            return "⚠️ No hospitals found. Try another location."

    except Exception as e:
        st.error(f"Error finding facilities: {e}")
        return "⚠️ Could not search for hospitals. Please check your Gemini API key and network connection."


def parse_facilities_to_df(text_result: str) -> pd.DataFrame:
    """
    Converts Gemini's text output (numbered list) into a simple DataFrame.
    Example input:
      1. Austin General Hospital, 123 Main St, Austin, TX
    """
    data = []
    # Regex looks for lines like "1. Name, Address"
    pattern = r"\d+\.\s*(.+?),\s*(.+)"
    for match in re.findall(pattern, text_result):
        name, address = match
        data.append({"name": name.strip(), "address": address.strip()})

    return pd.DataFrame(data)


def show_facilities_results(location_query: str):
    """
    Combines search + display logic for Streamlit.
    """
    st.subheader("🗺️ Nearby Healthcare Facilities")

    with st.spinner("Searching for nearby hospitals..."):
        result_text = find_nearby_facilities(location_query)

    st.markdown(result_text)

    facilities_df = parse_facilities_to_df(result_text)

    if not facilities_df.empty:
        st.dataframe(facilities_df, use_container_width=True)
    else:
        st.info("Gemini returned text results only — no coordinates available for mapping.")


def show_facilities_map(facilities_df: pd.DataFrame):
    """
    Displays a map if lat/lon are available.
    """
    if not facilities_df.empty and {"lat", "lon"}.issubset(facilities_df.columns):
        st.map(facilities_df[["lat", "lon"]])
        st.markdown("### 🏥 Nearby Healthcare Facilities (Map)")
        for _, row in facilities_df.iterrows():
            st.markdown(f"**{row['name']}** \n📍 ({row['lat']:.4f}, {row['lon']:.4f})")
    else:
        st.warning("Map skipped — Gemini results do not include coordinates.")


# --- Streamlit UI Layout ---
st.set_page_config(page_title="Nearby Healthcare Finder", page_icon="🏥", layout="centered")

st.title("🏥 Nearby Healthcare Facilities Finder")
st.write("Enter a city, state, or area to find hospitals near you.")

location_query = st.text_input("📍 Enter a location", placeholder="e.g., Austin, TX")

if st.button("Find Hospitals") and location_query:
    show_facilities_results(location_query)
