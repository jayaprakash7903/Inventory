import streamlit as st
import io
import zipfile
import pandas as pd
from modules.Scanner import RealTimeBarcodeScanner
from database.db_manager import create_tables, save_packing_slip, create_connection

# Create database tables at startup.
create_tables()

# Initialize session state variables.
if "header" not in st.session_state:
    st.session_state["header"] = ""
if "items" not in st.session_state:
    st.session_state["items"] = []  # Each item is a dict with keys: "item_id", "description", "quantity", "image"
if "captured_image" not in st.session_state:
    st.session_state["captured_image"] = None

st.title("Logistic Packing Slip App")

# ---------- Header Section ----------
st.header("Header Barcode")
if st.button("Scan Header Barcode"):
    scanned_header = RealTimeBarcodeScanner()
    if scanned_header:
        st.session_state["header"] = scanned_header
        st.success(f"Header scanned: {scanned_header}")
    else:
        st.error("Header scan failed!")

# Manual override for header barcode.
header_val = st.text_input("Header Barcode", value=st.session_state["header"])

# ---------- Packing Slip Details ----------
st.header("Packing Slip Details")
customer_name = st.text_input("Customer Name")
location = st.text_input("Location")
time_of_packing = st.text_input("Time of Packing (YYYY-MM-DD HH:MM)")

# ---------- Items Section ----------
st.header("Items")
num_items = st.number_input("Number of Items", min_value=1, step=1, value=1)

# Button to scan an item barcode. Each click appends a new item entry.
if st.button("Scan Item Barcode"):
    scanned_item = RealTimeBarcodeScanner()
    if scanned_item:
        st.session_state["items"].append({
            "item_id": scanned_item,
            "description": "",
            "quantity": 1,
            "image": None  # Will be updated if an image is captured.
        })
        st.success(f"Item scanned: {scanned_item}")
    else:
        st.error("Item scan failed!")

# Display scanned items with inputs for description and quantity.
if st.session_state["items"]:
    st.subheader("Item Details")
    for idx, item in enumerate(st.session_state["items"], start=1):
        st.write(f"**Item {idx}: Barcode:** {item['item_id']}")
        # Create two columns: one for description and one for quantity.
        col_desc, col_qty = st.columns(2)
        with col_desc:
            desc = st.text_input(
                label=f"Description for Item {idx}",
                value=item.get("description", ""),
                key=f"desc_{idx}"
            )
        with col_qty:
            qty = st.number_input(
                label=f"Quantity for Item {idx}",
                min_value=1,
                value=item.get("quantity", 1),
                key=f"qty_{idx}"
            )
        # Update the session state for the current item.
        st.session_state["items"][idx-1]["description"] = desc
        st.session_state["items"][idx-1]["quantity"] = qty

# ---------- Image Capture Section ----------
st.header("Capture Image Using Camera")
if st.button("Start Capture Image"):
    img_file = st.camera_input("Click a picture")
    if img_file is not None:
        st.image(img_file, caption="Captured Image", use_container_width=True)
        # Store the binary image data in session state.
        st.session_state["captured_image"] = img_file.getvalue()

# ---------- Save Data ----------
if st.button("Save Packing Slip"):
    # If a captured image exists, assign it to any item that doesn't have one.
    if st.session_state["captured_image"]:
        for item in st.session_state["items"]:
            if item["image"] is None:
                item["image"] = st.session_state["captured_image"]
    header_info = {
        "header_id": header_val,
        "customer_name": customer_name,
        "location": location,
        "time_of_packing": time_of_packing
    }
    item_list = st.session_state["items"]
    save_packing_slip(header_info, item_list)
    st.success("Packing slip saved successfully!")

# ---------- Download Data ----------
def export_data():
    conn = create_connection()
    df_slips = pd.read_sql_query("SELECT * FROM packing_slip", conn)
    df_items = pd.read_sql_query("SELECT * FROM packing_items", conn)
    conn.close()
    return df_slips, df_items

st.header("Download Database Data")
if st.button("Download Data"):
    df_slips, df_items = export_data()
    # Create an in-memory ZIP file containing two CSV files.
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("packing_slip.csv", df_slips.to_csv(index=False))
            zip_file.writestr("packing_items.csv", df_items.to_csv(index=False))
        buffer.seek(0)
        st.download_button("Download Database CSV", data=buffer, file_name="database_data.zip", mime="application/zip")
