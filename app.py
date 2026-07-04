import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Control Extasis", layout="wide")

@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(
        creds_dict, 
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
    return gspread.authorize(creds)

# --- CONEXIÓN Y DATOS ---
try:
    cliente = get_gspread_client()
    sheet_doc = cliente.open_by_url("https://docs.google.com/spreadsheets/d/1qQQtqJu5Qjisa-kN3Q3_zkuEb1wl010-Y5y9kyQOAiI/edit")
    ws_inventario = sheet_doc.worksheet("Inventario")
    ws_ventas = sheet_doc.worksheet("Ventas")

    df_inv = pd.DataFrame(ws_inventario.get_all_records())
    mapa_productos = {}
    for i, row in df_inv.iterrows():
        mapa_productos[row['Perfume']] = {
            'stock': int(row['Cantidad']),
            'precio_venta': float(row['Precio_Venta']),
            'fila': i + 2
        }
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# --- INTERFAZ ---
st.title("📦 Extasis - Gestión de Negocio")
tab1, tab2, tab3 = st.tabs(["📊 Inventario", "💰 Nueva Venta", "📈 Reporte"])

with tab1:
    st.dataframe(df_inv, use_container_width=True)

with tab2:
    st.subheader("Registrar Venta")
    with st.form("form_venta_inteligente", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre_cliente = st.text_input("Cliente")
            perfume_seleccionado = st.selectbox("Perfume", options=list(mapa_productos.keys()))
            cantidad = st.number_input("Cantidad a vender", min_value=1, step=1)
            tipo_pago = st.radio("Tipo de Pago", ["Al contado", "Crédito"])
        
        datos_perfume = mapa_productos[perfume_seleccionado]
        total_calculado = cantidad * datos_perfume['precio_venta']
        st.write(f"### Total a pagar: ${total_calculado:.2f}")

        # Lógica de campos para Crédito
        if tipo_pago == "Crédito":
            with col2:
                st.write("#### Detalles del Crédito")
                abono1 = st.number_input("Abono 1", min_value=0.0)
                fecha_abono1 = st.date_input("Fecha Abono 1")
                abono2 = st.number_input("Abono 2", min_value=0.0)
                fecha_abono2 = st.date_input("Fecha Abono 2")
                pago_total = st.number_input("Pago Total", value=float(total_calculado))
                pendiente = st.number_input("Pendiente", value=float(total_calculado - (abono1 + abono2)))
                estado = st.selectbox("Estado", ["Pendiente", "Pagado"])
        else:
            abono1, fecha_abono1, abono2, fecha_abono2 = 0.0, datetime.today(), 0.0, datetime.today()
            pago_total = total_calculado
            pendiente = 0.0
            estado = "Pagado"

        confirmar = st.form_submit_button("Confirmar Venta")

    if confirmar:
        if mapa_productos[perfume_seleccionado]['stock'] >= cantidad:
            ws_inventario.update_cell(datos_perfume['fila'], 1, mapa_productos[perfume_seleccionado]['stock'] - cantidad)
            ws_ventas.append_row([
                nombre_cliente, cantidad, perfume_seleccionado, tipo_pago, 
                abono1, str(fecha_abono1), abono2, str(fecha_abono2), 
                pago_total, pendiente, estado
            ])
            st.success(f"Venta de {perfume_seleccionado} registrada correctamente.")
            st.rerun()
        else:
            st.error("Stock insuficiente.")

with tab3:
    st.dataframe(pd.DataFrame(ws_ventas.get_all_records()))
