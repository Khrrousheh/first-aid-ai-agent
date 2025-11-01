import streamlit as st
import pandas as pd
from utils.map_helper import (
    find_nearby_facilities, 
    find_nearby_facilities_by_coords,
    show_facilities_map, 
    parse_facilities_to_df,
    reverse_geocode
)
from utils.ai_helpers import analyze_image, generate_first_aid_steps
from streamlit_geolocation import streamlit_geolocation


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
    
    # Initialize session state for location
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None
    if 'use_auto_location' not in st.session_state:
        st.session_state.use_auto_location = False
    
    # Option 1: Use Device Location (Auto-detect)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**📍 Option 1: Use My Location**")
        use_location = st.button("🗺️ Detect My Location", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("**🔍 Option 2: Search by Address**")
        location_query = st.text_input(
            "Enter city or address:", 
            placeholder="e.g., Austin, TX",
            label_visibility="collapsed"
        )
        search_location = st.button("🔍 Search Hospitals", use_container_width=True)
    
    # Handle geolocation request
    if use_location:
        st.session_state.use_auto_location = True
    
    # Get user's geolocation if requested
    if st.session_state.use_auto_location:
        st.info("📍 **Your browser will now prompt you for location permission.**\n\nYou'll see options to:\n- ✅ **Allow this time** (one-time access)\n- ✅ **Allow always** (remember this choice)\n- ❌ **Deny** (block location access)")
        
        # Use streamlit-geolocation component which triggers browser's native permission dialog
        # The browser's native dialog will show: "Allow this time", "Allow always", or "Deny"
        try:
            location_data = streamlit_geolocation(key="location_request")
            
            # Check if location was successfully obtained
            if location_data and isinstance(location_data, dict) and 'latitude' in location_data and 'longitude' in location_data:
                lat = location_data['latitude']
                lon = location_data['longitude']
                st.session_state.user_location = {'lat': lat, 'lon': lon}
                
                # Get address from coordinates
                address = reverse_geocode(lat, lon)
                
                if address:
                    st.success(f"✅ Location detected: {address}")
                    st.caption(f"Coordinates: {lat:.6f}, {lon:.6f}")
                else:
                    st.success(f"✅ Location detected at coordinates: {lat:.6f}, {lon:.6f}")
                
                # Automatically search for hospitals
                with st.spinner("🔍 Searching nearby hospitals..."):
                    results_text = find_nearby_facilities_by_coords(lat, lon)
                    st.markdown("### 🏥 Nearby Hospitals")
                    st.markdown(results_text)
                    
                    # Parse results and show map
                    facilities_df = parse_facilities_to_df(results_text)
                    
                    if not facilities_df.empty:
                        # Add user location to map
                        user_df = pd.DataFrame([{
                            "name": "Your Location",
                            "address": address or f"Lat: {lat}, Lon: {lon}",
                            "lat": lat,
                            "lon": lon
                        }])
                        
                        # Combine user location with facilities
                        combined_df = pd.concat([user_df, facilities_df], ignore_index=True)
                        
                        st.markdown("---")
                        st.markdown("### 📍 Hospital Locations Map")
                        st.map(combined_df, zoom=13)
                        
                        # Show facilities in a list
                        st.markdown("### 📋 Hospitals Nearby")
                        for idx, row in facilities_df.iterrows():
                            if "lat" in row and "lon" in row:
                                st.markdown(f"**{idx + 1}. {row['name']}**")
                                st.markdown(f"📍 {row['address']}")
                                st.markdown(f"Coordinates: ({row['lat']:.4f}, {row['lon']:.4f})")
                            else:
                                st.markdown(f"**{idx + 1}. {row['name']}**")
                                st.markdown(f"📍 {row['address']}")
                            st.markdown("---")
                
                # Reset auto location flag after successful location
                st.session_state.use_auto_location = False
            elif location_data is not None:
                st.warning("⚠️ Unable to get your location. Please check your browser permissions or try searching by address.")
                st.session_state.use_auto_location = False
        except Exception as e:
            st.error(f"Error getting location: {e}")
            st.info("💡 Please try searching by address instead, or check your browser's location permissions.")
            st.session_state.use_auto_location = False
    
    # Handle manual search by address
    elif search_location:
        if location_query.strip():
            with st.spinner("🔍 Searching nearby hospitals..."):
                results_text = find_nearby_facilities(location_query)
                st.markdown("### 🏥 Nearby Hospitals")
                st.markdown(results_text)
                
                # Parse results and show map
                facilities_df = parse_facilities_to_df(results_text)
                
                if not facilities_df.empty:
                    st.markdown("---")
                    st.markdown("### 📍 Hospital Locations Map")
                    show_facilities_map(facilities_df)
        else:
            st.warning("Please enter a valid location.")
