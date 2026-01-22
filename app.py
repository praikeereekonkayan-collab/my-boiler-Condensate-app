
import streamlit as st
import pandas as pd
import os
import io

st.set_page_config(page_title="Checklist App", layout="wide", page_icon="✅")

# Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Prompt', sans-serif; /* Example font */
    }

    /* Main Title */
    h1 {
        color: #2c3e50;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        padding-bottom: 20px;
    }

    /* Form Container */
    [data-testid="stForm"] {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: none;
    }

    /* Column Headers */
    .header-text {
        color: #5D3FD3; /* Vibrant Purple */
        font-weight: 700;
        font-size: 1.1em;
    }

    /* Inputs */
    .stTextInput input {
        border-radius: 10px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .stTextInput input:focus {
        border-color: #00C9FF;
        box-shadow: 0 0 5px rgba(0,201,255,0.5);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Card-like rows for items */
    .item-row {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #00C9FF;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ ระบบตรวจเช็ค (Checking System)")

# Load data
file_path = 'checklist_data.xlsx'
if not os.path.exists(file_path):
    st.error(f"File not found: {file_path}")
else:
    try:
        df = pd.read_excel(file_path, sheet_name='Sheet1')
        
        # Clean column names if necessary (remove leading/trailing spaces)
        df.columns = df.columns.str.strip()
        
        # Display the dataframe for reference (optional)
        # st.write("Raw Data:", df.head())

        # Inspector Name Input
        col_input1, col_input2 = st.columns(2)
        with col_input1:
            inspector_name = st.text_input("ชื่อผู้ตรวจ (Inspector Name)", key="inspector_name")
        with col_input2:
            machine_name = st.text_input("เครื่องที่ตรวจ (Machine Name)", key="machine_name")

        # Create a form for checking
        with st.form("checklist_form"):
            st.write("### รายการตรวจเช็ค (Checklist Items)")
            
            # Iterate through rows
            # Assuming column names based on previous analysis: 'จุดตรวจ (Inspection Point)', 'ค่ามาตรฐาน (Standard)', 'สถานะ (OK / NG)'
            # We'll try to identify columns dynamically if possible, or use index
            
            cols = st.columns([3, 2, 2, 2])
            cols[0].markdown("<div class='header-text'>Inspection Point</div>", unsafe_allow_html=True)
            cols[1].markdown("<div class='header-text'>Standard</div>", unsafe_allow_html=True)
            cols[2].markdown("<div class='header-text'>Status</div>", unsafe_allow_html=True)
            cols[3].markdown("<div class='header-text'>Note</div>", unsafe_allow_html=True)
            
            st.markdown("---") # Separator

            results = []
            
            for index, row in df.iterrows():
                # Styling for better row separation - although we can't wrap columns in div directly in pure streamlit easily without components, 
                # we can use markdown for visual separation
                
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                # Use iloc to access columns by position to be safe against Thai encoding issues in column names
                inspection_point = row.iloc[0] if len(row) > 0 else ""
                standard = row.iloc[1] if len(row) > 1 else ""
                
                with col1:
                    st.markdown(f"**{inspection_point}**")
                
                with col2:
                    st.markdown(f"<span style='color:#666;'>{standard}</span>", unsafe_allow_html=True)
                
                with col3:
                    # Key needs to be unique for each widget
                    status = st.radio(
                        "Status",
                        options=["OK", "NG"],
                        key=f"status_{index}",
                        horizontal=True,
                        label_visibility="collapsed"
                    )
                
                with col4:
                     note = st.text_input("Note", key=f"note_{index}", label_visibility="collapsed")

                results.append({
                    "Inspector Name": inspector_name,
                    "Machine Name": machine_name,
                    "Inspection Point": inspection_point,
                    "Standard": standard,
                    "Status": status,
                    "Note": note
                })

            submitted = st.form_submit_button("Save Results")
            
            if submitted:
                results_df = pd.DataFrame(results)
                st.success("บันทึกข้อมูลเรียบร้อย (Data Saved Successfully)")
                st.dataframe(results_df)
                
                # Option to download results
                # CSV
                # csv = results_df.to_csv(index=False).encode('utf-8-sig')
                
                # Excel
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    results_df.to_excel(writer, index=False, sheet_name='Results')
                
                st.download_button(
                    label="Download Excel",
                    data=buffer.getvalue(),
                    file_name='checklist_results.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")
