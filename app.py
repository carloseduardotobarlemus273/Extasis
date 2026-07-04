import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Control Extasis", layout="wide")

# --- CONEXIÓN ---
@st.cache_data(ttl=60)
def conectar_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

cliente = conectar_sheet()
sheet_doc = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qQQtqJu5Qjisa-kN3Q3_zkuEb1wl010-Y5y9kyQOAiI/edit")
ws_inventario = sheet_doc.worksheet("Inventario")
ws_ventas = sheet_doc.worksheet("Ventas")

# --- LÓGICA ---
st.title("📦 Extasis - Gestión de Negocio")

tab1, tab2, tab3 = st.tabs(["📊 Inventario", "💰 Nueva Venta", "📈 Reporte"])

# 1. PESTAÑA INVENTARIO
with tab1:
    st.subheader("Estado del Inventario")
    df_inv = pd.DataFrame(ws_inventario.get_all_records())
    st.dataframe(df_inv, use_container_width=True)

# 2. PESTAÑA VENTA (Adaptada a tus columnas)
with tab2:
    st.subheader("Registrar Venta")
    # Usamos 'Perfume' en lugar de 'Nombre' como dice tu hoja
    productos = df_inv['Perfume'].tolist()
    
    with st.form("form_venta"):
        prod_sel = st.selectbox("Seleccionar Perfume", productos)
        cant_sel = st.number_input("Cantidad a vender", min_value=1, step=1)
        btn_vender = st.form_submit_button("Confirmar Venta")
        
        if btn_vender:
            # Buscar fila basándonos en la columna 'Perfume'
            idx = df_inv[df_inv['Perfume'] == prod_sel].index[0]
            fila = idx + 2 # +2 porque gspread es 1-index y tiene cabeceras
            
            stock_actual = int(df_inv.loc[idx, 'Cantidad'])
            
            if stock_actual >= cant_sel:
                nuevo_stock = stock_actual - cant_sel
                # Actualizar cantidad en la columna 'Cantidad' (columna 1)
                ws_inventario.update_cell(fila, 1, nuevo_stock)
                
                # Registrar en hoja ventas (ajustado a tus columnas)
                ws_ventas.append_row([
                    "Venta Rápida", # Cliente
                    cant_sel, 
                    prod_sel, 
                    "Efectivo", # Tipo_Pago por defecto
                    0, "", 0, "", 0, 0, "Completado"
                ])
                st.success(f"Venta registrada: {cant_sel} x {prod_sel}")
                st.rerun()
            else:
                st.error("¡Stock insuficiente!")

# 3. PESTAÑA REPORTE
with tab3:
    st.subheader("Historial de Ventas")
    df_ventas = pd.DataFrame(ws_ventas.get_all_records())
    if not df_ventas.empty:
        st.dataframe(df_ventas, use_container_width=True)
    else:
        st.info("Aún no hay ventas registradas.")
