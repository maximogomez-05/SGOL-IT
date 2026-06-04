from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from config.database import DB
import datetime
import re
import uuid
import os
from werkzeug.utils import secure_filename
from modelos.cliente import Cliente
from modelos.equipo import Equipo
from modelos.orden_trabajo import OrdenTrabajo
from modelos.presupuesto import Presupuesto
from modelos.seguimiento import Seguimiento
from modelos.detalle_orden import DetalleOrden
from modelos.inventario import Inventario
from modelos.control_calidad import ControlCalidad

bp_ordenes = Blueprint('ordenes', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp_ordenes.route('/turnos')
def gestionar_turnos():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    
    q = request.args.get('q', '').strip()
    cursor = DB.cursor(dictionary=True)
    
    # asegurar tabla turno y columnas de garantia
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turno (
                ID_Turno INT AUTO_INCREMENT PRIMARY KEY,
                Cliente_ID_Cliente INT NOT NULL,
                Servicio VARCHAR(100),
                Presupuesto_Estimado DECIMAL(10,2),
                Fecha_Solicitud DATETIME,
                Estado VARCHAR(50) DEFAULT 'Pendiente',
                Garantia TINYINT(1) DEFAULT 0,
                FOREIGN KEY (Cliente_ID_Cliente) REFERENCES cliente(ID_Cliente) ON DELETE CASCADE
            )
        """)
        DB.commit()
    except Exception as e:
        print(f"Error al verificar/crear tabla turno: {e}")

    try:
        cursor.execute("SHOW COLUMNS FROM turno LIKE 'Garantia'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE turno ADD COLUMN Garantia TINYINT(1) DEFAULT 0")
            DB.commit()
    except Exception as e:
        print(f"Error al verificar/agregar Garantia a turno: {e}")

    try:
        cursor.execute("SHOW COLUMNS FROM orden_trabajo LIKE 'Garantia'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE orden_trabajo ADD COLUMN Garantia TINYINT(1) DEFAULT 0")
            DB.commit()
    except Exception as e:
        print(f"Error al verificar/agregar Garantia a orden_trabajo: {e}")

    try:
        cursor.execute("SHOW COLUMNS FROM orden_trabajo LIKE 'Servicio'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE orden_trabajo ADD COLUMN Servicio VARCHAR(100)")
            DB.commit()
    except Exception as e:
        print(f"Error al verificar/agregar Servicio a orden_trabajo: {e}")
        
    if q:
        sql = """SELECT t.ID_Turno, t.Servicio, t.Presupuesto_Estimado, t.Fecha_Solicitud, t.Estado, t.Garantia,
                        c.DNI_CUIL, c.Nombre_Completo, c.Email, c.Telefono 
                 FROM turno t 
                 JOIN cliente c ON t.Cliente_ID_Cliente = c.ID_Cliente
                 WHERE t.Estado = 'Pendiente' AND (c.DNI_CUIL LIKE %s OR t.ID_Turno = %s OR c.Nombre_Completo LIKE %s)
                 ORDER BY t.Fecha_Solicitud DESC"""
        like_q = f"%{q}%"
        id_q = int(q) if q.isdigit() else 0
        cursor.execute(sql, (like_q, id_q, like_q))
    else:
        cursor.execute("""SELECT t.ID_Turno, t.Servicio, t.Presupuesto_Estimado, t.Fecha_Solicitud, t.Estado, t.Garantia,
                                 c.DNI_CUIL, c.Nombre_Completo, c.Email, c.Telefono 
                          FROM turno t 
                          JOIN cliente c ON t.Cliente_ID_Cliente = c.ID_Cliente
                          WHERE t.Estado = 'Pendiente' 
                          ORDER BY t.Fecha_Solicitud DESC""")
        
    turnos = cursor.fetchall()
    cursor.close()
    return render_template('turnos.html', turnos=turnos, busqueda=q)

@bp_ordenes.route('/procesar_turno/<int:id_turno>', methods=['POST'])
def procesar_turno(id_turno):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT c.DNI_CUIL, c.Nombre_Completo, c.Email, c.Telefono, t.Garantia, t.Servicio 
                      FROM turno t 
                      JOIN cliente c ON t.Cliente_ID_Cliente = c.ID_Cliente 
                      WHERE t.ID_Turno = %s""", (id_turno,))
    turno = cursor.fetchone()
    
    cursor.execute("UPDATE turno SET Estado = 'Procesado' WHERE ID_Turno = %s", (id_turno,))
    DB.commit()
    cursor.close()
    
    flash("Turno validado exitosamente. Proceda a generar la Orden de Trabajo formal.", "success")
    
    if turno:
        return redirect(url_for('ordenes.ingreso_equipo', 
                               dni=turno['DNI_CUIL'], 
                               nombre=turno['Nombre_Completo'], 
                               email=turno['Email'], 
                               telefono=turno['Telefono'],
                               garantia=turno['Garantia'],
                               servicio=turno['Servicio']))
    
    return redirect(url_for('ordenes.ingreso_equipo'))

@bp_ordenes.route('/ingreso_equipo', methods=['GET', 'POST'])
def ingreso_equipo():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
        
    if request.method == 'POST':
        dni = request.form.get('dni')
        nom = request.form.get('nombre')
        tel = request.form.get('telefono')
        em = request.form.get('email')
        pw = request.form.get('password_web')
        ns = request.form.get('nro_serie')
        mod = request.form.get('modelo')
        tip = request.form.get('tipo')
        detalles_visuales = request.form.get('detalles_visuales', '').strip()
        garantia = int(request.form.get('garantia', '0'))
        servicio = request.form.get('servicio', '').strip()
        
        # validaciones basicas
        if not dni or not dni.isdigit() or not (7 <= len(dni) <= 11):
            flash("DNI debe ser numérico entre 7 y 11 dígitos.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not nom or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nom):
            flash("El nombre solo debe contener letras y espacios.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not tel or not re.match(r"^\d{8,15}$", tel):
            flash("Teléfono debe tener entre 8 y 15 dígitos sin espacios.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not em or not re.match(r"^[\w\.\+-]+@[\w\.-]+\.\w+$", em):
            flash("Formato de email inválido.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not pw or len(pw) < 6:
            flash("La clave web debe tener al menos 6 caracteres.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not ns or not re.match(r"^[a-zA-Z0-9\-_/\s]+$", ns):
            flash("Número de serie inválido.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not mod or "<" in mod or ">" in mod:
            flash("Modelo contiene caracteres inválidos.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if tip not in ('Notebook', 'PC de Escritorio', 'All-in-One', 'Impresora', 'Otro'):
            flash("Tipo de dispositivo inválido.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if not servicio:
            flash("Debe seleccionar un tipo de servicio.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        if "<" in detalles_visuales or ">" in detalles_visuales:
            flash("Las observaciones contienen caracteres inválidos.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))

        # subida de fotos (maximo 4)
        fotos_subidas = []
        fotos = request.files.getlist('fotos')
        fotos = [f for f in fotos if f and f.filename != '']
        if len(fotos) > 4:
            flash("Solo puedes subir un máximo de 4 fotos.", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
            
        for f in fotos:
            if f and allowed_file(f.filename):
                nombre_seguro = secure_filename(f.filename)
                ext = nombre_seguro.rsplit('.', 1)[1].lower()
                nuevo_nombre = f"{uuid.uuid4().hex}.{ext}"
                ruta_completa = os.path.join(current_app.config['UPLOAD_FOLDER'], nuevo_nombre)
                f.save(ruta_completa)
                fotos_subidas.append(nuevo_nombre)
            elif f:
                flash("Formato de imagen no permitido. Usa png, jpg, jpeg o webp.", "danger")
                return redirect(url_for('ordenes.ingreso_equipo'))
                
        fotos_str = ",".join(fotos_subidas) if fotos_subidas else None

        try:
            # busca o registra el cliente en la BD
            cl = Cliente.buscar_por_dni(dni)
            id_c = cl['id'] if cl else None
            if not id_c:
                id_c = Cliente(dni, nom, em, tel, pw).registrar()
            else:
                # Si el cliente ya existe (ej: por registrar un turno previo), actualizamos su contraseña web
                # a la nueva contraseña temporal provista en la recepción
                Cliente.actualizar_password(id_c, pw)
                
            # busca o registra el equipo
            eq_existente = Equipo.buscar_por_numero_serie(ns)
            if eq_existente:
                id_eq = eq_existente['id']
            else:
                id_eq = Equipo(ns, mod, tip, id_c).registrar()
            
            # crea la orden de trabajo (guarda Detalles_Visuales y Fotos aquí) usando OOP
            orden = OrdenTrabajo(
                id_equipo=id_eq,
                id_empleado=session['usuario_id'],
                detalles_visuales=detalles_visuales,
                fotos=fotos_str,
                garantia=garantia,
                servicio=servicio
            )
            id_o = orden.registrar()
            
            Seguimiento.registrar_hito(id_o, "Ingresado", "El equipo ingresó al laboratorio para su revisión inicial.")
            flash(f"¡Éxito! Orden #{id_o} generada.", "success")
            return redirect(url_for('ordenes.imprimir_ticket', id_orden=id_o))
        except Exception as e: 
            flash(f"Error: {e}", "danger")
            return redirect(url_for('ordenes.ingreso_equipo'))
        
    datos_turno = {
        'dni': request.args.get('dni', ''),
        'nombre': request.args.get('nombre', ''),
        'email': request.args.get('email', ''),
        'telefono': request.args.get('telefono', ''),
        'garantia': request.args.get('garantia', '0'),
        'servicio': request.args.get('servicio', '')
    }
    return render_template('ingreso_equipo.html', datos=datos_turno)

@bp_ordenes.route('/imprimir_ticket/<int:id_orden>')
def imprimir_ticket(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    
    orden = OrdenTrabajo.buscar_detalle_completo(id_orden)
    if not orden:
        flash("La orden no existe.", "danger")
        return redirect(url_for('ordenes.ingreso_equipo'))
        
    return render_template('ticket_recepcion.html', orden=orden)


@bp_ordenes.route('/presupuestos_pendientes')
def presupuestos_pendientes():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] == 'Esperando Aprobación']
    return render_template('presupuestos_pendientes.html', trabajos=ordenes)

@bp_ordenes.route('/cotizar_orden/<int:id_orden>', methods=['GET', 'POST'])
def cotizar_orden(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT d.Cantidad * i.Precio_Actual as subtotal FROM detalle_orden d 
                      JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                      WHERE d.Orden_Trabajo_ID_OT = %s""", (id_orden,))
    total = sum(d['subtotal'] for d in cursor.fetchall())
    
    if request.method == 'POST':
        if total <= 0:
            flash("Error: El total del presupuesto debe ser mayor a $0. Agregue al menos un repuesto o servicio antes de generar la cotización.", "danger")
            cursor.close()
            return redirect(url_for('ordenes.cotizar_orden', id_orden=id_orden))
            
        id_pres = Presupuesto(total).registrar()
        orden_obj = OrdenTrabajo.obtener_por_id(id_orden)
        if orden_obj:
            orden_obj.vincular_presupuesto(id_pres)
        Seguimiento.registrar_hito(id_orden, "Esperando Respuesta", f"Presupuesto formal generado por ${total}.")
        cursor.close()
        return redirect(url_for('ordenes.presupuestos_pendientes'))

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

@bp_ordenes.route('/entregas_pendientes')
def entregas_pendientes():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2): 
        return redirect(url_for('auth.inicio'))
    listos = OrdenTrabajo.buscar_listos_para_entregar()
    return render_template('entregas_pendientes.html', trabajos=listos)

@bp_ordenes.route('/laboratorio')
def laboratorio():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 3): 
        return redirect(url_for('auth.inicio'))
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] in ('Para Revisión', 'En Reparación', 'En Diagnóstico', 'Esperando Repuestos', 'Reparando', 'En Testing')]
    return render_template('laboratorio.html', trabajos=ordenes)

@bp_ordenes.route('/historial_equipo', methods=['POST'])
def historial_equipo():
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 3): 
        return redirect(url_for('auth.inicio'))
    nro_serie = request.form.get('nro_serie')
    historial = OrdenTrabajo.buscar_historial_por_nro_serie(nro_serie)
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] in ('Para Revisión', 'En Reparación', 'En Diagnóstico', 'Esperando Repuestos', 'Reparando', 'En Testing')]
    if not historial:
        flash("No se encontraron registros históricos para ese número de serie.", "warning")
    return render_template('laboratorio.html', trabajos=ordenes, historial=historial, serie_buscada=nro_serie)

@bp_ordenes.route('/historial_general')
def historial_general():
    if 'usuario_id' not in session:
        return redirect(url_for('auth.inicio'))
    ordenes = OrdenTrabajo.buscar_general()
    return render_template('historial_general.html', ordenes=ordenes)

@bp_ordenes.route('/detalle_historial/<int:id_orden>')
def detalle_historial(id_orden):
    if 'usuario_id' not in session:
        return redirect(url_for('auth.inicio'))
    orden = OrdenTrabajo.buscar_detalle_completo(id_orden)
    detalles = DetalleOrden.buscar_por_orden(id_orden)
    hitos = Seguimiento.buscar_por_orden(id_orden)
    return render_template('detalle_historial.html', orden=orden, detalles=detalles, hitos=hitos)

@bp_ordenes.route('/gestionar_orden/<int:id_orden>', methods=['GET', 'POST'])
def gestionar_orden(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 3): 
        return redirect(url_for('auth.inicio'))
    
    orden = OrdenTrabajo.buscar_detalle_completo(id_orden)
    orden_obj = OrdenTrabajo.obtener_por_id(id_orden)
    if not orden or not orden_obj:
        flash("La orden no existe.", "danger")
        return redirect(url_for('ordenes.laboratorio'))

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'actualizar_estado':
            nuevo_est = request.form.get('nuevo_estado')
            if nuevo_est in ('En Diagnóstico', 'Esperando Repuestos', 'Reparando', 'En Testing', 'Para Revisión'):
                orden_obj.actualizar_estado(nuevo_est)
                Seguimiento.registrar_hito(id_orden, nuevo_est, f"El técnico actualizó el estado a: {nuevo_est}.")
                flash(f"Estado actualizado a '{nuevo_est}'.", "success")
            else:
                flash("Estado inválido para actualización manual.", "danger")
                
        elif orden['estado'] in ('Para Revisión', 'En Diagnóstico'):
            diag = request.form.get('diagnostico')
            if diag:
                orden_obj.actualizar_estado('Esperando Aprobación')
                orden_obj.actualizar_diagnostico(diag)
                Seguimiento.registrar_hito(id_orden, "Diagnóstico Listo", diag)
                flash("Diagnóstico guardado y orden enviada a recepción para cotizar.", "success")
            else:
                flash("El diagnóstico es obligatorio.", "danger")
                
        elif orden['estado'] in ('En Reparación', 'Esperando Repuestos', 'Reparando', 'En Testing'):
            t = request.form.get('temperaturas')
            b = request.form.get('benchmark')
            o = request.form.get('observaciones')
            
            if not t or not b or not o:
                flash("Error: Todos los campos del Control de Calidad son obligatorios para entregar el equipo.", "danger")
            else:
                try:
                    ControlCalidad(id_orden, session['usuario_id'], t, b, o).registrar()
                    orden_obj.actualizar_estado('Listo para Entregar')
                    Seguimiento.registrar_hito(id_orden, "Listo para Entregar", "Control QA aprobado satisfactoriamente.")
                    
                    # notificacion en consola
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
            
        return redirect(url_for('ordenes.laboratorio'))

    detalles = DetalleOrden.buscar_por_orden(id_orden)
    if orden:
        orden['diagnostico_final'] = orden['diagnostico']
    return render_template('gestionar_orden.html', orden=orden, inventario=Inventario.listar_todo(), detalles=detalles)

@bp_ordenes.route('/subir_fotos_tecnico/<int:id_orden>', methods=['POST'])
def subir_fotos_tecnico(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 3): 
        return redirect(url_for('auth.inicio'))
        
    orden = OrdenTrabajo.buscar_detalle_completo(id_orden)
    if not orden:
        flash("La orden no existe.", "danger")
        return redirect(url_for('ordenes.laboratorio'))
        
    fotos_subidas = []
    fotos = request.files.getlist('fotos')
    fotos = [f for f in fotos if f and f.filename != '']
    
    if not fotos:
        flash("Debe seleccionar al menos una foto para subir.", "warning")
        return redirect(url_for('ordenes.gestionar_orden', id_orden=id_orden))
        
    if len(fotos) > 4:
        flash("Solo puedes subir un máximo de 4 fotos a la vez.", "danger")
        return redirect(url_for('ordenes.gestionar_orden', id_orden=id_orden))
        
    for f in fotos:
        if f and allowed_file(f.filename):
            nombre_seguro = secure_filename(f.filename)
            ext = nombre_seguro.rsplit('.', 1)[1].lower()
            nuevo_nombre = f"{uuid.uuid4().hex}.{ext}"
            ruta_completa = os.path.join(current_app.config['UPLOAD_FOLDER'], nuevo_nombre)
            f.save(ruta_completa)
            fotos_subidas.append(nuevo_nombre)
        elif f:
            flash("Formato de imagen no permitido. Usa png, jpg, jpeg o webp.", "danger")
            return redirect(url_for('ordenes.gestionar_orden', id_orden=id_orden))
            
    if fotos_subidas:
        orden_obj = OrdenTrabajo.obtener_por_id(id_orden)
        if orden_obj and orden_obj.guardar_fotos(fotos_subidas):
            Seguimiento.registrar_hito(id_orden, orden['estado'], f"El técnico subió {len(fotos_subidas)} nueva(s) fotografía(s) del equipo en estado: {orden['estado']}.")
            flash("Imágenes subidas exitosamente.", "success")
        else:
            flash("Error al actualizar las fotos en la base de datos.", "danger")
            
    return redirect(url_for('ordenes.gestionar_orden', id_orden=id_orden))

@bp_ordenes.route('/agregar_repuesto/<int:id_orden>', methods=['POST'])
def agregar_repuesto(id_orden):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 3): 
        return redirect(url_for('auth.inicio'))
    id_i = request.form.get('id_item')
    cant = int(request.form.get('cantidad') or 0)
    
    it = Inventario.buscar_por_id(id_i)
    if it and (it['tipo_item'] != 'Repuesto_Fisico' or cant <= it['stock']):
        res_reg = DetalleOrden(cant, it['precio'], id_orden, id_i).registrar()
        if res_reg:
            flash("Ítem añadido.", "info")
        else:
            flash("Error al registrar el repuesto en la orden de trabajo.", "danger")
    else: 
        flash("Error: Stock insuficiente.", "danger")
        
    return redirect(url_for('ordenes.gestionar_orden', id_orden=id_orden))

@bp_ordenes.route('/eliminar_repuesto_ot/<int:id_orden>/<int:id_item>', methods=['POST'])
def eliminar_repuesto_ot(id_orden, id_item):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 3): 
        return redirect(url_for('auth.inicio'))
    if DetalleOrden.eliminar_item_ot(id_orden, id_item):
        flash("Ítem removido.", "success")
    else:
        flash("Error al remover ítem.", "danger")
    return redirect(url_for('ordenes.gestionar_orden', id_orden=id_orden))
