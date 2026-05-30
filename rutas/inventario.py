from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from modelos.inventario import Inventario

bp_inventario = Blueprint('inventario', __name__)

@bp_inventario.route('/inventario', methods=['GET', 'POST'])
def inventario():
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('auth.inicio'))
    if request.method == 'POST':
        t = request.form.get('tipo')
        d = request.form.get('descripcion')
        p = float(request.form.get('precio') or 0)
        s = int(request.form.get('stock') or 0)
        sm = int(request.form.get('stock_minimo') or 0)
        
        # validaciones basicas
        if t not in ('Repuesto_Fisico', 'Servicio_ManoObra'):
            flash("Tipo de ítem inválido.", "danger")
            return redirect(url_for('inventario.inventario'))
        if not d or "<" in d or ">" in d:
            flash("La descripción contiene caracteres inválidos.", "danger")
            return redirect(url_for('inventario.inventario'))
        if p < 0 or s < 0 or sm < 0:
            flash("Precio y stock no pueden ser negativos.", "danger")
            return redirect(url_for('inventario.inventario'))

        Inventario(t, d, p, s, sm, "").registrar()
        flash("Ítem agregado al catálogo.", "success")
    return render_template('inventario.html', items=Inventario.listar_todo())

@bp_inventario.route('/editar_item/<int:id_item>', methods=['POST'])
def editar_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('auth.inicio'))
    d = request.form.get('descripcion')
    p = float(request.form.get('precio') or 0)
    s = int(request.form.get('stock') or 0)
    sm = int(request.form.get('stock_minimo') or 0)
    if Inventario.actualizar(id_item, d, p, s, sm):
        flash("Ítem actualizado exitosamente.", "success")
    else:
        flash("Error al actualizar el ítem.", "danger")
    return redirect(url_for('inventario.inventario'))

@bp_inventario.route('/eliminar_item/<int:id_item>', methods=['POST'])
def eliminar_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return redirect(url_for('auth.inicio'))
    try:
        Inventario.eliminar(id_item)
        flash("Producto eliminado.", "success")
    except Exception:
        flash("No se puede eliminar: el ítem está vinculado a órdenes históricas.", "danger")
    return redirect(url_for('inventario.inventario'))
