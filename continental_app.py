import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import StringIO, BytesIO

# ================== CONFIG & DATA ==================
# Set a unique key for the application session state to ensure stability
if 'app_key' not in st.session_state:
    st.session_state['app_key'] = 'snooker_app_v1_csv'

st.set_page_config(page_title="Continental Snooker", page_icon="🎱", layout="wide")

# Prices per hour
PRICES = {
    "English Snooker Table 1": 240,
    "English Snooker Table 2": 240,
    "French Snooker Table": 180
}

# CSV file path (Using CSV eliminates the openpyxl dependency)
EXCEL_FILE = "snooker_bookings.csv" 

# ================== CUSTOM CSS (LIGHT & GOLD/BLACK THEME) ==================
st.markdown("""
    <style>
    /* 1. LIGHT GREY BACKGROUND (Stable) */
    .stApp {
        background-color: #f0f2f6; /* Light grey/off-white */
        color: #1a1a1a; /* Default text color is black */
    }

    /* 2. Title and Header Colors */
    h1, h2, h3, h4, h5, h6 {
        color: #DAA520 !important; /* Goldenrod color for headers */
    }
    .title-text {
        color: #1a1a1a !important; /* Black text for the main title */
        font-weight: bold;
    }
    
    /* 3. Input Fields: Light background, black text, gold border */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea, 
    .stSelectbox>div>div {
        background-color: #ffffff !important; 
        color: #1a1a1a !important; /* Black text */
        border: 2px solid #DAA520 !important; /* Gold border */
        border-radius: 8px; 
        padding: 8px;
    }
    
    /* 4. Custom Box Style: White box with Black/Gold border for sections */
    .custom-box {
        background-color: #ffffff; /* White background */
        padding: 20px; 
        border-radius: 15px;
        border: 3px solid #1a1a1a; /* Strong black border */
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); /* Soft shadow */
    }
    
    /* 5. Button Styling: Black button with Gold text */
    .stButton>button {
        background-color: #1a1a1a; /* Black button */
        color: #DAA520 !important; /* Gold text */
        border-radius: 12px; 
        font-weight: bold;
        border: 2px solid #DAA520; /* Gold border */
        transition: all 0.2s ease;
    }
    .stButton>button:hover { 
        background-color: #333333; /* Darken on hover */
        color: #ffdf70 !important; /* Lighter gold on hover */
        transform: scale(1.01);
    }
    
    /* 6. Metrics/Stats Box Styling */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #1a1a1a;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    [data-testid="stMetricValue"] {
        color: #DAA520 !important; 
        font-size: 1.8rem;
    }
    
    /* Dataframe header styling for better visibility on light background */
    .dataframe-header {
        background-color: #1a1a1a !important;
        color: #DAA520 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ================== TITLE & LAYOUT ==================

st.markdown(
    """
    <div style='text-align:center;'>
        <h1><span class='title-text'>Continental Snooker</span> 🎱</h1>
        <h3 style='margin-top:-10px;'>A Simple Booking Management Tool</h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

col_booking, col_confirm = st.columns(2)

# ================== COLUMN 1: NEW BOOKING ==================
with col_booking:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📝 New Booking")

    # Added unique keys to prevent StreamlitDuplicateElementId error
    name = st.text_input("Customer Name", key="customer_name")
    table = st.selectbox("Choose Table", list(PRICES.keys()), key="selected_table")
    start_time = st.text_input("Enter Start Time (hh:mm AM/PM)", "02:00 PM", key="start_time")
    end_time = st.text_input("Enter End Time (hh:mm AM/PM)", "03:00 PM", key="end_time")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ================== COLUMN 2: PRICE & CONFIRMATION ==================
with col_confirm:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("💲 Price & Confirmation")
    
    current_price_placeholder = st.empty()
    st.markdown("---")
    
    if st.button("💾 Save Booking", use_container_width=True, key="save_button"):
        
        # --- Validation & Calculation ---
        if not name.strip():
            st.error("❌ Customer Name cannot be empty.")
            st.stop()
        
        try:
            # Time Parsing
            start_dt = datetime.strptime(start_time.strip().upper(), "%I:%M %p")
            end_dt = datetime.strptime(end_time.strip().upper(), "%I:%M %p")

            # Duration/Cross-midnight handling
            delta = end_dt - start_dt
            if delta.total_seconds() < 0:
                 delta += pd.Timedelta(days=1) 
                 
            if delta.total_seconds() <= 0:
                st.error("❌ End time must be after start time.")
                
            # Final Calculation and Save
            else:
                hours = delta.total_seconds() / 3600
                price = round(hours * PRICES[table], 2)

                # --- CORE DATA SAVE LOGIC (Using CSV) ---
                if os.path.exists(EXCEL_FILE):
                    try:
                        # READ from CSV
                        df = pd.read_csv(EXCEL_FILE)
                    except Exception as e:
                        st.warning(f"Existing CSV file could not be read. Starting a new log. Error: {e}")
                        df = pd.DataFrame(columns=["Name", "Table", "Time", "Price", "Date"])
                else:
                    df = pd.DataFrame(columns=["Name", "Table", "Time", "Price", "Date"])

                new_row = {
                    "Name": name.strip(),
                    "Table": table,
                    "Time": f"{start_time} - {end_time}",
                    "Price": price,
                    "Date": datetime.today().strftime("%Y-%m-%d")
                }
                
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                # WRITE to CSV
                df.to_csv(EXCEL_FILE, index=False)
                # --- END CORE DATA SAVE LOGIC ---

                st.success(f"✅ Booking saved! Total Price: ₹{price:,.2f} for {round(hours, 2)} hours. Data saved to '{EXCEL_FILE}'.")
                st.balloons() 

        except ValueError: 
            st.error("⚠️ Invalid time format. Please use hh:mm AM/PM (e.g., 02:30 PM).")
        except Exception as e:
             st.error(f"⚠️ An unexpected error occurred: {e}")

    # Calculate and display current price estimate dynamically
    try:
        # Using session state for accurate dynamic calculation
        start_dt_calc = datetime.strptime(st.session_state.start_time.strip().upper(), "%I:%M %p")
        end_dt_calc = datetime.strptime(st.session_state.end_time.strip().upper(), "%I:%M %p")
        
        delta_calc = end_dt_calc - start_dt_calc
        if delta_calc.total_seconds() < 0:
            delta_calc += pd.Timedelta(days=1)
            
        hours_calc = delta_calc.total_seconds() / 3600
        price_calc = round(hours_calc * PRICES[st.session_state.selected_table], 2)
        
        current_price_placeholder.info(f"Hourly Rate: **₹{PRICES[st.session_state.selected_table]}** | Est. Price: **₹{price_calc:,.2f}** for {round(hours_calc, 2)} hours")
        
    except:
        current_price_placeholder.info(f"Hourly Rate: **₹{PRICES[table]}** | Enter valid times for estimate.")
        
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---") 

# ================== BOTTOM ROW: QUICK STATS & ALL BOOKINGS ==================

col_stats, col_bookings = st.columns([1, 2]) 

with col_stats:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📊 Quick Stats")

    if os.path.exists(EXCEL_FILE):
        try:
            # READ from CSV for stats
            df = pd.read_csv(EXCEL_FILE)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0) 
            
            total_bookings = len(df)
            total_revenue = df["Price"].sum()
            today_revenue = df[df["Date"] == datetime.today().strftime("%Y-%m-%d")]["Price"].sum()

            st.metric("Total Bookings", total_bookings)
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
            st.metric("Today's Revenue", f"₹{today_revenue:,.2f}")

            # Download button (Using CSV format for download)
            towrite = StringIO()
            df.to_csv(towrite, index=False)
            towrite.seek(0)
            
            st.download_button(
                label="📥 Download CSV",
                data=towrite.getvalue(),
                file_name="snooker_bookings.csv",
                mime="text/csv", # Changed MIME type
                use_container_width=True,
                key="download_button"
            )
        except Exception as e:
            st.error(f"Error reading stats from CSV: {e}")
    else:
        st.info("No bookings yet.")

    st.markdown("</div>", unsafe_allow_html=True)

with col_bookings:
    st.markdown("<div class='custom-box'>", unsafe_allow_html=True) 
    st.subheader("📋 All Saved Bookings")
    
    if os.path.exists(EXCEL_FILE):
        try:
            # READ from CSV for display
            df_all = pd.read_csv(EXCEL_FILE)
            st.dataframe(df_all.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
        except Exception as e:
            st.error(f"Error displaying bookings from CSV: {e}")
    else:
        st.info("No bookings saved yet.")
        
    st.markdown("</div>", unsafe_allow_html=True)

# ================== FILE LOCATION DISPLAY ==================
st.markdown("---")
st.markdown(f"""
<div style='font-size: small; color: #555;'>
    ℹ️ **File Location:** The booking data is stored in the **CSV file** `{EXCEL_FILE}` located in the same directory as this `app.py` file:
    <br/>
    <code>{os.path.abspath(EXCEL_FILE)}</code>
</div>
""", unsafe_allow_html=True)
