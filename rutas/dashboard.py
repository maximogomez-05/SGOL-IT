from flask import Blueprint, render_template, session, redirect, url_for
from config.database import DB

bp_dashboard = Blueprint('dashboard', __name__)

@bp_dashboard.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session: 
        return redirect(url_for('auth.inicio'))
    
    listos_count = 0
    alertas_stock = []
    stats = {}
    
    cursor = DB.cursor(dictionary=True)
    
    if int(session.get('rol_id', 0) or 0) == 1:
        try:
            cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN Stock_Minimo INT DEFAULT 0")
        except:
            pass
        cursor.execute("CALL sp_obtener_alertas_stock()")
        alertas_stock = cursor.fetchall()
        
        # MySQL Connector puede requerir avanzar el resultset después de un CALL
        while cursor.nextset():
            pass
        
        # 1. total ingresos
        cursor.execute("SELECT SUM(Monto_Total) as total FROM factura")
        total_res = cursor.fetchone()
        stats['total_ingresos'] = float(total_res['total'] or 0.0) if total_res else 0.0

        # 2. total ots finalizadas
        cursor.execute("SELECT COUNT(*) as total FROM orden_trabajo WHERE Estado_General = 'Finalizado'")
        finalizados_res = cursor.fetchone()
        stats['total_finalizados'] = finalizados_res['total'] if finalizados_res else 0

        # 3. facturacion por mes
        cursor.execute("""
            SELECT DATE_FORMAT(Fecha_Emision, '%Y-%m') as mes, SUM(Monto_Total) as total 
            FROM factura 
            GROUP BY mes 
            ORDER BY mes ASC
        """)
        stats['mensual_labels'] = []
        stats['mensual_valores'] = []
        for row in cursor.fetchall():
            stats['mensual_labels'].append(row['mes'])
            stats['mensual_valores'].append(float(row['total']))

        # 4. metodos de pago
        cursor.execute("""
            SELECT Metodo_Pago as metodo, SUM(Monto_Total) as total 
            FROM factura 
            GROUP BY Metodo_Pago
        """)
        stats['metodo_labels'] = []
        stats['metodo_valores'] = []
        for row in cursor.fetchall():
            stats['metodo_labels'].append(row['metodo'])
            stats['metodo_valores'].append(float(row['total']))

        # 5. repuestos vs mano de obra
        cursor.execute("""
            SELECT ci.Tipo_Item as tipo, SUM(do.Cantidad * do.Precio_Unitario_Congelado) as total
            FROM detalle_orden do
            JOIN catalogo_inventario ci ON do.Catalogo_Inventario_ID_Item = ci.ID_Item
            JOIN orden_trabajo ot ON do.Orden_Trabajo_ID_OT = ot.ID_OT
            WHERE ot.Estado_General = 'Finalizado'
            GROUP BY ci.Tipo_Item
        """)
        stats['tipo_labels'] = []
        stats['tipo_valores'] = []
        for row in cursor.fetchall():
            tipo_bonito = "Repuestos" if row['tipo'] == 'Repuesto_Fisico' else "Mano de Obra"
            stats['tipo_labels'].append(tipo_bonito)
            stats['tipo_valores'].append(float(row['total']))

        # 6. desempeño de tecnicos (solo rol 3 = técnico)
        cursor.execute("""
            SELECT e.Nombre_Completo as tecnico, COUNT(ot.ID_OT) as cantidad
            FROM orden_trabajo ot
            JOIN empleado e ON ot.Empleado_ID_Empleado = e.ID_Empleado
            JOIN legajo_empleado le ON e.ID_Empleado = le.Empleado_ID_Empleado
            WHERE ot.Estado_General = 'Finalizado' AND le.Roles_ID_Rol = 3
            GROUP BY e.Nombre_Completo
            ORDER BY cantidad DESC
        """)
        stats['tecnico_labels'] = []
        stats['tecnico_valores'] = []
        for row in cursor.fetchall():
            stats['tecnico_labels'].append(row['tecnico'])
            stats['tecnico_valores'].append(int(row['cantidad']))
            
        # 7. distribucion de dispositivos
        cursor.execute("""
            SELECT Tipo_Dispositivo as tipo, COUNT(*) as cantidad
            FROM equipo
            GROUP BY Tipo_Dispositivo
        """)
        stats['dispositivos_labels'] = []
        stats['dispositivos_valores'] = []
        for row in cursor.fetchall():
            stats['dispositivos_labels'].append(row['tipo'])
            stats['dispositivos_valores'].append(int(row['cantidad']))

        # 8. estado de la cola de trabajo
        cursor.execute("""
            SELECT Estado_General as estado, COUNT(*) as cantidad
            FROM orden_trabajo
            GROUP BY Estado_General
        """)
        stats['estados_labels'] = []
        stats['estados_valores'] = []
        for row in cursor.fetchall():
            stats['estados_labels'].append(row['estado'])
            stats['estados_valores'].append(int(row['cantidad']))
        
    if int(session.get('rol_id', 0) or 0) in (1, 2):
        cursor.execute("SELECT COUNT(*) as cant FROM orden_trabajo WHERE Estado_General = 'Listo para Entregar'")
        res = cursor.fetchone()
        listos_count = res['cant'] if res else 0

    # 9. Obtener últimas órdenes activas (laboratorio en progreso)
    cursor.execute("CALL sp_obtener_ordenes_recientes()")
    ordenes_recientes = cursor.fetchall()
    
    while cursor.nextset():
        pass

    # 10. Obtener últimos turnos pendientes solicitados
    turnos_recientes = []
    if int(session.get('rol_id', 0) or 0) in (1, 2):
        cursor.execute("""
            SELECT t.ID_Turno, t.Servicio, t.Presupuesto_Estimado, 
                   DATE_FORMAT(t.Fecha_Solicitud, '%d/%m/%Y %H:%i') as fecha, t.Estado, t.Garantia,
                   c.Nombre_Completo as Cliente, c.Telefono 
            FROM turno t 
            JOIN cliente c ON t.Cliente_ID_Cliente = c.ID_Cliente
            WHERE t.Estado = 'Pendiente'
            ORDER BY t.Fecha_Solicitud DESC
            LIMIT 5
        """)
        turnos_recientes = cursor.fetchall()
        
    cursor.close()
        
    return render_template(
        'dashboard.html', 
        listos_entrega=listos_count, 
        alertas_stock=alertas_stock, 
        stats=stats,
        ordenes_recientes=ordenes_recientes,
        turnos_recientes=turnos_recientes
    )
