from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime
from auth.login import Autenticacion  
from modelos.presupuesto import Presupuesto
from modelos.detalle_orden import DetalleOrden
from config.database import DB  
from modelos.orden_trabajo import OrdenTrabajo
from modelos.inventario import Inventario
from modelos.seguimiento import Seguimiento
from modelos.control_calidad import ControlCalidad
from modelos.cliente import Cliente
from modelos.equipo import Equipo
from modelos.empleado import Empleado
from modelos.factura import Factura

app = Flask(__name__)
app.secret_key = "sgol_it_key_2024_university_project"

@app.route('/')
def inicio():
    if 'usuario_id' in session: 
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user = request.form.get('usuario')
    pw = request.form.get('password')
    res = Autenticacion().iniciar_sesion(user, pw)
    if res:
        session.update({
            'usuario_id': res['id'], 
            'nombre': res['nombre'], 
            'rol_id': res['rol_id'], 
            'nombre_rol': res['nombre_rol']
        })
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Credenciales inválidas.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session: 
        return redirect(url_for('inicio'))
    
    listos_count = 0
    alertas_stock = []
    
    cursor = DB.cursor(dictionary=True)
    
    if session['rol_id'] == 1:
        try:
            cursor.execute("ALTER TABLE catalogo_inventario ADD COLUMN Stock_Minimo INT DEFAULT 0")
        except:
            pass
        cursor.execute("SELECT Descripcion, Stock_Disponible, Stock_Minimo FROM catalogo_inventario WHERE Tipo_Item = 'Repuesto_Fisico' AND Stock_Disponible <= Stock_Minimo")
        alertas_stock = cursor.fetchall()
        
    if session['rol_id'] == 2:
        cursor.execute("SELECT COUNT(*) as cant FROM orden_trabajo WHERE Estado_General = 'Listo para Entregar'")
        res = cursor.fetchone()
        listos_count = res['cant'] if res else 0
        
    cursor.close()
        
    return render_template('dashboard.html', listos_entrega=listos_count, alertas_stock=alertas_stock)

@app.route('/solicitar_turno', methods=['GET', 'POST'])
def solicitar_turno():
    if request.method == 'POST':
        dni = request.form.get('dni')
        nom = request.form.get('nombre')
        tel = request.form.get('telefono')
        em = request.form.get('email')
        serv = request.form.get('servicio')
        pres = float(request.form.get('presupuesto_estimado') or 0.0)
        try:
            cursor = DB.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS turno (
                    ID_Turno INT AUTO_INCREMENT PRIMARY KEY,
                    DNI_CUIL VARCHAR(15),
                    Nombre_Completo VARCHAR(100),
                    Email VARCHAR(100),
                    Telefono VARCHAR(20),
                    Servicio VARCHAR(100),
                    Presupuesto_Estimado DECIMAL(10,2),
                    Fecha_Solicitud DATETIME,
                    Estado VARCHAR(50) DEFAULT 'Pendiente'
                )
            """)
            cursor.execute(
                "INSERT INTO turno (DNI_CUIL, Nombre_Completo, Email, Telefono, Servicio, Presupuesto_Estimado, Fecha_Solicitud) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (dni, nom, em, tel, serv, pres, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            DB.commit()
            cursor.close()
            flash("Turno solicitado con éxito. Presentate en el local con tu DNI.", "success")
            return redirect(url_for('inicio'))
        except Exception as e: 
            flash(f"Error: {e}", "danger")
    return render_template('solicitar_turno.html')

@app.route('/gestion_personal', methods=['GET', 'POST'])
def gestion_personal():
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        n = request.form.get('nombre')
        u = request.form.get('usuario')
        p = request.form.get('password')
        r = request.form.get('rol_id')
        try:
            Empleado(n, u, p, r).registrar()
            flash("Empleado registrado exitosamente.", "success")
        except Exception as e: 
            flash(f"Error: {e}", "danger")
    
    empleados = Empleado.listar_todos()
    return render_template('gestion_personal.html', empleados=empleados)

@app.route('/eliminar_empleado/<int:id_emp>', methods=['POST'])
def eliminar_empleado(id_emp):
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('inicio'))
    if id_emp == session['usuario_id']:
        flash("No puedes eliminar tu propia cuenta.", "danger")
    else:
        if Empleado.eliminar(id_emp):
            flash("Empleado eliminado del sistema.", "success")
        else:
            flash("Error al eliminar el empleado.", "danger")
    return redirect(url_for('gestion_personal'))

@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('inicio'))
    if request.method == 'POST':
        t = request.form.get('tipo')
        d = request.form.get('descripcion')
        p = float(request.form.get('precio'))
        s = int(request.form.get('stock') or 0)
        sm = int(request.form.get('stock_minimo') or 0)
        Inventario(t, d, p, s, sm, "").registrar()
        flash("Ítem agregado al catálogo.", "success")
    return render_template('inventario.html', items=Inventario.listar_todo())

@app.route('/editar_item/<int:id_item>', methods=['POST'])
def editar_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('inicio'))
    d = request.form.get('descripcion')
    p = float(request.form.get('precio'))
    s = int(request.form.get('stock') or 0)
    sm = int(request.form.get('stock_minimo') or 0)
    if Inventario.actualizar(id_item, d, p, s, sm):
        flash("Ítem actualizado exitosamente.", "success")
    else:
        flash("Error al actualizar el ítem.", "danger")
    return redirect(url_for('inventario'))

@app.route('/eliminar_item/<int:id_item>', methods=['POST'])
def eliminar_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('inicio'))
    try:
        Inventario.eliminar(id_item)
        flash("Producto eliminado.", "success")
    except Exception:
        flash("No se puede eliminar: el ítem está vinculado a órdenes históricas.", "danger")
    return redirect(url_for('inventario'))

@app.route('/turnos')
def gestionar_turnos():
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
    
    q = request.args.get('q', '').strip()
    cursor = DB.cursor(dictionary=True)
    if q:
        sql = """SELECT * FROM turno 
                 WHERE Estado = 'Pendiente' AND (DNI_CUIL LIKE %s OR ID_Turno = %s OR Nombre_Completo LIKE %s)
                 ORDER BY Fecha_Solicitud DESC"""
        like_q = f"%{q}%"
        id_q = int(q) if q.isdigit() else 0
        cursor.execute(sql, (like_q, id_q, like_q))
    else:
        cursor.execute("SELECT * FROM turno WHERE Estado = 'Pendiente' ORDER BY Fecha_Solicitud DESC")
        
    turnos = cursor.fetchall()
    cursor.close()
    return render_template('turnos.html', turnos=turnos, busqueda=q)

@app.route('/procesar_turno/<int:id_turno>', methods=['POST'])
def procesar_turno(id_turno):
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
    
    cursor = DB.cursor(dictionary=True)
    cursor.execute("SELECT DNI_CUIL, Nombre_Completo, Email, Telefono FROM turno WHERE ID_Turno = %s", (id_turno,))
    turno = cursor.fetchone()
    
    cursor.execute("UPDATE turno SET Estado = 'Procesado' WHERE ID_Turno = %s", (id_turno,))
    DB.commit()
    cursor.close()
    
    flash("Turno validado exitosamente. Proceda a generar la Orden de Trabajo formal.", "success")
    
    if turno:
        return redirect(url_for('ingreso_equipo', dni=turno['DNI_CUIL'], nombre=turno['Nombre_Completo'], email=turno['Email'], telefono=turno['Telefono']))
    
    return redirect(url_for('ingreso_equipo'))

@app.route('/ingreso_equipo', methods=['GET', 'POST'])
def ingreso_equipo():
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
        
    if request.method == 'POST':
        dni = request.form.get('dni')
        nom = request.form.get('nombre')
        tel = request.form.get('telefono')
        em = request.form.get('email')
        pw = request.form.get('password_web')
        ns = request.form.get('nro_serie')
        mod = request.form.get('modelo')
        tip = request.form.get('tipo')
        
        if not dni.isdigit() or not (7 <= len(dni) <= 11):
            flash("Error: El DNI debe ser numérico.", "danger")
            return redirect(url_for('ingreso_equipo'))

        try:
            cursor = DB.cursor(dictionary=True)
            cursor.execute("SELECT ID_Cliente FROM cliente WHERE DNI_CUIL = %s", (dni,))
            cl = cursor.fetchone()
            id_c = cl['ID_Cliente'] if cl else None
            if not id_c:
                cursor.execute("INSERT INTO cliente (DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web) VALUES (%s,%s,%s,%s,%s)", (dni,nom,em,tel,pw))
                id_c = cursor.lastrowid
            cursor.execute("INSERT INTO equipo (Numero_Serie, Marca_Modelo, Tipo_Dispositivo, Cliente_ID_Cliente) VALUES (%s,%s,%s,%s)", (ns,mod,tip,id_c))
            id_eq = cursor.lastrowid
            cursor.execute("INSERT INTO orden_trabajo (Estado_General, Fecha_Creacion, Equipo_ID_Equipo, Empleado_ID_Empleado) VALUES (%s,%s,%s,%s)", ('Para Revisión', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id_eq, session['usuario_id']))
            id_o = cursor.lastrowid
            DB.commit()
            cursor.close()
            Seguimiento.registrar_hito(id_o, "Ingresado", "El equipo ingresó al laboratorio para su revisión inicial.")
            flash(f"¡Éxito! Orden #{id_o} generada.", "success")
        except Exception as e: 
            flash(f"Error: {e}", "danger")
        return redirect(url_for('ingreso_equipo'))
        
    datos_turno = {
        'dni': request.args.get('dni', ''),
        'nombre': request.args.get('nombre', ''),
        'email': request.args.get('email', ''),
        'telefono': request.args.get('telefono', '')
    }
    return render_template('ingreso_equipo.html', datos=datos_turno)

@app.route('/presupuestos_pendientes')
def presupuestos_pendientes():
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] == 'Esperando Aprobación']
    return render_template('presupuestos_pendientes.html', trabajos=ordenes)

@app.route('/cotizar_orden/<int:id_orden>', methods=['GET', 'POST'])
def cotizar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT d.Cantidad * i.Precio_Actual as subtotal FROM detalle_orden d 
                      JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                      WHERE d.Orden_Trabajo_ID_OT = %s""", (id_orden,))
    total = sum(d['subtotal'] for d in cursor.fetchall())
    
    if request.method == 'POST':
        cursor.execute("SELECT Equipo_ID_Equipo FROM orden_trabajo WHERE ID_OT = %s", (id_orden,))
        id_eq = cursor.fetchone()['Equipo_ID_Equipo']
        id_pres = Presupuesto(total, id_eq).registrar()
        cursor.execute("UPDATE orden_trabajo SET Presupuesto_ID_Presupuesto = %s, Estado_General = 'Esperando Respuesta' WHERE ID_OT = %s", (id_pres, id_orden))
        DB.commit()
        Seguimiento.registrar_hito(id_orden, "Esperando Respuesta", f"Presupuesto formal generado por ${total}.")
        cursor.close()
        return redirect(url_for('presupuestos_pendientes'))

    cursor.execute("""SELECT d.Cantidad, i.Precio_Actual as precio_unit, (d.Cantidad * i.Precio_Actual) as subtotal, i.Descripcion 
                      FROM detalle_orden d JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                      WHERE d.Orden_Trabajo_ID_OT = %s""", (id_orden,))
    detalles = cursor.fetchall()
    cursor.execute("""SELECT ot.ID_OT as id_orden, ot.Diagnostico_Final as diagnostico_final, 
                      CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, ot.ID_OT as codigo
                      FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s""", (id_orden,))
    orden = cursor.fetchone()
    cursor.close()
    return render_template('cotizar_orden.html', orden=orden, detalles=detalles, total=total)

@app.route('/entregas_pendientes')
def entregas_pendientes():
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
    listos = OrdenTrabajo.buscar_listos_para_entregar()
    return render_template('entregas_pendientes.html', trabajos=listos)

@app.route('/facturar/<int:id_orden>')
def facturar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 2: 
        return redirect(url_for('inicio'))
    orden = OrdenTrabajo.buscar_por_id(id_orden)
    return render_template('facturar_orden.html', orden=orden)

@app.route('/procesar_pago/<int:id_orden>', methods=['POST'])
def procesar_pago(id_orden):
    metodo = request.form.get('metodo_pago')
    orden = OrdenTrabajo.buscar_por_id(id_orden)
    monto = orden['costo'] if orden and orden['costo'] else 0.0
    
    # OOP: registrar factura
    fact = Factura(id_orden, monto, metodo)
    fact.registrar()
    
    # OOP: actualizar estado de OT a Finalizado
    OrdenTrabajo.actualizar_estado(id_orden, 'Finalizado')
    
    # OOP: marcar componentes como consumidos y descontar stock (RF-4.3)
    DetalleOrden.consumir_componentes(id_orden)
    
    Seguimiento.registrar_hito(id_orden, "Finalizado", f"Equipo entregado al cliente. Pago registrado vía {metodo}.")
    flash("Orden finalizada y factura generada.", "success")
    return redirect(url_for('dashboard'))

@app.route('/laboratorio')
def laboratorio():
    if 'usuario_id' not in session or session['rol_id'] != 3: 
        return redirect(url_for('inicio'))
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] in ('Para Revisión', 'En Reparación', 'En Diagnóstico', 'Esperando Repuestos', 'Reparando', 'En Testing')]
    return render_template('laboratorio.html', trabajos=ordenes)

@app.route('/historial_equipo', methods=['POST'])
def historial_equipo():
    if 'usuario_id' not in session or session['rol_id'] != 3: 
        return redirect(url_for('inicio'))
    nro_serie = request.form.get('nro_serie')
    historial = OrdenTrabajo.buscar_historial_por_nro_serie(nro_serie)
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] in ('Para Revisión', 'En Reparación', 'En Diagnóstico', 'Esperando Repuestos', 'Reparando', 'En Testing')]
    if not historial:
        flash("No se encontraron registros históricos para ese número de serie.", "warning")
    return render_template('laboratorio.html', trabajos=ordenes, historial=historial, serie_buscada=nro_serie)

@app.route('/historial_general')
def historial_general():
    if 'usuario_id' not in session:
        return redirect(url_for('inicio'))
    ordenes = OrdenTrabajo.buscar_general()
    return render_template('historial_general.html', ordenes=ordenes)

@app.route('/detalle_historial/<int:id_orden>')
def detalle_historial(id_orden):
    if 'usuario_id' not in session:
        return redirect(url_for('inicio'))
    orden = OrdenTrabajo.buscar_detalle_completo(id_orden)
    detalles = DetalleOrden.buscar_por_orden(id_orden)
    hitos = Seguimiento.buscar_por_orden(id_orden)
    return render_template('detalle_historial.html', orden=orden, detalles=detalles, hitos=hitos)

@app.route('/gestionar_orden/<int:id_orden>', methods=['GET', 'POST'])
def gestionar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 3: 
        return redirect(url_for('inicio'))
    
    orden = OrdenTrabajo.buscar_detalle_completo(id_orden)
    if not orden:
        flash("La orden no existe.", "danger")
        return redirect(url_for('laboratorio'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'actualizar_estado':
            nuevo_est = request.form.get('nuevo_estado')
            if nuevo_est in ('En Diagnóstico', 'Esperando Repuestos', 'Reparando', 'En Testing', 'Para Revisión'):
                OrdenTrabajo.actualizar_estado(id_orden, nuevo_est)
                Seguimiento.registrar_hito(id_orden, nuevo_est, f"El técnico actualizó el estado a: {nuevo_est}.")
                flash(f"Estado actualizado a '{nuevo_est}'.", "success")
            else:
                flash("Estado inválido para actualización manual.", "danger")
                
        elif orden['estado'] in ('Para Revisión', 'En Diagnóstico'):
            # Registrar diagnóstico e ir a Esperando Aprobación
            diag = request.form.get('diagnostico')
            if diag:
                OrdenTrabajo.actualizar_estado(id_orden, 'Esperando Aprobación')
                OrdenTrabajo.actualizar_diagnostico(id_orden, diag)
                Seguimiento.registrar_hito(id_orden, "Diagnóstico Listo", diag)
                flash("Diagnóstico guardado y orden enviada a recepción para cotizar.", "success")
            else:
                flash("El diagnóstico es obligatorio.", "danger")
                
        elif orden['estado'] in ('En Reparación', 'Esperando Repuestos', 'Reparando', 'En Testing'):
            # Registrar QA para pasar a Listo para Entregar
            t = request.form.get('temperaturas')
            b = request.form.get('benchmark')
            o = request.form.get('observaciones')
            
            if not t or not b or not o:
                flash("Error: Todos los campos del Control de Calidad son obligatorios para entregar el equipo.", "danger")
            else:
                try:
                    ControlCalidad(id_orden, session['usuario_id'], t, b, o).registrar()
                    OrdenTrabajo.actualizar_estado(id_orden, 'Listo para Entregar')
                    Seguimiento.registrar_hito(id_orden, "Listo para Entregar", "Control QA aprobado satisfactoriamente.")
                    
                    # RF-5.2: Aviso de retiro al cliente
                    orden_actualizada = OrdenTrabajo.buscar_detalle_completo(id_orden)
                    import_final = orden_actualizada['presupuesto'] or 0.0
                    print(f"\n>>> [NOTIFICACIÓN ENVIADA] Destinatario: {orden_actualizada['email']} | Teléfono: {orden_actualizada['telefono']}")
                    print(f">>> Asunto: Equipo Listo para Retirar - Orden #{id_orden}")
                    print(f">>> Mensaje: Estimado/a {orden_actualizada['cliente']}, su equipo ({orden_actualizada['equipo']}) ha superado las pruebas de control de calidad y está listo para retirar. El importe final congelado a abonar en el local es de ${import_final}.\n")
                    
                    flash("Control de calidad aprobado. El equipo está listo para entregar y se notificó al cliente.", "success")
                except Exception as e: 
                    flash(f"Error en QA: {e}", "danger")
        else:
            flash("No se puede gestionar la orden en su estado actual.", "warning")
            
        return redirect(url_for('laboratorio'))

    detalles = DetalleOrden.buscar_por_orden(id_orden)
    if orden:
        orden['diagnostico_final'] = orden['diagnostico']
    return render_template('gestionar_orden.html', orden=orden, inventario=Inventario.listar_todo(), detalles=detalles)

@app.route('/agregar_repuesto/<int:id_orden>', methods=['POST'])
def agregar_repuesto(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 3: 
        return redirect(url_for('inicio'))
    id_i = request.form.get('id_item')
    cant = int(request.form.get('cantidad'))
    
    it = Inventario.buscar_por_id(id_i)
    if it and (it['tipo_item'] != 'Repuesto_Fisico' or cant <= it['stock']):
        DetalleOrden(cant, it['precio'], id_orden, id_i).registrar()
        flash("Ítem añadido.", "info")
    else: 
        flash("Error: Stock insuficiente.", "danger")
        
    return redirect(url_for('gestionar_orden', id_orden=id_orden))

@app.route('/eliminar_repuesto_ot/<int:id_orden>/<int:id_item>', methods=['POST'])
def eliminar_repuesto_ot(id_orden, id_item):
    if 'usuario_id' not in session or session['rol_id'] != 3: 
        return redirect(url_for('inicio'))
    if DetalleOrden.eliminar_item_ot(id_orden, id_item):
        flash("Ítem removido.", "success")
    else:
        flash("Error al remover ítem.", "danger")
    return redirect(url_for('gestionar_orden', id_orden=id_orden))

@app.route('/tracking', methods=['GET', 'POST'])
def tracking_login():
    if request.method == 'POST':
        dni = request.form.get('dni')
        pw = request.form.get('password_web')
        cl = Cliente.buscar_por_credenciales(dni, pw)
        if cl: 
            session.update({'cliente_id': cl['id'], 'cliente_nombre': cl['nombre']})
            return redirect(url_for('portal_cliente'))
        flash("Datos incorrectos.", "danger")
    return render_template('login.html')

@app.route('/portal_cliente')
def portal_cliente():
    if 'cliente_id' not in session: 
        return redirect(url_for('inicio'))
    ord = OrdenTrabajo.buscar_por_cliente(session['cliente_id'])
    det = DetalleOrden.buscar_por_cliente(session['cliente_id'])
    hit = Seguimiento.listar_todos()
    return render_template('portal_cliente.html', ordenes=ord, hitos=hit, detalles=det)

@app.route('/responder_presupuesto/<int:id_orden>/<respuesta>')
def responder_presupuesto(id_orden, respuesta):
    est = "En Reparación" if respuesta == 'aprobar' else "Rechazado"
    est_presupuesto = "Aprobado" if respuesta == 'aprobar' else "Rechazado"
    
    orden = OrdenTrabajo.buscar_por_id(id_orden)
    if orden and orden['id_presupuesto']:
        Presupuesto.actualizar_estado(orden['id_presupuesto'], est_presupuesto)
        
    if respuesta == 'aprobar':
        # Marcar repuestos como 'Reservados' (RF-4.3)
        DetalleOrden.reservar_componentes(id_orden)
        
    OrdenTrabajo.actualizar_estado(id_orden, est)
    Seguimiento.registrar_hito(id_orden, est, f"El cliente {respuesta}ó el presupuesto.")
    return redirect(url_for('portal_cliente'))

@app.route('/cambiar_password_cliente', methods=['POST'])
def cambiar_password_cliente():
    if 'cliente_id' not in session:
        return redirect(url_for('inicio'))
    
    nueva = request.form.get('nueva_password')
    confirmar = request.form.get('confirmar_password')
    
    if nueva != confirmar:
        flash("Las contraseñas no coinciden.", "danger")
        return redirect(url_for('portal_cliente'))
        
    if Cliente.actualizar_password(session['cliente_id'], nueva):
        flash("Contraseña actualizada exitosamente.", "success")
    else:
        flash("Error al actualizar la contraseña.", "danger")
        
    return redirect(url_for('portal_cliente'))

@app.route('/seguimiento/<codigo_tracking>')
def seguimiento_publico(codigo_tracking):
    orden = OrdenTrabajo.buscar_por_codigo_tracking(codigo_tracking)
    if not orden:
        flash("Código de seguimiento inválido.", "danger")
        return redirect(url_for('inicio'))
        
    hitos = Seguimiento.buscar_por_orden(orden['id_orden'])
    detalles = DetalleOrden.buscar_por_orden(orden['id_orden'])
    
    return render_template('seguimiento.html', orden=orden, hitos=hitos, detalles=detalles)

@app.route('/logout_cliente')
def logout_cliente():
    session.pop('cliente_id', None)
    session.pop('cliente_nombre', None)
    return redirect(url_for('inicio'))

if __name__ == '__main__':
    app.run(debug=True)