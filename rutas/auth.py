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
            session['force_password_change'] = True
            return redirect(url_for('auth.cambiar_password_obligatorio'))
            
        return redirect(url_for('dashboard.dashboard'))
    return render_template('login.html', error="Credenciales inválidas o cuenta desactivada.")

@bp_auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.inicio'))

@bp_auth.route('/tracking', methods=['GET', 'POST'])
def tracking_login():
    if request.method == 'POST':
        dni = request.form.get('dni')
        pw = request.form.get('password_web')
        cl = Cliente.buscar_por_credenciales(dni, pw)
        if cl: 
            session.update({'cliente_id': cl['id'], 'cliente_nombre': cl['nombre']})
            # si usa la clave por defecto del cliente
            if pw in ('1234', '123'):
                session['force_password_change'] = True
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

        # evitar volver a usar las default
        if nueva in ('123', '1234', 'admin123', 'recep123', 'tecnico123'):
            flash("Por favor, ingrese una contraseña personalizada que no sea por defecto.", "danger")
            return render_template('cambiar_password_obligatorio.html')

        exito = False
        if 'usuario_id' in session:
            exito = Empleado.actualizar_password(session['usuario_id'], nueva)
        elif 'cliente_id' in session:
            exito = Cliente.actualizar_password(session['cliente_id'], nueva)

        if exito:
            session.pop('force_password_change', None)
            flash("Contraseña actualizada exitosamente. ¡Bienvenido/a!", "success")
            if 'usuario_id' in session:
                return redirect(url_for('dashboard.dashboard'))
            else:
                return redirect(url_for('auth.portal_cliente'))
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
    est = "En Reparación" if respuesta == 'aprobar' else "Rechazado"
    est_presupuesto = "Aprobado" if respuesta == 'aprobar' else "Rechazado"
    
    orden = OrdenTrabajo.buscar_por_id(id_orden)
    if orden and orden['id_presupuesto']:
        Presupuesto.actualizar_estado(orden['id_presupuesto'], est_presupuesto)
        
    if respuesta == 'aprobar':
        # reservar componentes
        DetalleOrden.reservar_componentes(id_orden)
        
    OrdenTrabajo.actualizar_estado(id_orden, est)
    Seguimiento.registrar_hito(id_orden, est, f"El cliente {respuesta}ó el presupuesto.")
    return redirect(url_for('auth.portal_cliente'))

@bp_auth.route('/cambiar_password_cliente', methods=['POST'])
def cambiar_password_cliente():
    if 'cliente_id' not in session:
        return redirect(url_for('auth.inicio'))
    
    nueva = request.form.get('nueva_password')
    confirmar = request.form.get('confirmar_password')
    
    if nueva != confirmar:
        flash("Las contraseñas no coinciden.", "danger")
        return redirect(url_for('auth.portal_cliente'))
        
    if Cliente.actualizar_password(session['cliente_id'], nueva):
        flash("Contraseña actualizada exitosamente.", "success")
    else:
        flash("Error al actualizar la contraseña.", "danger")
        
    return redirect(url_for('portal_cliente'))

@bp_auth.route('/seguimiento/<codigo_tracking>')
def seguimiento_publico(codigo_tracking):
    orden = OrdenTrabajo.buscar_por_codigo_tracking(codigo_tracking)
    if not orden:
        flash("Código de seguimiento inválido.", "danger")
        return redirect(url_for('auth.inicio'))
        
    hitos = Seguimiento.buscar_por_orden(orden['id_orden'])
    detalles = DetalleOrden.buscar_por_orden(orden['id_orden'])
    
    return render_template('seguimiento.html', orden=orden, hitos=hitos, detalles=detalles)

@bp_auth.route('/logout_cliente')
def logout_cliente():
    session.pop('cliente_id', None)
    session.pop('cliente_nombre', None)
    return redirect(url_for('auth.inicio'))

@bp_auth.route('/solicitar_turno', methods=['GET', 'POST'])
def solicitar_turno():
    if request.method == 'POST':
        dni = request.form.get('dni', '').strip()
        nombre = request.form.get('nombre', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        servicio = request.form.get('servicio', '').strip()
        presupuesto = request.form.get('presupuesto_estimado', '0')
        
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
                    FOREIGN KEY (Cliente_ID_Cliente) REFERENCES cliente(ID_Cliente) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                INSERT INTO turno (Cliente_ID_Cliente, Servicio, Presupuesto_Estimado, Fecha_Solicitud, Estado)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_c, servicio, float(presupuesto), fecha_hoy, 'Pendiente'))
            DB.commit()
            cursor.close()
            flash("Turno solicitado con éxito. Nos comunicaremos a la brevedad.", "success")
            return redirect(url_for('auth.inicio'))
        except Exception as e:
            flash(f"Error al solicitar turno: {e}", "danger")
            return render_template('solicitar_turno.html')
            
    return render_template('solicitar_turno.html')
