from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import datetime
import re
from config.database import DB
from auth.login import Autenticacion
from modelos.cliente import Cliente
from modelos.orden_trabajo import OrdenTrabajo
from modelos.detalle_orden import DetalleOrden
from modelos.seguimiento import Seguimiento
from modelos.empleado import Empleado
from modelos.presupuesto import Presupuesto

bp_auth = Blueprint('auth', __name__)

@bp_auth.route('/')
def inicio():
    if 'usuario_id' in session: 
        return redirect(url_for('dashboard.dashboard'))
    return render_template('login.html')

@bp_auth.route('/login', methods=['POST'])
def login():
    user = request.form.get('usuario')
    pw = request.form.get('password')
    res = Autenticacion().iniciar_sesion(user, pw)
    if res:
        session.update({
            'usuario_id': res['id'], 
            'nombre': res['nombre'], 
            'rol_id': int(res['rol_id']), 
            'nombre_rol': res['nombre_rol']
        })
        
        # si la clave es la por defecto, obligar a cambiarla
        if pw in ('admin123', 'recep123', 'tecnico123', '123'):
            session['force_password_change'] = 'empleado'
            return redirect(url_for('auth.cambiar_password_obligatorio'))
            
        return redirect(url_for('dashboard.dashboard'))
    return render_template('login.html', error="Credenciales inválidas o cuenta desactivada.")

@bp_auth.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('nombre', None)
    session.pop('rol_id', None)
    session.pop('nombre_rol', None)
    session.pop('force_password_change', None)
    return redirect(url_for('auth.inicio'))

@bp_auth.route('/tracking', methods=['GET', 'POST'])
def tracking_login():
    if request.method == 'GET' and 'cliente_id' in session:
        return redirect(url_for('auth.portal_cliente'))
        
    if request.method == 'POST':
        dni = request.form.get('dni', '').strip()
        pw = request.form.get('password_web', '').strip()
        
        # Limpiar DNI de puntos, guiones y espacios para robustez
        dni_clean = re.sub(r'[^0-9]', '', dni)
        
        cl = Cliente.buscar_por_credenciales(dni_clean, pw)
        if cl: 
            session.update({'cliente_id': cl['id'], 'cliente_nombre': cl['nombre']})
            # si el cliente nunca cambió su contraseña provisional, obligar
            if not cl.get('password_cambiada', 1):
                session['force_password_change'] = 'cliente'
                return redirect(url_for('auth.cambiar_password_obligatorio'))
            return redirect(url_for('auth.portal_cliente'))
        flash("Datos incorrectos.", "danger")
    return render_template('login.html')

@bp_auth.route('/cambiar_password_obligatorio', methods=['GET', 'POST'])
def cambiar_password_obligatorio():
    # valida que exista sesion
    if 'usuario_id' not in session and 'cliente_id' not in session:
        return redirect(url_for('auth.inicio'))

    if request.method == 'POST':
        nueva = request.form.get('nueva_password')
        confirmar = request.form.get('confirmar_password')

        if not nueva or not confirmar:
            flash("Todos los campos son obligatorios.", "danger")
            return render_template('cambiar_password_obligatorio.html')

        if nueva != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
            return render_template('cambiar_password_obligatorio.html')

        if len(nueva) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "danger")
            return render_template('cambiar_password_obligatorio.html')

        # evitar volver a usar las default
        if nueva in ('123', '1234', 'admin123', 'recep123', 'tecnico123'):
            flash("Por favor, ingrese una contraseña personalizada que no sea por defecto.", "danger")
            return render_template('cambiar_password_obligatorio.html')

        exito = False
        quien = session.get('force_password_change', '')
        if quien == 'cliente' and 'cliente_id' in session:
            exito = Cliente.actualizar_password(session['cliente_id'], nueva)
        elif quien == 'empleado' and 'usuario_id' in session:
            exito = Empleado.actualizar_password(session['usuario_id'], nueva)
        elif 'cliente_id' in session and 'usuario_id' not in session:
            exito = Cliente.actualizar_password(session['cliente_id'], nueva)
            quien = 'cliente'
        elif 'usuario_id' in session:
            exito = Empleado.actualizar_password(session['usuario_id'], nueva)
            quien = 'empleado'

        if exito:
            session.pop('force_password_change', None)
            flash("Contraseña actualizada exitosamente. ¡Bienvenido/a!", "success")
            if quien == 'cliente':
                return redirect(url_for('auth.portal_cliente'))
            else:
                return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Error al actualizar la contraseña.", "danger")

    return render_template('cambiar_password_obligatorio.html')

@bp_auth.route('/portal_cliente')
def portal_cliente():
    if 'cliente_id' not in session: 
        return redirect(url_for('auth.inicio'))
    ord = OrdenTrabajo.buscar_por_cliente(session['cliente_id'])
    det = DetalleOrden.buscar_por_cliente(session['cliente_id'])
    hit = Seguimiento.listar_todos()
    return render_template('portal_cliente.html', ordenes=ord, hitos=hit, detalles=det)

@bp_auth.route('/responder_presupuesto/<int:id_orden>/<respuesta>')
def responder_presupuesto(id_orden, respuesta):
    if 'cliente_id' not in session:
        return redirect(url_for('auth.inicio'))
    
    # validar que la respuesta sea una de las permitidas
    if respuesta not in ('aprobar', 'rechazar'):
        flash("Acción no válida.", "danger")
        return redirect(url_for('auth.portal_cliente'))
        
    orden_completa = OrdenTrabajo.buscar_detalle_completo(id_orden)
    if not orden_completa or orden_completa['estado'] not in ('Esperando Aprobación', 'Esperando Respuesta'):
        flash("La orden no se encuentra en estado de aprobación.", "danger")
        return redirect(url_for('auth.portal_cliente'))
    
    # validar que la orden pertenezca al cliente logueado
    from modelos.equipo import Equipo
    cursor_check = DB.cursor(dictionary=True)
    try:
        cursor_check.execute("SELECT e.Cliente_ID_Cliente FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s", (id_orden,))
        row = cursor_check.fetchone()
        if not row or row['Cliente_ID_Cliente'] != session['cliente_id']:
            flash("No tiene permiso para responder esta orden.", "danger")
            return redirect(url_for('auth.portal_cliente'))
    finally:
        cursor_check.close()
        
    est = "En Reparación" if respuesta == 'aprobar' else "Rechazado"
    est_presupuesto = "Aprobado" if respuesta == 'aprobar' else "Rechazado"
    
    orden_obj = OrdenTrabajo.obtener_por_id(id_orden)
    if orden_obj and orden_obj.id_presupuesto:
        Presupuesto.actualizar_estado(orden_obj.id_presupuesto, est_presupuesto)
        
    if respuesta == 'aprobar':
        # reservar componentes
        DetalleOrden.reservar_componentes(id_orden)
        
    if orden_obj:
        orden_obj.actualizar_estado(est)
    
    accion_texto = "aprobó" if respuesta == 'aprobar' else "rechazó"
    Seguimiento.registrar_hito(id_orden, est, f"El cliente {accion_texto} el presupuesto.")
    return redirect(url_for('auth.portal_cliente'))

@bp_auth.route('/cambiar_password_cliente', methods=['POST'])
def cambiar_password_cliente():
    if 'cliente_id' not in session:
        return redirect(url_for('auth.inicio'))
    
    nueva = request.form.get('nueva_password')
    confirmar = request.form.get('confirmar_password')
    
    if not nueva or not confirmar:
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('auth.portal_cliente'))
    
    if len(nueva) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "danger")
        return redirect(url_for('auth.portal_cliente'))
    
    if nueva != confirmar:
        flash("Las contraseñas no coinciden.", "danger")
        return redirect(url_for('auth.portal_cliente'))
        
    if Cliente.actualizar_password(session['cliente_id'], nueva):
        flash("Contraseña actualizada exitosamente.", "success")
    else:
        flash("Error al actualizar la contraseña.", "danger")
        
    return redirect(url_for('auth.portal_cliente'))

@bp_auth.route('/seguimiento/<codigo_tracking>')
def seguimiento_publico(codigo_tracking):
    orden = OrdenTrabajo.buscar_por_codigo_tracking(codigo_tracking)
    if not orden:
        flash("Código de seguimiento inválido.", "danger")
        return redirect(url_for('auth.tracking_login'))
        
    hitos = Seguimiento.buscar_por_orden(orden['id_orden'])
    detalles = DetalleOrden.buscar_por_orden(orden['id_orden'])
    
    return render_template('seguimiento.html', orden=orden, hitos=hitos, detalles=detalles)

@bp_auth.route('/logout_cliente')
def logout_cliente():
    session.pop('cliente_id', None)
    session.pop('cliente_nombre', None)
    return redirect(url_for('auth.tracking_login'))

@bp_auth.route('/solicitar_turno', methods=['GET', 'POST'])
def solicitar_turno():
    if request.method == 'POST':
        dni = request.form.get('dni', '').strip()
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        servicio = request.form.get('servicio', '').strip()
        presupuesto = request.form.get('presupuesto_estimado', '0')
        try:
            garantia = int(request.form.get('garantia', '0'))
        except (ValueError, TypeError):
            garantia = 0
        
        # validaciones de entrada del cliente
        if not dni or not dni.isdigit() or not (7 <= len(dni) <= 11):
            flash("DNI debe ser numérico entre 7 y 11 dígitos.", "danger")
            return render_template('solicitar_turno.html')
        if not nombre or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", nombre):
            flash("El nombre solo debe contener letras y espacios.", "danger")
            return render_template('solicitar_turno.html')
        if not telefono or not re.match(r"^\d{8,15}$", telefono):
            flash("Teléfono debe tener entre 8 y 15 dígitos.", "danger")
            return render_template('solicitar_turno.html')
        if not email or not re.match(r"^[\w\.\+-]+@[\w\.-]+\.\w+$", email):
            flash("Formato de email inválido.", "danger")
            return render_template('solicitar_turno.html')
        if not servicio:
            flash("Debe seleccionar un servicio.", "danger")
            return render_template('solicitar_turno.html')
        servicios_validos = ('Limpieza y Mantenimiento', 'Formateo e Instalación OS', 'No enciende', 'Lentitud extrema', 'Otro')
        if servicio not in servicios_validos:
            flash("Servicio seleccionado no válido.", "danger")
            return render_template('solicitar_turno.html')
        try:
            presupuesto = float(presupuesto)
            if presupuesto < 0:
                presupuesto = 0
        except (ValueError, TypeError):
            presupuesto = 0
        if garantia not in (0, 1):
            flash("Valor de garantía no válido.", "danger")
            return render_template('solicitar_turno.html')
            
        try:
            # 1. Buscar o registrar cliente primero
            cl = Cliente.buscar_por_dni(dni)
            id_c = cl['id'] if cl else None
            if not id_c:
                # Se registra con contraseña provisional '123'
                id_c = Cliente(dni, nombre, email, telefono, "123").registrar()
                
            cursor = DB.cursor()
            fecha_hoy = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # crear tabla turno por las dudas con la clave ajena a cliente
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
            
            cursor.execute("""
                INSERT INTO turno (Cliente_ID_Cliente, Servicio, Presupuesto_Estimado, Fecha_Solicitud, Estado, Garantia)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_c, servicio, float(presupuesto), fecha_hoy, 'Pendiente', garantia))
            DB.commit()
            cursor.close()
            flash("Turno solicitado con éxito. Nos comunicaremos a la brevedad.", "success")
            return redirect(url_for('auth.solicitar_turno'))
        except Exception as e:
            flash(f"Error al solicitar turno: {e}", "danger")
            return render_template('solicitar_turno.html')
            
    return render_template('solicitar_turno.html')

@bp_auth.route('/resetear_password_cliente', methods=['POST'])
def resetear_password_cliente():
    """Permite a un recepcionista o admin resetear la contraseña de un cliente."""
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) not in (1, 2):
        return redirect(url_for('auth.inicio'))
    
    dni = request.form.get('dni_reset', '').strip()
    nueva_password = request.form.get('nueva_password_reset', '').strip()
    
    if not dni or not nueva_password:
        flash("DNI y nueva contraseña son obligatorios.", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    if len(nueva_password) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    cl = Cliente.buscar_por_dni(re.sub(r'[^0-9]', '', dni))
    if not cl:
        flash(f"No se encontró ningún cliente con DNI: {dni}", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    if Cliente.actualizar_password(cl['id'], nueva_password):
        flash(f"Contraseña del cliente {cl['nombre']} reseteada exitosamente. Nueva clave temporal: {nueva_password}", "success")
    else:
        flash("Error al resetear la contraseña.", "danger")
    
    return redirect(url_for('dashboard.dashboard'))
