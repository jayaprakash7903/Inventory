import streamlit as st
import io
import zipfile
import pandas as pd
import datetime
import os
from modules.scanner1 import decode_barcode_from_bytes
from database.db_manager1 import create_tables, save_packing_slip

# Initialize session state properly
class SessionState:
    def __init__(self):
        self.header = None
        self.items = []

if 'app_state' not in st.session_state:
    st.session_state.app_state = SessionState()

# Initialize database
create_tables()

# UI Configuration
st.set_page_config(page_title="FLS Bawal Inventory", page_icon="🔍")
st.title("📦 FLS Packing Tracker")

# Helper function for image input
def get_image_input(label):
    option = st.radio(f"{label} - Input Method:", 
                     ["Camera", "Upload"], 
                     horizontal=True,
                     key=f"input_{label}")
    if option == "Camera":
        return st.camera_input(label)
    return st.file_uploader(label, type=['jpg', 'png', 'jpeg'])

# Step 1: Scan Item Barcodes
st.header("Step 1: Scan Items")
num_items = st.number_input("Number of items to scan:", min_value=1, value=1, step=1)

# Ensure items list is properly sized
while len(st.session_state.app_state.items) < num_items:
    st.session_state.app_state.items.append(None)

for i in range(num_items):
    with st.expander(f"Item {i+1}", expanded=True):
        image = get_image_input(f"Scan Item {i+1}")
        if image:
            barcode = decode_barcode_from_bytes(image.getvalue())
            if barcode:
                st.session_state.app_state.items[i] = {
                    "item_id": barcode,
                    "description": "",
                    "quantity": 1,
                    "image": None
                }
                st.success(f"✅ Scanned Item {i+1}: {barcode}")
            else:
                st.warning("No barcode detected. Try again.")

# Step 2: Header Barcode
st.header("Step 2: Scan Header")
header_img = get_image_input("Scan Header Barcode")
if header_img:
    header_code = decode_barcode_from_bytes(header_img.getvalue())
    if header_code:
        st.session_state.app_state.header = header_code
        st.success(f"✅ Scanned Header: {header_code}")
    else:
        st.warning("No barcode detected in header. Try again.")

# Packing Slip Details
st.header("Packing Details")
customer_name = st.text_input("Customer Name")
location = st.text_input("Location")
time_of_packing = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Item Management
if any(st.session_state.app_state.items):
    st.header("📝 Item Details")
    for idx, item in enumerate(st.session_state.app_state.items.copy(), 1):
        if item is None:
            continue
            
        cols = st.columns([4, 1])
        with cols[0]:
            st.subheader(f"Item {idx}: {item['item_id']}")
            item["description"] = st.text_input(
                "Description", 
                value=item.get("description", ""),
                key=f"desc_{idx}"
            )
            item["quantity"] = st.number_input(
                "Quantity",
                min_value=1,
                value=item.get("quantity", 1),
                key=f"qty_{idx}"
            )
            
            if st.button(f"📷 Capture Image", key=f"img_btn_{idx}"):
                img = get_image_input(f"Capture Item {idx} Image")
                if img:
                    item["image"] = img.getvalue()
        
        with cols[1]:
            if st.button("❌", key=f"del_{idx}"):
                st.session_state.app_state.items.pop(idx-1)
                st.rerun()

# Save Functionality
st.header("Save Data")
if st.button("💾 Save Packing Slip"):
    if not st.session_state.app_state.header:
        st.error("Please scan header barcode")
    elif not any(item for item in st.session_state.app_state.items if item):
        st.error("Please scan at least one valid item")
    elif not customer_name:
        st.error("Please enter customer name")
    else:
        save_packing_slip(
            {
                "header_id": st.session_state.app_state.header,
                "customer_name": customer_name,
                "location": location,
                "time_of_packing": time_of_packing
            },
            [item for item in st.session_state.app_state.items if item]
        )
        st.success("Packing slip saved successfully!")

# Export Functionality
@st.cache_data
def export_data():
    import database.db_manager1 as db
    conn = db.create_connection()
    df_slips = pd.read_sql("SELECT * FROM packing_slip", conn)
    df_items = pd.read_sql("SELECT * FROM packing_items", conn)
    conn.close()
    return df_slips, df_items

if st.button("📤 Export Data"):
    df_slips, df_items = export_data()
    
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, 'w') as zip_file:
            zip_file.writestr('packing_slips.csv', df_slips.to_csv(index=False))
            zip_file.writestr('packing_items.csv', df_items.to_csv(index=False))
        buffer.seek(0)
        st.download_button(
            "Download Data as ZIP",
            data=buffer,
            file_name="packing_data.zip",
            mime="application/zip"
        )