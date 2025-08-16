# consultai_app.py

import streamlit as st
import ollama
import pandas as pd
from io import BytesIO
from gtts import gTTS
import tempfile
from fpdf import FPDF
import PyPDF2

# Initialize Ollama client
client = ollama.Client()

st.set_page_config(page_title="ConsultAI", layout="wide")
st.title("ConsultAI - Your AI Business Consultant")

# Sidebar options
task = st.sidebar.selectbox(
    "Select a task:",
    ["Chat", "Generate Marketing Plan", "Analyze PDF", "Analyze CSV", "Search & Report"]
)

def read_text(text, lang="en"):
    """Generate a playable audio for text"""
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        tts.save(f.name)
        audio_file = open(f.name, "rb").read()
    st.audio(audio_file, format="audio/mp3")

# ------------------ CHAT ------------------
if task == "Chat":
    st.subheader("Chat with ConsultAI")
    user_input = st.text_input("Enter your message:")
    if st.button("Send") and user_input:
        response = client.chat(
            model="mistral",
            messages=[{"role": "user", "content": user_input}]
        )
        st.write("ConsultAI:", response.content)
        read_text(response.content)

# ------------------ MARKETING PLAN ------------------
elif task == "Generate Marketing Plan":
    st.subheader("Generate Marketing Plan")
    business_name = st.text_input("Business Name:")
    industry = st.text_input("Industry:")
    goals = st.text_area("Business Goals:")

    if st.button("Generate Plan") and business_name and industry and goals:
        prompt = f"""
        Write a detailed marketing plan for a company named {business_name} 
        in the {industry} industry, focusing on these goals: {goals}.
        Include introduction, body, conclusion, charts if needed.
        """
        report = client.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        st.write(report.content)
        read_text(report.content)

        # Download PDF
        pdf_bytes = BytesIO()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in report.content.split("\n"):
            pdf.multi_cell(0, 5, line)
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)
        st.download_button("Download PDF", pdf_bytes, file_name="MarketingPlan.pdf")

# ------------------ PDF ANALYSIS ------------------
elif task == "Analyze PDF":
    st.subheader("Analyze PDF Content")
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    if uploaded_file:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        prompt = f"Analyze this text and summarize what the report is about, include key insights and conclusions:\n{text}"
        analysis = client.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        st.write(analysis.content)
        read_text(analysis.content)

# ------------------ CSV ANALYSIS ------------------
elif task == "Analyze CSV":
    st.subheader("Analyze CSV Content")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df)
        prompt = f"Analyze this dataset and write a detailed report about its contents, trends, and insights:\n{df.head(20).to_string()}"
        analysis = client.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        st.write(analysis.content)
        read_text(analysis.content)

# ------------------ SEARCH & REPORT ------------------
elif task == "Search & Report":
    st.subheader("Search the Internet and Generate Report with Citations")
    query = st.text_input("Enter topic to research:")
    if st.button("Generate Report") and query:
        prompt = f"""
        Search the web for the topic: {query}.
        Write a detailed report with an introduction, body, conclusion,
        and include citations from reliable sources.
        """
        report = client.chat(model="llama2", messages=[{"role": "user", "content": prompt}])
        st.write(report.content)
        read_text(report.content)

        # Download PDF
        pdf_bytes = BytesIO()
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        for line in report.content.split("\n"):
            pdf.multi_cell(0, 5, line)
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)
        st.download_button("Download PDF", pdf_bytes, file_name="WebReport.pdf")
