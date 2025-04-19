import streamlit as st
import io
import zipfile
import pandas as pd
import datetime
from modules.Scanner import decode_barcode_from_bytes, RealTimeBarcodeScanner
from database.db_manager import create_tables, save_packing_slip, create_connection

st.set_page_config(page_title="Barcode Scanner", page_icon="🔍")

# ---------- Initialize ----------
create_tables()

# Session state variables
if "header" not in st.session_state:
    st.session_state["header"] = None
if "items" not in st.session_state:
    st.session_state["items"] = []
if "captured_image" not in st.session_state:
    st.session_state["captured_image"] = None

st.title("📦 Barcode Scanner App")

# ---------- Step 1: Scan Item Barcodes ----------
st.header("Step 1: Scan Item Barcodes")
n = st.number_input("Enter number of items to scan (excluding header):", min_value=1, step=1)

for i in range(n):
    if i >= len(st.session_state["items"]):
        st.session_state["items"].append(None)
    with st.expander(f"Scan Item {i + 1}"):
        image = st.camera_input(f"Take photo of Item {i + 1}")
        if image:
            barcode = decode_barcode_from_bytes(image.getvalue())
            if barcode:
                st.session_state["items"][i] = {
                    "item_id": barcode,
                    "description": "",
                    "quantity": 1,
                    "image": None
                }
                st.success(f"✅ Scanned Item {i + 1}: {barcode}")
            else:
                st.warning("No barcode detected. Try again.")

# ---------- Step 2: Header Barcode ----------
st.header("Step 2: Scan Header Barcode")
header_img = st.camera_input("Scan Header Barcode")

if header_img:
    header_code = decode_barcode_from_bytes(header_img.getvalue())
    if header_code:
        st.session_state["header"] = header_code
        st.success(f"✅ Scanned Header: {header_code}")
    else:
        st.warning("No barcode detected in header. Try again.")

# ---------- Final Results ----------
st.header("📋 Final Scanned Results")
if all(item is not None for item in st.session_state["items"]) and st.session_state["header"]:
    for idx, item in enumerate(st.session_state["items"], start=1):
        st.write(f"Item {idx}: {item['item_id']}")
    st.write(f"Header: {st.session_state['header']}")
else:
    st.info("Scan all items and the header to see final results.")

# ---------- Packing Slip Details ----------
st.header("Packing Slip Details")
customer_name = st.text_input("Customer Name")
location = st.text_input("Location")
# Automatically set the packing time to the current date and time.
time_of_packing = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"Time of Packing: {time_of_packing}")

# ---------- Add More Items via Real-time Scanner ----------
st.header("📦 Add More Items via Real-Time Scanner")
if st.button("Scan Item Barcode"):
    scanned_item = RealTimeBarcodeScanner()
    if scanned_item:
        st.session_state["items"].append({
            "item_id": scanned_item,
            "description": "",
            "quantity": 1,
            "image": None
        })
        st.success(f"Item scanned: {scanned_item}")
    else:
        st.error("Item scan failed!")

# ---------- Enter Details for Items ----------
if st.session_state["items"]:
    st.subheader("📝 Item Details")
    for idx, item in enumerate(st.session_state["items"], start=1):
        if item is None:
            st.warning(f"Item {idx} has not been scanned yet.")
            continue
        st.write(f"**Item {idx}: Barcode - {item['item_id']}**")
        col1, col2 = st.columns(2)
        with col1:
            desc = st.text_input(f"Description for Item {idx}", value=item.get("description", ""), key=f"desc_{idx}")
        with col2:
            qty = st.number_input(f"Quantity for Item {idx}", min_value=1, value=item.get("quantity", 1), key=f"qty_{idx}")
        st.session_state["items"][idx - 1]["description"] = desc
        st.session_state["items"][idx - 1]["quantity"] = qty

# ---------- Capture Image for Items ----------
st.header("📷 Capture Image for Items")
if st.button("Start Capture Image"):
    img_file = st.camera_input("Take a picture of an item")
    if img_file:
        st.image(img_file, caption="Captured Image", use_container_width=True)
        st.session_state["captured_image"] = img_file.getvalue()

# ---------- Save Packing Slip ----------
if st.button("Save Packing Slip"):
    if st.session_state["captured_image"]:
        for item in st.session_state["items"]:
            if item["image"] is None:
                item["image"] = st.session_state["captured_image"]
    header_info = {
        "header_id": st.session_state["header"],
        "customer_name": customer_name,
        "location": location,
        "time_of_packing": time_of_packing
    }
    item_list = st.session_state["items"]
    save_packing_slip(header_info, item_list)
    st.success("Packing slip saved successfully!")

# ---------- Export to CSV ----------
def export_data():
    conn = create_connection()
    df_slips = pd.read_sql_query("SELECT * FROM packing_slip", conn)
    df_items = pd.read_sql_query("SELECT * FROM packing_items", conn)
    conn.close()
    return df_slips, df_items

st.header("⬇️ Download Database")
if st.button("Download Data"):
    df_slips, df_items = export_data()
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("packing_slip.csv", df_slips.to_csv(index=False))
            zip_file.writestr("packing_items.csv", df_items.to_csv(index=False))
        buffer.seek(0)
        st.download_button("Download Database CSV", data=buffer, file_name="database_data.zip", mime="application/zip")
