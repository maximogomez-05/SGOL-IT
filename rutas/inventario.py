from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from modelos.inventario import Inventario
from servicios.scraper import ScraperPrecios

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
        
        url = request.form.get('url_referencia', '')
        
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
        if t == 'Repuesto_Fisico' and sm < 10:
            flash("El stock mínimo crítico no puede ser menor a 10 para repuestos físicos.", "danger")
            return redirect(url_for('inventario.inventario'))

        Inventario(t, d, p, s, sm, url).registrar()
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
    url = request.form.get('url_referencia', '')
    
    item = Inventario.buscar_por_id(id_item)
    if not item:
        flash("Ítem no encontrado.", "danger")
        return redirect(url_for('inventario.inventario'))
        
    if item['tipo_item'] == 'Repuesto_Fisico' and sm < 10:
        flash("El stock mínimo crítico no puede ser menor a 10 para repuestos físicos.", "danger")
        return redirect(url_for('inventario.inventario'))
        
    if Inventario.actualizar(id_item, d, p, s, sm, url):
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

@bp_inventario.route('/inventario/scrapear/<int:id_item>', methods=['GET'])
def scrapear_item(id_item):
    if 'usuario_id' not in session or session['rol_id'] != 1: 
        return jsonify({"error": "No autorizado"}), 401
    
    item = Inventario.buscar_por_id(id_item)
    if not item:
        return jsonify({"error": "Ítem no encontrado"}), 404
        
    url = item.get('url_referencia')
    precio_cat = float(item.get('precio') or 0)
    descripcion = item.get('descripcion')
    
    # Ejecutar scraping
    precio_mercado, final_url = ScraperPrecios.obtener_precio_en_vivo(url, precio_cat, descripcion)
    
    if precio_mercado is None:
        return jsonify({
            "status": "error",
            "message": "No se pudo obtener el precio online"
        })
    
    # Calcular comparaciones: (cat - mercado) / mercado * 100
    diff_monto = precio_cat - precio_mercado
    diff_pct = (diff_monto / precio_mercado * 100) if precio_mercado > 0 else 0
    
    if diff_pct > 10:
        comparativa = "Alto"
    elif diff_pct < -10:
        comparativa = "Bajo"
    else:
        comparativa = "Competitivo"
        
    return jsonify({
        "status": "ok",
        "precio_mercado": precio_mercado,
        "diferencia_monto": round(abs(diff_monto), 2),
        "diferencia_porcentaje": round(diff_pct, 1),
        "comparativa": comparativa,
        "url_referencia": final_url
    })
