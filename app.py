import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

st.title("Control de Perfumes")

# Configuración para conectar con tu Sheet
# (Luego configuraremos esto para que sea seguro)
def conectar_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

cliente = conectar_sheet()
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qQQtqJu5Qjisa-kN3Q3_zkuEb1wl010-Y5y9kyQOAiI/edit")

# Mostrar inventario
st.subheader("Inventario")
datos = sheet.worksheet("Inventario").get_all_records()
st.dataframe(pd.DataFrame(datos))
