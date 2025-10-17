import streamlit as st
import google.generativeai as genai
import pandas as pd
import re


def find_nearby_facilities(location_query: str):
    """
    Finds nearby healthcare facilities using Gemini's Search grounding tool
    based on a text-based location query (e.g., "Austin, TX").

    Args:
        location_query (str): User's input location.
    Returns:
        str: Formatted text with hospital names and addresses.
    """
    try:
        # 1. Configure Gemini with API key
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

        # 2. Choose a grounded model (supports search)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # 3. Define the prompt and instructions
        system_prompt = (
            "You are a helpful emergency assistant. "
            "Use Google Search to find the top 3 nearest public or general hospitals near the user's requested location. "
            "Return results as a numbered list with the hospital name and full address."
        )

        user_query = (
            f"Find the 3 closest hospitals near: {location_query}. "
            "Provide only the hospital name and full address, formatted as a numbered list."
        )

        # 4. Generate response with Google Search tool
        response = model.generate_content(
            user_query,
            tools=[{"google_search": {}}],
            system_instruction=system_prompt
        )

        # 5. Return the formatted text (Gemini grounding returns plain text)
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        else:
            return "⚠️ No hospitals found. Try another location."

    except Exception as e:
        st.error(f"Error finding facilities: {e}")
        return "⚠️ Could not search for hospitals. Please check your Gemini API key and network connection."


def parse_facilities_to_df(text_result: str) -> pd.DataFrame:
    """
    Converts Gemini's text output (numbered list) into a simple DataFrame
    for optional mapping or display.
    """
    data = []
    pattern = r"\d+\.\s*(.+?),\s*(.+)"
    for match in re.findall(pattern, text_result):
        name, address = match
        data.append({"name": name.strip(), "address": address.strip()})
    return pd.DataFrame(data)


def show_facilities_results(location_query: str):
    """
    Combines search + display logic for easy use in Streamlit.
    """
    st.subheader("🗺️ Nearby Healthcare Facilities")

    result_text = find_nearby_facilities(location_query)
    st.markdown(result_text)

    # Optional: parse text into DataFrame (no coordinates yet)
    facilities_df = parse_facilities_to_df(result_text)

    if not facilities_df.empty:
        st.dataframe(facilities_df, use_container_width=True)
    else:
        st.info("Gemini returned text results only — no coordinates available for mapping.")


def show_facilities_map(facilities_df: pd.DataFrame):
    """
    Keeps backward compatibility if lat/lon are available in mock data.
    """
    if not facilities_df.empty and {"lat", "lon"}.issubset(facilities_df.columns):
        st.map(facilities_df[["lat", "lon"]])
        st.markdown("### 🏥 Nearby Healthcare Facilities (Mock Map)")
        for _, row in facilities_df.iterrows():
            st.markdown(f"**{row['name']}** \n📍 ({row['lat']:.4f}, {row['lon']:.4f})")
    else:
        st.warning("Map skipped — Gemini results do not include coordinates.")
