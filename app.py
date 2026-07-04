# --- FORMULARIO DE VENTA ---
with st.form("form_venta_inteligente", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_cliente = st.text_input("Cliente")
        perfume_seleccionado = st.selectbox("Perfume", options=list(mapa_productos.keys()))
        cantidad = st.number_input("Cantidad a vender", min_value=1, step=1)
        
        datos_perfume = mapa_productos[perfume_seleccionado]
        precio_unitario = datos_perfume['precio_venta']
        total_calculado = cantidad * precio_unitario
        
        st.write(f"**Precio unitario:** ${precio_unitario}")
        st.write(f"**Total a pagar:** ${total_calculado}")
        tipo_pago = st.radio("Tipo de Pago", ["Al contado", "Crédito"])

    if tipo_pago == "Al contado":
        pago_total = total_calculado
        abono1, fecha_abono1 = 0.0, ""
        abono2, fecha_abono2 = 0.0, ""
        pendiente = 0
        estado = "Pagado"
    else:
        with col2:
            abono1 = st.number_input("Abono_1", min_value=0.0)
            fecha_abono1 = st.date_input("Fecha_Abono_1")
            abono2 = st.number_input("Abono_2", min_value=0.0)
            fecha_abono2 = st.date_input("Fecha_Abno_2")
            pago_total = st.number_input("Pago_Total", value=float(total_calculado))
            pendiente = st.number_input("Pendiente", value=float(total_calculado - (abono1 + abono2)))
            estado = st.selectbox("Estado", ["Pendiente", "Pagado"])

    submit_btn = st.form_submit_button("Confirmar Venta")

    if submit_btn:
        stock_actual = datos_perfume['stock']
        fila_inv = datos_perfume['fila']
        
        if stock_actual >= cantidad:
            ws_inventario.update_cell(fila_inv, 1, stock_actual - cantidad)
            ws_ventas.append_row([
                nombre_cliente, cantidad, perfume_seleccionado, tipo_pago, 
                abono1, str(fecha_abono1), abono2, str(fecha_abono2), 
                pago_total, pendiente, estado
            ])
            st.success(f"Venta registrada: {cantidad} x {perfume_seleccionado}")
            st.rerun()
        else:
            st.error(f"Error: Solo quedan {stock_actual} unidades.")
