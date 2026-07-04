import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# --- Configuración ---
def conectar_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

cliente = conectar_sheet()
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qQQtqJu5Qjisa-kN3Q3_zkuEb1wl010-Y5y9kyQOAiI/edit")
ws_ventas = sheet.worksheet("Ventas")
ws_inventario = sheet.worksheet("Inventario")

st.subheader("Registrar Nueva Venta")

# --- Formulario de Venta ---
with st.form("form_venta_completo", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_cliente = st.text_input("Cliente")
        perfume = st.text_input("Perfume") # O un selectbox si prefieres listar inventario
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        tipo_pago = st.selectbox("Tipo_Pago", ["Efectivo", "Crédito"])
        abono1 = st.number_input("Abono_1", min_value=0.0)
        fecha_abono1 = st.date_input("Fecha_Abono_1", value=datetime.now())

    with col2:
        abono2 = st.number_input("Abono_2", min_value=0.0)
        fecha_abono2 = st.date_input("Fecha_Abno_2", value=datetime.now())
        pago_total = st.number_input("Pago_Total", min_value=0.0)
        pendiente = st.number_input("Pendiente", min_value=0.0)
        estado = st.selectbox("Estado", ["Pagado", "Pendiente"])

    submit_btn = st.form_submit_button("Registrar en Sheet")

    if submit_btn:
        # Preparar lista de datos en el orden exacto de tus columnas:
        # Cliente, Cantidad, Perfume, Tipo_Pago, Abono_1, Fecha_Abono_1, Abono_2, Fecha_Abno_2, Pago_Total, Pendiente, Estado
        fila_datos = [
            nombre_cliente, 
            cantidad, 
            perfume, 
            tipo_pago, 
            abono1, 
            str(fecha_abono1), 
            abono2, 
            str(fecha_abono2), 
            pago_total, 
            pendiente, 
            estado
        ]
        
        try:
            ws_ventas.append_row(fila_datos)
            st.success("Venta registrada exitosamente en el Sheet.")
        except Exception as e:
            st.error(f"Error al guardar: {e}")
