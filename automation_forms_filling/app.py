import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. PAGE CONFIGURATION (Must be the first line) ---
st.set_page_config(
    page_title="LOGWIN Tracking",
    layout="wide", # Important for the "Dashboard" look
    page_icon="📦"
)

# --- 2. SESSION STATE MANAGEMENT ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Dummy data for search
DUMMY_DB = {
    "SHIP001": {
        "Status": "In Transit",
        "MOT": "Sea",
        "Port of Origin": "Hamburg",
        "Port of Destination": "New York",
        "Shipment No.": "SHIP001",
        "House": "H123",
        "Master": "M456",
        "Shipper": "ACME Corp",
        "Consignee": "Globex Inc",
        "ETD": "2025-09-19",
        "ETA": "2025-10-05"
    },
    "SHIP002": {
        "Status": "Arrived",
        "MOT": "Air",
        "Port of Origin": "Tokyo Narita (NRT)",
        "Port of Destination": "Frankfurt (FRA)",
        "Shipment No.": "SHIP002",
        "House": "AWB-998",
        "Master": "MAWB-001",
        "Shipper": "Sony Electronics",
        "Consignee": "MediaMarkt DE",
        "ETD": "2025-09-20",
        "ETA": "2025-09-21"
    },
    "SHIP003": {
        "Status": "Customs Hold",
        "MOT": "Sea",
        "Port of Origin": "Shanghai",
        "Port of Destination": "Rotterdam",
        "Shipment No.": "SHIP003",
        "House": "H-SHANG-003",
        "Master": "MSC-T55",
        "Shipper": "Fast Textiles Ltd",
        "Consignee": "Fashion Nova",
        "ETD": "2025-08-15",
        "ETA": "2025-09-30"
    },
    "SHIP004": {
        "Status": "Delivered",
        "MOT": "Road",
        "Port of Origin": "Paris",
        "Port of Destination": "Berlin",
        "Shipment No.": "SHIP004",
        "House": "TRUCK-11",
        "Master": "DHL-Road",
        "Shipper": "L'Oreal Paris",
        "Consignee": "Rossmann",
        "ETD": "2025-09-10",
        "ETA": "2025-09-12"
    },
    "SHIP005": {
        "Status": "Pending",
        "MOT": "Rail",
        "Port of Origin": "Chengdu",
        "Port of Destination": "Warsaw",
        "Shipment No.": "SHIP005",
        "House": "RAIL-CN-PL",
        "Master": "CR-EXPRESS",
        "Shipper": "Lenovo China",
        "Consignee": "X-Kom PL",
        "ETD": "2025-10-01",
        "ETA": "2025-10-15"
    }
}

# --- 3. FUNCTION: GLOBAL CSS (The "Makeup") ---
def inject_custom_css():
    st.markdown("""
        <style>
        /* A. Remove default Streamlit margins to fit edges */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }
        
        /* B. The Green Top Bar (Header) */
        header {visibility: hidden;} /* Hide standard Streamlit header */
        
        .custom-header {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 60px;
            background-color: #8cb938; /* Approximate Logwin Green */
            color: white;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .header-logo {
            font-size: 24px;
            font-weight: bold;
            display: flex;
            align-items: center;
        }
        .header-user {
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .user-circle {
            background-color: #007bff;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        /* C. Style for "Card" containers (White boxes) */
        .css-card {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        
        /* D. Sidebar Style (Simulation) */
        [data-testid="stSidebar"] {
            background-color: #f0f0f0; /* Light gray */
            border-right: 1px solid #ddd;
        }
        
        /* E. Small UI adjustments */
        .breadcrumb {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .section-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        </style>
        
        <div class="custom-header">
            <div class="header-logo">
                ⬜ LOGWIN 
            </div>
            <div class="header-user">
                <span>🔔</span>
                <div class="user-circle">h</div>
                <div>
                    <div>Hannelore Bojes</div>
                    <div style="font-size:11px; opacity:0.8;">h.bojes</div>
                </div>
            </div>
        </div>
        <br><br> """, unsafe_allow_html=True)

# --- 4. LOGIN PAGE (Simplified for example) ---
def login_page():
    # CSS pour la page de login avec bordure légère
    st.markdown("""
        <style>
        /* Fond de page gris clair */
        .stApp {
            background-color: #f0f0f1 !important;
        }
        
        /* Cacher les éléments Streamlit par défaut */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Retirer le padding du container principal */
        .block-container {
            padding-top: 3rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* FOND BLANC pour le container du formulaire */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            background-color: #ffffff !important;
        }
        
        /* CACHER les labels au-dessus des champs */
        .stTextInput > label {
            display: none !important;
        }
        
        /* Input fields styling - CHAMPS PLUS GRANDS */
        .stTextInput > div > div > input {
            border: 1px solid #d0d0d0 !important;
            border-radius: 3px !important;
            padding: 11px 14px !important;
            font-size: 14px !important;
            background-color: white !important;
            width: 100% !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #8cb938 !important;
            box-shadow: 0 0 0 1px #8cb938 !important;
            outline: none !important;
        }
        
        /* Style pour le bouton Anmelden (vert LOGWIN) */
        div.stButton > button {
            background-color: #8cb938 !important;
            color: white !important;
            border: none !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            padding: 11px 20px !important;
            border-radius: 3px !important;
            transition: all 0.2s ease;
            width: 100% !important;
            text-transform: none !important;
        }
        
        div.stButton > button:hover {
            background-color: #7aa330 !important;
            box-shadow: 0 2px 6px rgba(140, 185, 56, 0.4) !important;
        }

        /* Style pour la checkbox "Stay signed in" - CENTREE */
        .stCheckbox {
            margin-top: 12px !important;
            margin-bottom: 20px !important;
            display: flex !important;
            justify-content: center !important;
        }
        
        .stCheckbox > label {
            font-size: 13px !important;
            color: #666 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        /* Centrer l'image du logo */
        .stImage {
            display: flex;
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Layout centré avec colonnes plus étroites
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    
    with col2:
        # Espacement vertical pour centrer
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # UTILISER st.container() avec border=True pour la card
        with st.container(border=True):
            # Logo depuis le dossier assets
            try:
                st.image("assets/logo.png", width=220)
            except:
                st.markdown("""
                    <div style='text-align:center; margin-bottom: 25px; color: #999;'>
                        <p style='font-size:12px;'>⚠️ Logo: <code>assets/logo.png</code></p>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Champs de saisie avec PLACEHOLDER (texte dans le champ)
            username = st.text_input(
                "username", 
                key="login_user", 
                placeholder="Benutzername *",
                label_visibility="collapsed"
            )
            
            password = st.text_input(
                "password", 
                type="password", 
                key="login_pass", 
                placeholder="Passwort",
                label_visibility="collapsed"
            )
            
            # Checkbox "Stay signed in" CENTREE
            st.checkbox("Stay signed in", key="stay_signed")
            
            # Bouton Anmelden
            if st.button("Anmelden", use_container_width=True, key="login_btn"):
                if username and password:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Bitte geben Sie Benutzername und Passwort ein.")
            
            # Lien "Open Tracking" en bas
            st.markdown("""
                <div style='text-align:center; margin-top:20px;'>
                    <a href='#' style='color:#666; font-size:13px; text-decoration:none;'>Open Tracking</a>
                </div>
            """, unsafe_allow_html=True)

# --- 5. DASHBOARD PAGE (The requested interface) ---
def dashboard_page():
    inject_custom_css()
    
    # --- A. Sidebar (Left Menu) ---
    with st.sidebar:
        st.markdown("<br><br>", unsafe_allow_html=True) # Space for the green header
        st.markdown("### START")
        st.markdown("🎛️ Dashboard")
        
        st.markdown("### TRACKING")
        # Simulating an active menu item with background color
        st.info("📦 Track shipments") 
        st.markdown("container Track containers")
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # --- B. Main Content Area ---
    
    # Breadcrumb
    st.markdown('<div class="breadcrumb"> > Tracking > Track shipments</div>', unsafe_allow_html=True)
    
    # --- Block 1: SEARCH ---
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Search ✏️</div>', unsafe_allow_html=True)
        
        # Row 1
        c1, c2, c3 = st.columns(3)
        with c1: st.selectbox("Status", ["- All -"])
        with c2: st.selectbox("MOT", ["- All -"])
        with c3: shipment_input = st.text_input("Shipment No.", key="search_input")
        
        # Row 2
        c4, c5, c6 = st.columns(3)
        with c4: st.text_input("House")
        with c5: st.text_input("PO Number")
        with c6: st.text_input("Shipper Ref.")

        # Row 3
        c7, c8, c9 = st.columns(3)
        with c7: st.text_input("Additional Ref.")
        with c8: st.text_input("Container")
        with c9: 
            # Simulation of ETD dates (From - To)
            sc1, sc2 = st.columns(2)
            with sc1: st.date_input("ETD From", value=None)
            with sc2: st.date_input("ETD To", value=None)

        col_search, col_space = st.columns([1, 5])
        with col_search:
            search_clicked = st.button("🔍 Search", type="primary")

        st.markdown('</div>', unsafe_allow_html=True) # End Search card

    # --- Block 2: RESULT ---
    
    # Simple search logic
    df_result = pd.DataFrame() # Empty by default
    
    if search_clicked and shipment_input:
        if shipment_input in DUMMY_DB:
            # If found, create a DataFrame with data
            data = DUMMY_DB[shipment_input]
            df_result = pd.DataFrame([data])
            st.success("Record found.")
        else:
            st.warning("No records found.")
    
    # Display result
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">Result ({len(df_result)})</div>', unsafe_allow_html=True)
    
    if not df_result.empty:
        # Display "Excel" style table
        st.dataframe(
            df_result,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="medium"),
                "ETD": st.column_config.DateColumn("ETD", format="DD/MM/YYYY"),
                "ETA": st.column_config.DateColumn("ETA", format="DD/MM/YYYY"),
            }
        )
        # Simulated pagination
        st.markdown("<div style='text-align:right; color:#666; font-size:12px;'>1-1 of 1 records &nbsp; < &nbsp; > </div>", unsafe_allow_html=True)
    else:
        # Empty table to keep visual structure
        empty_cols = ["Status", "MOT", "Port of Origin", "Port of Destination", "Shipment No.", "House", "Master", "ETD"]
        st.dataframe(pd.DataFrame(columns=empty_cols), hide_index=True, use_container_width=True)
        st.markdown("<div style='text-align:center; color:#999; padding:20px;'>0-0 of 0 records</div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) # End Result card


# --- 6. MAIN ROUTER ---
if __name__ == "__main__":
    if st.session_state.logged_in:
        dashboard_page()
    else:
        login_page()