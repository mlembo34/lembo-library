import streamlit as st
import gspread

from google.oauth2.service_account import Credentials

SCOPES = [
  "https://www.googleapis.com/auth/spreadsheets",
  "https://www.googleapis.com/auth/drive"
]

def connect():
  credentials = Credentials.from_service_account_info(
    dict(st.secrets),
    scopes = SCOPES
  )

  gc = gspread.authorize(credentials)

  return gc.open("My Library").sheet1


def isbn_exists(sheet, isbn):
  values = sheet.col_values(1)

  return isbn in values


def add_book(sheet, book):
  sheet.append_row([
    book["isbn"],
    book["title"],
    book["author"],
    book["genre"],
    book["publisher"],
    book["published_date"],
    book["summary"]
  ])