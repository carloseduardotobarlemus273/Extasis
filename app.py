import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.title("Control de Perfumes - Extasis")

# Configuración de conexión
def conectar_sheet():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(creds)

cliente = conectar_sheet()
sheet = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qQQtqJu5Qjisa-kN3Q3_zkuEb1wl010-Y5y9kyQOAiI/edit")
ws_inventario = sheet.worksheet("Inventario")
ws_ventas = sheet.worksheet("Ventas")

# --- APARTADO 1: INVENTARIO ---
st.subheader("Inventario Actual")
datos = ws_inventario.get_all_records()
df_inventario = pd.DataFrame(datos)
st.dataframe(df_inventario)

# --- APARTADO 2: AGREGAR PRODUCTO ---
with st.expander("➕ Agregar nuevo producto al inventario"):
    with st.form("form_inventario"):
        nombre = st.text_input("Nombre del Perfume")
        cantidad = st.number_input("Cantidad inicial", min_value=1, step=1)
        costo = st.number_input("Precio Costo", min_value=0.0)
        precio = st.number_input("Precio Venta", min_value=0.0)
        submit_inv = st.form_submit_button("Guardar Producto")
        
        if submit_inv:
            ws_inventario.append_row([cantidad, nombre, costo, precio])
            st.success("Producto agregado correctamente")
            st.rerun()

# --- APARTADO 3: REGISTRAR VENTA ---
with st.expander("💰 Registrar Venta"):
    nombres_disponibles = df_inventario['Perfume'].tolist()
    with st.form("form_venta"):
        producto_vendido = st.selectbox("Selecciona Perfume", nombres_disponibles)
        cantidad_vendida = st.number_input("Cantidad a vender", min_value=1, step=1)
        submit_venta = st.form_submit_button("Confirmar Venta")
        
        if submit_venta:
            # Buscar fila del producto
            celda = ws_inventario.find(producto_vendido)
            fila = celda.row
            cantidad_actual = int(ws_inventario.cell(fila, 1).value)
            
            if cantidad_actual >= cantidad_vendida:
                # Actualizar Inventario
                ws_inventario.update_cell(fila, 1, cantidad_actual - cantidad_vendida)
                # Registrar en Ventas
                ws_ventas.append_row([str(datetime.now()), producto_vendido, cantidad_vendida])
                st.success(f"Venta registrada: {producto_vendido}")
                st.rerun()
            else:
                st.error("¡Stock insuficiente!")
