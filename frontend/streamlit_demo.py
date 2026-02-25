import requests
import streamlit as st
from io import BytesIO
from pypdf import PdfReader

st.title("Document review system")

uploaded_file = st.file_uploader("Choose a PDF file with study plan", type="pdf")

if uploaded_file is not None:
    # Read PDF
    pdf_reader = PdfReader(BytesIO(uploaded_file.read()))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    st.text_area("Extracted Text", text, height=300)
    
    if st.button("Suggenst improvements"):
        # Send text to backend
        backend_url = "http://localhost:8000/generate-tokens"  # Change as needed
        try:
            response = requests.post(backend_url, json={"text": text})
            if response.status_code == 200:
                st.success("Text sent successfully!")
                st.markdown(response.json()["tokens"])
            else:
                st.error(f"Backend error: {response.status_code}")
        except Exception as e:
            st.error(f"Request failed: {e}")