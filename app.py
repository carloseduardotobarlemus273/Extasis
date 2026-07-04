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
ws_inventario = sheet.worksheet("Inventario")
ws_ventas = sheet.worksheet("Ventas")

# --- Obtener productos del Inventario ---
datos_inventario = ws_inventario.get_all_records()
# Creamos un diccionario donde la llave es el nombre y guardamos toda la info necesaria
mapa_productos = {
    fila['Perfume']: {
        'fila': i + 2, 
        'stock': fila['Cantidad'], 
        'precio_venta': fila['Precio_Venta']
    } 
    for i, fila in enumerate(datos_inventario)
}

st.subheader("Registrar Nueva Venta")

with st.form("form_venta_inteligente", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_cliente = st.text_input("Cliente")
        # El selectbox permite elegir el perfume
        perfume_seleccionado = st.selectbox("Perfume", options=list(mapa_productos.keys()))
        
        # Recuperamos el precio del perfume seleccionado
        precio_unitario = mapa_productos[perfume_seleccionado]['precio_venta']
        
        cantidad = st.number_input("Cantidad a vender", min_value=1, step=1)
        
        # Calculamos el total esperado automáticamente
        total_calculado = cantidad * precio_unitario
        st.write(f"**Precio unitario:** ${precio_unitario}")
        
        tipo_pago = st.selectbox("Tipo_Pago", ["Efectivo", "Crédito"])

    with col2:
        abono1 = st.number_input("Abono_1", min_value=0.0)
        fecha_abono1 = st.date_input("Fecha_Abono_1", value=datetime.now())
        abono2 = st.number_input("Abono_2", min_value=0.0)
        fecha_abono2 = st.date_input("Fecha_Abno_2", value=datetime.now())
        
        # Mostramos el total calculado
        pago_total = st.number_input("Pago_Total", value=float(total_calculado))
        pendiente = st.number_input("Pendiente", value=float(total_calculado - (abono1 + abono2)))
        estado = st.selectbox("Estado", ["Pagado", "Pendiente"])

    submit_btn = st.form_submit_button("Confirmar Venta")

    if submit_btn:
        stock_actual = mapa_productos[perfume_seleccionado]['stock']
        fila_inv = mapa_productos[perfume_seleccionado]['fila']
        
        if stock_actual >= cantidad:
            # 1. Descontar en Inventario
            ws_inventario.update_cell(fila_inv, 1, stock_actual - cantidad)
            
            # 2. Registrar en Ventas
            fila_ventas = [
                nombre_cliente, cantidad, perfume_seleccionado, tipo_pago, abono1, 
                str(fecha_abono1), abono2, str(fecha_abono2), pago_total, pendiente, estado
            ]
            ws_ventas.append_row(fila_ventas)
            
            st.success(f"Venta registrada: {cantidad} x {perfume_seleccionado}. Inventario actualizado.")
            st.rerun()
        else:
            st.error(f"Error: Solo quedan {stock_actual} unidades.")
