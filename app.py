import os
import base64
import streamlit as st
import google.generativeai as genai
import io
import PyPDF2 as pdf
import pdf2image
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini response
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Function to prepare PDF as an image (for visual inspection)
def input_pdf_image(uploaded_file):
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    first_page = images[0]
    
    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    first_page.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    # Encode image as base64
    pdf_parts = [
        {
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()  # Encode to base64
        }
    ]
    return pdf_parts

# Function to extract text from PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += page.extract_text() or ""
    return text

# Streamlit app setup
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Resume Analysis System")

# Text area for job description input
input_text = st.text_area("Job Description:", help="Paste the job description here.")

# File uploader for PDF resume
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"], help="Please upload a PDF resume.")

# Buttons for actions
submit1 = st.button("General Resume Evaluation")
submit2 = st.button("ATS Percentage Match")

# Prompts for Gemini
input_prompt_general = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt_ats = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. Provide the percentage match if the resume aligns with the job description. 
The output should include the percentage match, missing keywords, and final thoughts.
"""

# Action for the general resume evaluation
if submit1:
    if uploaded_file is not None and input_text.strip() != "":
        with st.spinner("Analyzing resume..."):
            try:
                # Extract PDF as image for Gemini input
                pdf_content = input_pdf_image(uploaded_file)
                
                # Get response from Gemini
                response = get_gemini_response(input_text, pdf_content, input_prompt_general)
                
                # Display the response
                st.subheader("HR Evaluation Response:")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please upload a resume and enter the job description.")

# Action for the ATS percentage match
elif submit2:
    if uploaded_file is not None and input_text.strip() != "":
        with st.spinner("Calculating ATS percentage match..."):
            try:
                # Extract text from PDF for content-based analysis
                pdf_text = input_pdf_text(uploaded_file)
                
                # Convert text into a format acceptable by Gemini
                pdf_content = [{"mime_type": "text/plain", "data": pdf_text}]
                
                # Get response from Gemini
                response = get_gemini_response(input_text, pdf_content, input_prompt_ats)
                
                # Display the response
                st.subheader("ATS Evaluation Response:")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.error("Please upload a resume and enter the job description.")
