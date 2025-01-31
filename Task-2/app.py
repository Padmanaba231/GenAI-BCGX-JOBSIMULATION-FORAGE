import os
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

# Konfigurasi API Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# Fungsi untuk membaca dan mengubah data CSV ke format JSON
def read_financial_data(csv_path):
    df = pd.read_csv(csv_path)
    return df.to_json(orient="records", lines=True)

# Membaca data CSV dan mengubahnya menjadi JSON
financial_data_json = read_financial_data('./Task-2/Final_Data.csv')


# Buat konfigurasi model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 10000,
    "response_mime_type": "text/plain",
}

# Inisialisasi model Gemini
model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
)

# Prompt engineering: Chatbot asisten untuk orang tuli dan BISINDO
prompt = f"""
You are an assistant designed to help people understand financial data.
Here is data about a company's financials in JSON format:
{financial_data_json}

Your task is to assist the user in understanding the company's financial status.
If a user asks about the company's revenue, net income, assets, or liabilities, provide the relevant information from the data.
This data is about 3 companies, Tesla, Apple, and Microsoft from 2021 to 2023. Ensure that you provide the correct information based on the user's query.
"""
# Mulai sesi chat dengan prompt
chat_session = model.start_chat(
    history=[{"role": "model", "parts": prompt}]
)

# Menyimpan riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Fungsi untuk menampilkan pesan pada UI chatbot
def direct_chat(text, role):
    with st.chat_message(role):
        st.write(text)

# Fungsi untuk chatbot
def chatbot():
    st.header("Finance Chatbot")
    st.write("Welcome to the Finance Chatbot! Ask me anything about financial data and I'll help you understand it. 😊")
    st.write("You can ask me about finance data of Tesla, Apple, Microsoft from 2021 to 2023!")
    
    # Jika belum ada percakapan, bot memulai percakapan
    if len(st.session_state.chat_history) == 0:
        initial_message = "Hi! I'm here to help you understand financial data. What would you like to learn today? 😊"
        st.session_state.chat_history.append({"role": "assistant", "text": initial_message})
    
    # Tampilkan semua chat sebelumnya, kecuali prompt
    for message in st.session_state.chat_history:
        if message["role"] != "model":  # Pastikan prompt tidak ditampilkan
            direct_chat(message["text"], role=message["role"])

    # Input teks dari pengguna
    user_input = st.chat_input("Type something about finance...")

    if user_input:
        # Simpan pesan pengguna ke riwayat chat
        st.session_state.chat_history.append({"role": "user", "text": user_input})

        # Kirim pesan ke model dan dapatkan respons
        response = chat_session.send_message(user_input)

        # Simpan respons dari Gemini ke riwayat chat
        st.session_state.chat_history.append({"role": "assistant", "text": response.text})
        
        # Tampilkan pesan baru
        direct_chat(user_input, role="user")
        direct_chat(response.text, role="assistant")
# Langsung panggil chatbot tanpa pilihan menu
chatbot()
