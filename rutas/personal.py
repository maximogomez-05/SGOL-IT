from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import re
from modelos.empleado import Empleado

bp_personal = Blueprint('personal', __name__)

@bp_personal.route('/gestion_personal', methods=['GET', 'POST'])
def gestion_personal():
    if session.get('rol_id') is None or int(session.get('rol_id', 0) or 0) != 1: 
        return redirect(url_for('auth.inicio'))
    if request.method == 'POST':
        n = request.form.get('nombre')
        u = request.form.get('usuario')
        p = request.form.get('password')
        r = request.form.get('rol_id')
        
        # validaciones basicas
        if not n or not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", n):
            flash("El nombre solo debe tener letras y espacios.", "danger")
            return redirect(url_for('personal.gestion_personal'))
        if not u or not re.match(r"^[a-zA-Z0-9_]+$", u):
            flash("El usuario solo debe tener caracteres alfanuméricos o guión bajo.", "danger")
            return redirect(url_for('personal.gestion_personal'))
        if not p or len(p) < 4:
            flash("La clave debe tener mínimo 4 caracteres.", "danger")
            return redirect(url_for('personal.gestion_personal'))
        if not r or r not in ('1', '2', '3'):
            flash("Rol inválido.", "danger")
            return redirect(url_for('personal.gestion_personal'))

        try:
            Empleado(n, u, p, r).registrar()
            flash("Empleado registrado exitosamente.", "success")
        except Exception as e: 
            flash(f"Error: {e}", "danger")
    
    empleados = Empleado.listar_todos()
    return render_template('gestion_personal.html', empleados=empleados)

@bp_personal.route('/toggle_empleado/<int:id_emp>/<accion>', methods=['POST'])
def toggle_empleado(id_emp, accion):
    if 'usuario_id' not in session or int(session.get('rol_id', 0) or 0) != 1: 
        return redirect(url_for('auth.inicio'))
    if id_emp == session['usuario_id']:
        flash("No puedes modificar tu propia cuenta.", "danger")
    else:
        if accion == 'desactivar':
            if Empleado.eliminar(id_emp):
                flash("Empleado desactivado exitosamente.", "success")
            else:
                flash("Error al desactivar el empleado.", "danger")
        elif accion == 'activar':
            if Empleado.activar(id_emp):
                flash("Empleado reactivado exitosamente.", "success")
            else:
                flash("Error al activar el empleado.", "danger")
    return redirect(url_for('personal.gestion_personal'))
