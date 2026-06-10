from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modelos.factura import Factura
from modelos.orden_trabajo import OrdenTrabajo
from modelos.detalle_orden import DetalleOrden
from modelos.seguimiento import Seguimiento

bp_facturacion = Blueprint('facturacion', __name__)

@bp_facturacion.route('/facturas')
def listar_facturas():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    facturas = Factura.listar_todas()
    return render_template('facturas.html', facturas=facturas)

@bp_facturacion.route('/factura/<int:id_factura>')
def ver_factura(id_factura):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    factura = Factura.buscar_por_id(id_factura)
    if not factura:
        flash("Factura no encontrada.", "warning")
        return redirect(url_for('facturacion.listar_facturas'))
    detalles = DetalleOrden.buscar_por_orden(factura['id_orden'])
    return render_template('ver_factura.html', factura=factura, detalles=detalles)

@bp_facturacion.route('/facturar/<int:id_orden>')
def facturar_orden(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    orden = OrdenTrabajo.buscar_por_id(id_orden)
    if not orden:
        flash("La orden no existe.", "danger")
        return redirect(url_for('ordenes.entregas_pendientes'))
    if orden.get('estado') != 'Listo para Entregar':
        flash("Solo se pueden facturar órdenes en estado 'Listo para Entregar'.", "danger")
        return redirect(url_for('ordenes.entregas_pendientes'))
    return render_template('facturar_orden.html', orden=orden)

@bp_facturacion.route('/procesar_pago_avanzado/<int:id_orden>', methods=['POST'])
def procesar_pago_avanzado(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    
    metodo = request.form.get('metodo_pago')
    tipo_factura = request.form.get('tipo_factura', 'B')
    documento = request.form.get('documento_cliente', '')
    
    # validar método de pago contra whitelist
    metodos_validos = ('Efectivo', 'Tarjeta de Débito', 'Tarjeta de Crédito', 'Transferencia')
    if not metodo or metodo not in metodos_validos:
        flash("Método de pago inválido.", "danger")
        return redirect(url_for('facturacion.facturar_orden', id_orden=id_orden))
    
    # validar tipo de factura
    tipos_validos = ('A', 'B', 'C', 'A-CBU', 'A-RET')
    if tipo_factura not in tipos_validos:
        flash("Tipo de factura inválido.", "danger")
        return redirect(url_for('facturacion.facturar_orden', id_orden=id_orden))
        
    # validar documento del cliente
    import re
    if tipo_factura.startswith('A'):
        if not documento or not re.match(r'^\d{11}$', documento):
            flash("Para Facturas tipo A, el CUIT es obligatorio y debe tener exactamente 11 números.", "danger")
            return redirect(url_for('facturacion.facturar_orden', id_orden=id_orden))
    else:
        if documento and not re.match(r'^\d+$', documento):
            flash("El número de documento solo puede contener números.", "danger")
            return redirect(url_for('facturacion.facturar_orden', id_orden=id_orden))
    
    
    orden = OrdenTrabajo.buscar_por_id(id_orden)
    if not orden:
        flash("La orden no existe.", "danger")
        return redirect(url_for('ordenes.entregas_pendientes'))
    
    # validar que la orden esté en estado correcto
    if orden.get('estado') != 'Listo para Entregar':
        flash("Solo se pueden facturar órdenes en estado 'Listo para Entregar'.", "danger")
        return redirect(url_for('ordenes.entregas_pendientes'))
    
    # verificar que no exista ya una factura para esta orden (previene duplicados)
    facturas_existentes = Factura.listar_todas()
    for f in facturas_existentes:
        if f.get('id_orden') == id_orden:
            flash("Esta orden ya fue facturada.", "warning")
            return redirect(url_for('facturacion.ver_factura', id_factura=f['id_factura']))
    
    monto = orden['costo'] if orden and orden['costo'] else 0.0
    
    # validar monto > 0
    if not monto or float(monto) <= 0:
        flash("Error: El monto a facturar debe ser mayor a $0. Verifique que la orden tenga un presupuesto aprobado.", "danger")
        return redirect(url_for('facturacion.facturar_orden', id_orden=id_orden))
    
    fact = Factura(id_orden, monto, metodo, tipo_factura, documento)
    id_factura = fact.registrar()
    
    if id_factura:
        orden_obj = OrdenTrabajo.obtener_por_id(id_orden)
        if orden_obj:
            orden_obj.actualizar_estado('Finalizado')
        DetalleOrden.consumir_componentes(id_orden)
        Seguimiento.registrar_hito(id_orden, "Finalizado", f"Factura Tipo {tipo_factura} generada. Pago vía {metodo}.")
        flash(f"Orden finalizada y Factura Tipo {tipo_factura} generada con éxito.", "success")
        return redirect(url_for('facturacion.ver_factura', id_factura=id_factura))
    else:
        flash("Hubo un error al generar la factura.", "danger")
        return redirect(url_for('facturacion.facturar_orden', id_orden=id_orden))
