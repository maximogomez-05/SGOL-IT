from flask import Flask, render_template, request, redirect, url_for, session, flash
from auth.login import Autenticacion  
from modelos.cliente import Cliente
from modelos.equipo import Equipo
from modelos.orden_trabajo import OrdenTrabajo
from modelos.inventario import Inventario
from modelos.seguimiento import Seguimiento

app = Flask(__name__)
# Clave para encriptar sesiones
app.secret_key = "sgol_it_key_2024_university_project"

# --- RUTAS DE AUTENTICACIÓN ---

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
    else:
        return render_template('login.html', error="Credenciales inválidas. Intente nuevamente.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('inicio'))

# --- RUTA PRINCIPAL: DASHBOARD ---

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('inicio'))
    return render_template('dashboard.html')

# --- RUTAS DE RECEPCIÓN Y PRESUPUESTOS ---

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

        cliente = Cliente.buscar_por_dni(dni)
        id_cliente = cliente['id'] if cliente else Cliente(dni, nombre, email, telefono, pass_web).registrar()

        if id_cliente:
            id_equipo = Equipo(nro_serie, modelo, tipo, id_cliente).registrar()
            ot = OrdenTrabajo(id_equipo, session['usuario_id'], None)
            ot.registrar()
            flash("Equipo ingresado correctamente y derivado a Laboratorio.", "success")
            return redirect(url_for('ingreso_equipo'))

    return render_template('ingreso_equipo.html')

@app.route('/presupuestos_pendientes')
def presupuestos_pendientes():
    # Solo entran los Recepcionistas (rol_id == 2)
    if 'usuario_id' not in session or session['rol_id'] != 2:
        return redirect(url_for('inicio'))
    
    # Buscamos las órdenes pendientes
    ordenes = OrdenTrabajo.buscar_pendientes()
    # Filtramos solo las que el técnico ya diagnosticó
    trabajos = [o for o in ordenes if o['estado'] == 'Esperando Aprobación']
    
    return render_template('presupuestos_pendientes.html', trabajos=trabajos)

# --- RUTAS DE LABORATORIO ---

@app.route('/laboratorio')
def laboratorio():
    if 'usuario_id' not in session or session['rol_id'] != 3:
        return redirect(url_for('inicio'))
    
    ordenes = OrdenTrabajo.buscar_pendientes()
    trabajos = [o for o in ordenes if o['estado'] in ('Para Revisión', 'En Reparación')]
    
    return render_template('laboratorio.html', trabajos=trabajos)

@app.route('/gestionar_orden/<int:id_orden>', methods=['GET', 'POST'])
def gestionar_orden(id_orden):
    if 'usuario_id' not in session or session['rol_id'] != 3:
        return redirect(url_for('inicio'))

    ordenes = OrdenTrabajo.buscar_pendientes()
    orden_actual = next((o for o in ordenes if o['id_orden'] == id_orden), None)

    if not orden_actual:
        return "Orden no encontrada", 404

    if request.method == 'POST':
        diagnostico = request.form.get('diagnostico')
        OrdenTrabajo.actualizar_estado(id_orden, "Esperando Aprobación")
        Seguimiento.registrar_hito(id_orden, "Esperando Aprobación", diagnostico)
        flash("Diagnóstico enviado correctamente a Recepción.", "success")
        return redirect(url_for('laboratorio'))

    return render_template('gestionar_orden.html', orden=orden_actual)

# --- RUTA DE INVENTARIO E REPORTES (Administrador) ---

@app.route('/inventario', methods=['GET', 'POST'])
def inventario():
    # Solo entran los Administradores (rol_id == 1)
    if 'usuario_id' not in session or session['rol_id'] != 1:
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        desc = request.form.get('descripcion')
        precio = request.form.get('precio')
        stock = request.form.get('stock')
        
        # Asumimos stock 0 si es un servicio y no se mandó cantidad
        stock_val = int(stock) if stock else 0
        Inventario(tipo, desc, float(precio), stock_val, "").registrar()
        
        flash("Ítem agregado exitosamente al catálogo.", "success")
        return redirect(url_for('inventario'))

    # Si es GET, listamos todos los items para la tabla
    items = Inventario.listar_todo()
    return render_template('inventario.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)