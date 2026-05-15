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

app = Flask(__name__)
app.secret_key = "sgol_it_key_2024_university_project"

# ==========================================
# 🔐 SEGURIDAD Y ACCESO
# ==========================================

@app.route('/')
def inicio():
    if 'usuario_id' in session: return redirect(url_for('dashboard'))
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
    if 'usuario_id' not in session: return redirect(url_for('inicio'))
    
    # Contador de equipos listos para la Recepcionista
    listos_count = 0
    if session['rol_id'] == 2:
        cursor = DB.cursor()
        cursor.execute("SELECT COUNT(*) FROM orden_trabajo WHERE Estado_General = 'Listo para Entregar'")
        listos_count = cursor.fetchone()[0]
        cursor.close()
        
    return render_template('dashboard.html', listos_entrega=listos_count)

# ==========================================
# 👨‍💼 MÓDULO ADMINISTRADOR (ROL 1)
# ==========================================

@app.route('/gestion_personal', methods=['GET', 'POST'])
def gestion_personal():
    if 'usuario_id' not in session or session['rol_id'] != 1: return redirect(url_for('inicio'))
    if request.method == 'POST':
        n, u, p, r = request.form.get('nombre'), request.form.get('usuario'), request.form.get('password'), request.form.get('rol_id')
        try:
            cursor = DB.cursor()
            cursor.execute("INSERT INTO empleado (Nombre_Completo, Usuario_Login, Password_Hash) VALUES (%s,%s,%s)", (n,u,p))
            id_e = cursor.lastrowid
            cursor.execute("INSERT INTO legajo_empleado (Empleado_ID_Empleado, Roles_ID_Rol, Fecha_Ingreso) VALUES (%s,%s,%s)", (id_e, r, datetime.datetime.now().strftime('%Y-%m-%d')))
            DB.commit(); cursor.close()
            flash("Empleado registrado exitosamente.", "success")
        except Exception as e: flash(f"Error: {e}", "danger")
    
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT e.ID_Empleado as id, e.Nombre_Completo as nombre, e.Usuario_Login as usuario, r.Nombre_Rol as rol 
                      FROM empleado e JOIN legajo_empleado l ON e.ID_Empleado = l.Empleado_ID_Empleado 
                      JOIN roles r ON l.Roles_ID_Rol = r.ID_Rol""")
    empleados = cursor.fetchall(); cursor.close()
    return render_template('gestion_personal.html', empleados=empleados)

@app.route('/eliminar_empleado/<int:id_emp>', methods=['POST'])
def eliminar_empleado(id_emp):
    if 'usuario_id' not in session or session['rol_id'] != 1: return redirect(url_for('inicio'))
    if id_emp == session['usuario_id']:
        flash("No puedes eliminar tu propia cuenta.", "danger")
    else:
        cursor = DB.cursor()
        cursor.execute("DELETE FROM legajo_empleado WHERE Empleado_ID_Empleado = %s", (id_emp,))
        cursor.execute("DELETE FROM empleado WHERE ID_Empleado = %s", (id_emp,))
        DB.commit(); cursor.close()
        flash("Empleado eliminado del sistema.", "success")
    return redirect(url_for('gestion_personal'))

@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    if 'usuario_id' not in session or session['rol_id'] != 1: return redirect(url_for('inicio'))
    if request.method == 'POST':
        t, d, p = request.form.get('tipo'), request.form.get('descripcion'), float(request.form.get('precio'))
        s = int(request.form.get('stock') or 0)
        Inventario(t, d, p, s, "").registrar()
        flash("Ítem agregado al catálogo.", "success")
    return render_template('inventario.html', items=Inventario.listar_todo())

@app.route('/eliminar_item/<int:id_item>', methods=['POST'])
def eliminar_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1: return redirect(url_for('inicio'))
    try:
        cursor = DB.cursor()
        cursor.execute("DELETE FROM catalogo_inventario WHERE ID_Item = %s", (id_item,))
        DB.commit(); cursor.close()
        flash("Producto eliminado.", "success")
    except Exception:
        flash("No se puede eliminar: el ítem está vinculado a órdenes históricas.", "danger")
    return redirect(url_for('inventario'))

# ==========================================
# 👩‍💻 MÓDULO RECEPCIÓN (ROL 2)
# ==========================================

@app.route('/ingreso_equipo', methods=['GET', 'POST'])
def ingreso_equipo():
    if 'usuario_id' not in session or session['rol_id'] != 2: return redirect(url_for('inicio'))
    if request.method == 'POST':
        dni, nom, tel, em, pw = request.form.get('dni'), request.form.get('nombre'), request.form.get('telefono'), request.form.get('email'), request.form.get('password_web')
        ns, mod, tip = request.form.get('nro_serie'), request.form.get('modelo'), request.form.get('tipo')
        
        if not dni.isdigit() or not (7 <= len(dni) <= 11):
            flash("Error: El DNI debe ser numérico.", "danger"); return redirect(url_for('ingreso_equipo'))

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
            DB.commit(); cursor.close()
            Seguimiento.registrar_hito(id_o, "Ingresado", "El equipo ingresó al laboratorio para su revisión inicial.")
            flash(f"¡Éxito! Orden #{id_o} generada.", "success")
        except Exception as e: flash(f"Error: {e}", "danger")
        return redirect(url_for('ingreso_equipo'))
    return render_template('ingreso_equipo.html')

@app.route('/presupuestos_pendientes')
def presupuestos_pendientes():
    if 'usuario_id' not in session or session['rol_id'] != 2: return redirect(url_for('inicio'))
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] == 'Esperando Aprobación']
    return render_template('presupuestos_pendientes.html', trabajos=ordenes)

@app.route('/cotizar_orden/<int:id_orden>', methods=['GET', 'POST'])
def cotizar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 2: return redirect(url_for('inicio'))
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
        cursor.close(); return redirect(url_for('presupuestos_pendientes'))

    cursor.execute("""SELECT d.Cantidad, i.Precio_Actual as precio_unit, (d.Cantidad * i.Precio_Actual) as subtotal, i.Descripcion 
                      FROM detalle_orden d JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                      WHERE d.Orden_Trabajo_ID_OT = %s""", (id_orden,))
    detalles = cursor.fetchall()
    cursor.execute("""SELECT ot.ID_OT as id_orden, ot.Diagnostico_Final as diagnostico_final, 
                      CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, ot.ID_OT as codigo
                      FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s""", (id_orden,))
    orden = cursor.fetchone(); cursor.close()
    return render_template('cotizar_orden.html', orden=orden, detalles=detalles, total=total)

@app.route('/entregas_pendientes')
def entregas_pendientes():
    if 'usuario_id' not in session or session['rol_id'] != 2: return redirect(url_for('inicio'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT ot.ID_OT as id_orden, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, p.Monto_Total_Cotizado as costo 
                      FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                      JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto 
                      WHERE ot.Estado_General = 'Listo para Entregar'""")
    listos = cursor.fetchall(); cursor.close()
    return render_template('entregas_pendientes.html', trabajos=listos)

@app.route('/facturar/<int:id_orden>')
def facturar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 2: return redirect(url_for('inicio'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT ot.ID_OT as id_orden, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, p.Monto_Total_Cotizado as costo 
                      FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                      JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto WHERE ot.ID_OT = %s""", (id_orden,))
    orden = cursor.fetchone(); cursor.close()
    return render_template('facturar_orden.html', orden=orden)

@app.route('/procesar_pago/<int:id_orden>', methods=['POST'])
def procesar_pago(id_orden):
    metodo = request.form.get('metodo_pago')
    cursor = DB.cursor()
    cursor.execute("INSERT INTO factura (Fecha_Emision, Metodo_Pago, Orden_Trabajo_ID_OT) VALUES (%s, %s, %s)", (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), metodo, id_orden))
    cursor.execute("UPDATE orden_trabajo SET Estado_General = 'Finalizado' WHERE ID_OT = %s", (id_orden,))
    DB.commit(); cursor.close()
    Seguimiento.registrar_hito(id_orden, "Finalizado", f"Equipo entregado al cliente. Pago registrado vía {metodo}.")
    flash("Orden finalizada y factura generada.", "success"); return redirect(url_for('dashboard'))

# ==========================================
# 🛠️ MÓDULO LABORATORIO (ROL 3)
# ==========================================

@app.route('/laboratorio')
def laboratorio():
    if 'usuario_id' not in session or session['rol_id'] != 3: return redirect(url_for('inicio'))
    ordenes = [o for o in OrdenTrabajo.buscar_pendientes() if o['estado'] in ('Para Revisión', 'En Reparación')]
    return render_template('laboratorio.html', trabajos=ordenes)

@app.route('/gestionar_orden/<int:id_orden>', methods=['GET', 'POST'])
def gestionar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 3: return redirect(url_for('inicio'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT ot.ID_OT as id_orden, ot.Estado_General as estado, 
                      CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo FROM orden_trabajo ot 
                      JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s""", (id_orden,))
    orden = cursor.fetchone()

    if request.method == 'POST':
        if orden['estado'] == 'Para Revisión':
            diag = request.form.get('diagnostico')
            cursor.execute("UPDATE orden_trabajo SET Estado_General = 'Esperando Aprobación', Diagnostico_Final = %s WHERE ID_OT = %s", (diag, id_orden))
            Seguimiento.registrar_hito(id_orden, "Diagnóstico Listo", diag)
        elif orden['estado'] == 'En Reparación':
            t, b, o = request.form.get('temperaturas'), request.form.get('benchmark'), request.form.get('observaciones')
            try:
                ControlCalidad(id_orden, session['usuario_id'], t, b, o).registrar()
                cursor.execute("UPDATE orden_trabajo SET Estado_General = 'Listo para Entregar' WHERE ID_OT = %s", (id_orden,))
                Seguimiento.registrar_hito(id_orden, "Listo para Entregar", "Control QA aprobado satisfactoriamente.")
                flash("Control de calidad aprobado.", "success")
            except Exception as e: flash(f"Error en QA: {e}", "danger")
        DB.commit(); cursor.close(); return redirect(url_for('laboratorio'))

    cursor.execute("""SELECT d.Catalogo_Inventario_ID_Item as id_item, d.Cantidad, (d.Cantidad * i.Precio_Actual) as subtotal, i.Descripcion 
                      FROM detalle_orden d JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                      WHERE d.Orden_Trabajo_ID_OT = %s""", (id_orden,))
    detalles = cursor.fetchall(); cursor.close()
    return render_template('gestionar_orden.html', orden=orden, inventario=Inventario.listar_todo(), detalles=detalles)

@app.route('/agregar_repuesto/<int:id_orden>', methods=['POST'])
def agregar_repuesto(id_orden):
    id_i, cant = request.form.get('id_item'), int(request.form.get('cantidad'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("SELECT Precio_Actual, Stock_Disponible, Tipo_Item FROM catalogo_inventario WHERE ID_Item = %s", (id_i,))
    it = cursor.fetchone()
    if it and (it['Tipo_Item'] != 'Repuesto' or cant <= it['Stock_Disponible']):
        cursor.execute("INSERT INTO detalle_orden (Cantidad, Precio_Unitario_Congelado, Orden_Trabajo_ID_OT, Catalogo_Inventario_ID_Item) VALUES (%s,%s,%s,%s)", (cant, it['Precio_Actual'], id_orden, id_i))
        DB.commit(); flash("Ítem añadido.", "info")
    else: flash("Error: Stock insuficiente.", "danger")
    cursor.close(); return redirect(url_for('gestionar_orden', id_orden=id_orden))

@app.route('/eliminar_repuesto_ot/<int:id_orden>/<int:id_item>', methods=['POST'])
def eliminar_repuesto_ot(id_orden, id_item):
    cursor = DB.cursor()
    cursor.execute("DELETE FROM detalle_orden WHERE Orden_Trabajo_ID_OT = %s AND Catalogo_Inventario_ID_Item = %s", (id_orden, id_item))
    DB.commit(); cursor.close(); flash("Ítem removido.", "success")
    return redirect(url_for('gestionar_orden', id_orden=id_orden))

# ==========================================
# 🌐 PORTAL CLIENTE (PÚBLICO)
# ==========================================

@app.route('/tracking', methods=['GET', 'POST'])
def tracking_login():
    if request.method == 'POST':
        dni, pw = request.form.get('dni'), request.form.get('password_web')
        cursor = DB.cursor(dictionary=True)
        cursor.execute("SELECT ID_Cliente, Nombre_Completo FROM cliente WHERE DNI_CUIL = %s AND Password_web = %s", (dni, pw))
        cl = cursor.fetchone()
        if cl: session.update({'cliente_id': cl['ID_Cliente'], 'cliente_nombre': cl['Nombre_Completo']}); return redirect(url_for('portal_cliente'))
        flash("Datos incorrectos.", "danger")
    return render_template('tracking.html')

@app.route('/portal_cliente')
def portal_cliente():
    if 'cliente_id' not in session: return redirect(url_for('tracking_login'))
    cursor = DB.cursor(dictionary=True)
    cursor.execute("""SELECT ot.ID_OT as id_orden, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, ot.Estado_General as estado, p.Monto_Total_Cotizado as costo 
                      FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo 
                      LEFT JOIN presupuesto p ON ot.Presupuesto_ID_Presupuesto = p.ID_Presupuesto WHERE e.Cliente_ID_Cliente = %s""", (session['cliente_id'],))
    ord = cursor.fetchall()
    cursor.execute("""SELECT d.Orden_Trabajo_ID_OT as id_orden, d.Cantidad, (d.Cantidad * d.Precio_Unitario_Congelado) as subtotal, i.Descripcion FROM detalle_orden d 
                      JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item 
                      JOIN orden_trabajo ot ON d.Orden_Trabajo_ID_OT = ot.ID_OT 
                      JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE e.Cliente_ID_Cliente = %s""", (session['cliente_id'],))
    det = cursor.fetchall()
    cursor.execute("SELECT * FROM seguimiento_estados ORDER BY Fecha_Actualizacion DESC")
    hit = cursor.fetchall(); cursor.close()
    return render_template('portal_cliente.html', ordenes=ord, hitos=hit, detalles=det)

@app.route('/responder_presupuesto/<int:id_orden>/<respuesta>')
def responder_presupuesto(id_orden, respuesta):
    est = "En Reparación" if respuesta == 'aprobar' else "Rechazado"
    cursor = DB.cursor(dictionary=True)
    if respuesta == 'aprobar':
        cursor.execute("SELECT Catalogo_Inventario_ID_Item, Cantidad FROM detalle_orden WHERE Orden_Trabajo_ID_OT = %s", (id_orden,))
        for it in cursor.fetchall():
            cursor.execute("UPDATE catalogo_inventario SET Stock_Disponible = Stock_Disponible - %s WHERE ID_Item = %s AND Tipo_Item = 'Repuesto'", (it['Cantidad'], it['Catalogo_Inventario_ID_Item']))
    cursor.execute("UPDATE orden_trabajo SET Estado_General = %s WHERE ID_OT = %s", (est, id_orden))
    DB.commit(); Seguimiento.registrar_hito(id_orden, est, f"El cliente {respuesta}ó el presupuesto."); cursor.close()
    return redirect(url_for('portal_cliente'))

if __name__ == '__main__':
    app.run(debug=True)