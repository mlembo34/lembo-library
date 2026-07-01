import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets,
    scopes=SCOPES
)

gc = gspread.authorize(credentials)

sheet = gc.open("My Library").sheet1

sheet.append_row(["TEST", "Connection works", "", "", "", "", "", ""])

print("Success! Row added.")