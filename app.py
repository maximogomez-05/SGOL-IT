from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import datetime
from auth.login import Autenticacion  

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
    auth = Autenticacion()
    res = auth.iniciar_sesion(user, pw)
    if res:
        session['usuario_id'] = res['id']
        session['nombre'] = res['nombre']
        session['rol_id'] = res['rol_id']
        session['nombre_rol'] = res['nombre_rol']
        return redirect(url_for('dashboard'))
    return render_template('login.html', error="Credenciales inválidas. Intente nuevamente.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

# --- DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('inicio'))
    return render_template('dashboard.html')


@app.route('/gestion_personal', methods=['GET', 'POST'])
def gestion_personal():
    if 'usuario_id' not in session or session['rol_id'] != 1:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        usuario = request.form.get('usuario')
        password = request.form.get('password')
        rol_id = request.form.get('rol_id')
        try:
            conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO empleado (Nombre_Completo, Usuario_Login, Password_Hash) VALUES (%s, %s, %s)", (nombre, usuario, password))
            id_emp = cursor.lastrowid
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d')
            cursor.execute("INSERT INTO legajo_empleado (Empleado_ID_Empleado, Roles_ID_Rol, Fecha_Ingreso) VALUES (%s, %s, %s)", (id_emp, rol_id, fecha_actual))
            conexion.commit()
            conexion.close()
            flash("Empleado registrado exitosamente.", "success")
        except Exception as e:
            flash(f"Error al registrar: {e}", "danger")
        return redirect(url_for('gestion_personal'))

    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT e.ID_Empleado as id, e.Nombre_Completo as nombre, e.Usuario_Login as usuario, l.Roles_ID_Rol as rol_id FROM empleado e LEFT JOIN legajo_empleado l ON e.ID_Empleado = l.Empleado_ID_Empleado")
        lista_empleados = cursor.fetchall()
        conexion.close()
    except Exception:
        lista_empleados = []
    return render_template('gestion_personal.html', empleados=lista_empleados)

@app.route('/eliminar_empleado/<int:id_emp>', methods=['POST'])
def eliminar_empleado(id_emp):
    if 'usuario_id' not in session or session['rol_id'] != 1:
        return redirect(url_for('inicio'))
    
    # Evitar que el admin se borre a sí mismo
    if id_emp == session['usuario_id']:
        flash("No puedes eliminar tu propia cuenta mientras estás logueado.", "danger")
        return redirect(url_for('gestion_personal'))

    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor()
        # Primero borramos su legajo (por la relación de la BD)
        cursor.execute("DELETE FROM legajo_empleado WHERE Empleado_ID_Empleado = %s", (id_emp,))
        # Luego borramos al empleado
        cursor.execute("DELETE FROM empleado WHERE ID_Empleado = %s", (id_emp,))
        conexion.commit()
        conexion.close()
        flash("Empleado eliminado correctamente.", "success")
    except Exception as e:
        flash("El empleado no puede ser eliminado porque tiene un historial de operaciones en el sistema.", "danger")
    return redirect(url_for('gestion_personal'))


@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    if 'usuario_id' not in session or session['rol_id'] != 1:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        desc = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
        stock = int(request.form.get('stock')) if request.form.get('stock') else 0
        try:
            conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO catalogo_inventario (Tipo_Item, Descripcion, Precio_Actual, Stock_Disponible) VALUES (%s, %s, %s, %s)", (tipo, desc, precio, stock))
            conexion.commit()
            conexion.close()
            flash("Ítem agregado exitosamente al catálogo.", "success")
        except Exception as e:
            flash(f"Error BD: {e}", "danger")
        return redirect(url_for('inventario'))

    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT ID_Item as id, Descripcion as descripcion, Tipo_Item as tipo_item, Precio_Actual as precio, Stock_Disponible as stock FROM catalogo_inventario")
        items = cursor.fetchall()
        conexion.close()
    except Exception:
        items = []
    return render_template('inventario.html', items=items)

@app.route('/eliminar_item/<int:id_item>', methods=['POST'])
def eliminar_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1:
        return redirect(url_for('inicio'))
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM catalogo_inventario WHERE ID_Item = %s", (id_item,))
        conexion.commit()
        conexion.close()
        flash("Producto eliminado correctamente.", "success")
    except Exception as e:
        flash("No se puede borrar este producto porque ya fue utilizado en presupuestos u órdenes anteriores.", "danger")
    return redirect(url_for('inventario'))

# --- RECEPCIÓN ---
@app.route('/ingreso_equipo', methods=['GET', 'POST'])
def ingreso_equipo():
    if 'usuario_id' not in session or session['rol_id'] != 2:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        dni = request.form.get('dni')
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')
        pass_web = request.form.get('password_web')
        nro_serie = request.form.get('nro_serie')
        modelo = request.form.get('modelo')
        tipo = request.form.get('tipo')

        try:
            conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT ID_Cliente FROM cliente WHERE DNI_CUIL = %s", (dni,))
            cliente = cursor.fetchone()
            if cliente:
                id_cliente = cliente['ID_Cliente']
            else:
                cursor.execute("INSERT INTO cliente (DNI_CUIL, Nombre_Completo, Email, Telefono, Password_web) VALUES (%s, %s, %s, %s, %s)", (dni, nombre, email, telefono, pass_web))
                id_cliente = cursor.lastrowid
            
            cursor.execute("INSERT INTO equipo (Numero_Serie, Marca_Modelo, Tipo_Dispositivo, Cliente_ID_Cliente) VALUES (%s, %s, %s, %s)", (nro_serie, modelo, tipo, id_cliente))
            id_equipo = cursor.lastrowid
            
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO orden_trabajo (Estado_General, Fecha_Creacion, Equipo_ID_Equipo, Empleado_ID_Empleado, Presupuesto_ID_Presupuesto) VALUES (%s, %s, %s, %s, %s)", ('Para Revisión', fecha_actual, id_equipo, session['usuario_id'], None))
            id_orden = cursor.lastrowid
            conexion.commit()
            conexion.close()
            flash(f"¡Éxito! Orden #{id_orden} generada.", "success")
        except Exception as e:
            flash(f"Error crítico en la base de datos: {e}", "danger")
        return redirect(url_for('ingreso_equipo'))
    return render_template('ingreso_equipo.html')

# --- LABORATORIO ---
@app.route('/laboratorio')
def laboratorio():
    if 'usuario_id' not in session or session['rol_id'] != 3:
        return redirect(url_for('inicio'))
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT ot.ID_OT as id_orden, ot.ID_OT as codigo, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, ot.Estado_General as estado FROM orden_trabajo ot LEFT JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.Estado_General IN ('Para Revisión', 'En Reparación')")
        trabajos = cursor.fetchall()
        conexion.close()
    except: trabajos = []
    return render_template('laboratorio.html', trabajos=trabajos)

@app.route('/gestionar_orden/<int:id_orden>', methods=['GET', 'POST'])
def gestionar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 3:
        return redirect(url_for('inicio'))

    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        
        if request.method == 'POST':
            diagnostico = request.form.get('diagnostico')
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE orden_trabajo SET Estado_General = 'Esperando Aprobación', Diagnostico_Final = %s WHERE ID_OT = %s", (diagnostico, id_orden))
            cursor.execute("INSERT INTO seguimiento_estados (Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion, Orden_Trabajo_ID_OT) VALUES (%s, %s, %s, %s)", ('Esperando Aprobación', diagnostico, fecha_actual, id_orden))
            conexion.commit()
            conexion.close()
            flash("Diagnóstico enviado correctamente.", "success")
            return redirect(url_for('laboratorio'))
            
        cursor.execute("SELECT ot.ID_OT as id_orden, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo FROM orden_trabajo ot LEFT JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s", (id_orden,))
        orden_actual = cursor.fetchone()

        cursor.execute("SELECT d.Cantidad as cantidad, d.Precio_Unitario_Congelado as subtotal, i.Descripcion as descripcion FROM detalle_orden d JOIN catalogo_inventario i ON d.Catalogo_Inventario_ID_Item = i.ID_Item WHERE d.Orden_Trabajo_ID_OT = %s", (id_orden,))
        detalles = cursor.fetchall()

        cursor.execute("SELECT ID_Item as id, Descripcion as descripcion, Precio_Actual as precio, Stock_Disponible as stock FROM catalogo_inventario")
        inventario = cursor.fetchall()
        
        conexion.close()
        return render_template('gestionar_orden.html', orden=orden_actual, detalles=detalles, inventario=inventario)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/agregar_repuesto/<int:id_orden>', methods=['POST'])
def agregar_repuesto(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 3:
        return redirect(url_for('inicio'))
    
    id_item = request.form.get('id_item')
    cantidad = int(request.form.get('cantidad'))
    
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT Precio_Actual FROM catalogo_inventario WHERE ID_Item = %s", (id_item,))
        item = cursor.fetchone()
        
        if item:
            precio_final = float(item['Precio_Actual']) * cantidad
            cursor.execute("INSERT INTO detalle_orden (Cantidad, Precio_Unitario_Congelado, Orden_Trabajo_ID_OT, Catalogo_Inventario_ID_Item) VALUES (%s, %s, %s, %s)", (cantidad, precio_final, id_orden, id_item))
            conexion.commit()
            flash("Ítem añadido a la orden.", "info")
        
        conexion.close()
    except Exception as e:
        flash(f"Error al añadir repuesto: {e}", "danger")
        
    return redirect(url_for('gestionar_orden', id_orden=id_orden))

# --- PRESUPUESTOS Y COTIZACIÓN ---
@app.route('/presupuestos_pendientes')
def presupuestos_pendientes():
    if 'usuario_id' not in session or session['rol_id'] != 2:
        return redirect(url_for('inicio'))
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT ot.ID_OT as id_orden, ot.ID_OT as codigo, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, ot.Estado_General as estado FROM orden_trabajo ot LEFT JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.Estado_General = 'Esperando Aprobación'")
        trabajos = cursor.fetchall()
        conexion.close()
    except: trabajos = []
    return render_template('presupuestos_pendientes.html', trabajos=trabajos)

@app.route('/cotizar_orden/<int:id_orden>', methods=['GET', 'POST'])
def cotizar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 2:
        return redirect(url_for('inicio'))
    try:
        conexion = mysql.connector.connect(host="localhost", user="root", password="", database="sgol_it")
        cursor = conexion.cursor(dictionary=True)
        if request.method == 'POST':
            monto = request.form.get('monto')
            fecha_actual = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT Equipo_ID_Equipo FROM orden_trabajo WHERE ID_OT = %s", (id_orden,))
            id_equipo = cursor.fetchone()['Equipo_ID_Equipo']
            cursor.execute("INSERT INTO presupuesto (Monto_Total_Cotizado, Estado_Presupuesto, Comprobante_Impreso, Presupuesto_Preliminar_Web, Equipo_ID_Equipo) VALUES (%s, %s, %s, %s, %s)", (monto, 'Pendiente', 'No', monto, id_equipo))
            id_presupuesto = cursor.lastrowid
            cursor.execute("UPDATE orden_trabajo SET Estado_General = 'Esperando Respuesta', Presupuesto_ID_Presupuesto = %s WHERE ID_OT = %s", (id_presupuesto, id_orden))
            cursor.execute("INSERT INTO seguimiento_estados (Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion, Orden_Trabajo_ID_OT) VALUES (%s, %s, %s, %s)", ('Esperando Respuesta', f'Cotización: ${monto}', fecha_actual, id_orden))
            conexion.commit()
            conexion.close()
            flash("Presupuesto enviado.", "success")
            return redirect(url_for('presupuestos_pendientes'))

        cursor.execute("SELECT ot.ID_OT as id_orden, ot.ID_OT as codigo, ot.Diagnostico_Final as diagnostico, CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo FROM orden_trabajo ot LEFT JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s", (id_orden,))
        orden_actual = cursor.fetchone()
        conexion.close()
        return render_template('cotizar_orden.html', orden=orden_actual)
    except: return "Error", 500

if __name__ == '__main__':
    app.run(debug=True)