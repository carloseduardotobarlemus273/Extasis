import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA Y CONEXIÓN ---
st.set_page_config(page_title="Control Extasis", layout="wide")

@st.cache_data(ttl=60)
def conectar_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

# --- CARGA DE DATOS ---
cliente = conectar_sheet()
sheet_doc = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qQQtqJu5Qjisa-kN3Q3_zkuEb1wl010-Y5y9kyQOAiI/edit")
ws_inventario = sheet_doc.worksheet("Inventario")
ws_ventas = sheet_doc.worksheet("Ventas")

# Crear mapa de productos para el selectbox
df_inv = pd.DataFrame(ws_inventario.get_all_records())
mapa_productos = {}
for i, row in df_inv.iterrows():
    mapa_productos[row['Perfume']] = {
        'stock': int(row['Cantidad']),
        'precio_venta': float(row['Precio_Venta']),
        'fila': i + 2
    }

# --- AHORA SÍ, TU FORMULARIO ---
with st.form("form_venta_inteligente", clear_on_submit=True):
    # ... aquí va el resto de tu código del formulario ...
