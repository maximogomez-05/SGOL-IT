from flask import Blueprint, request, jsonify, session
from modelos.mensaje_chat import MensajeChat
from config.database import DB

bp_chat = Blueprint('chat', __name__)

def _cliente_tiene_acceso_a_orden(id_orden, cliente_id):
    """Verifica que la orden pertenezca al cliente logueado."""
    cursor = DB.cursor(dictionary=True)
    try:
        cursor.execute("SELECT e.Cliente_ID_Cliente FROM orden_trabajo ot JOIN equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo WHERE ot.ID_OT = %s", (id_orden,))
        row = cursor.fetchone()
        return row and row['Cliente_ID_Cliente'] == cliente_id
    except Exception:
        return False
    finally:
        cursor.close()

@bp_chat.route('/chat/<int:id_orden>', methods=['GET'])
def obtener_mensajes(id_orden):
    # valida que haya una sesion iniciada
    if 'usuario_id' not in session and 'cliente_id' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    # determinar el rol activo segun parametro 'como' o por defecto
    como = request.args.get('como', '')
    es_cliente = (como == 'cliente' and 'cliente_id' in session) or ('cliente_id' in session and 'usuario_id' not in session)
    
    # si es cliente, validar que la orden le pertenezca
    if es_cliente:
        if not _cliente_tiene_acceso_a_orden(id_orden, session['cliente_id']):
            return jsonify({"error": "No autorizado para esta orden"}), 403
    
    # determina quien lee el mensaje para marcarlo como leido
    if es_cliente:
        MensajeChat.marcar_leido_por_orden(id_orden, 'cliente')
    else:
        MensajeChat.marcar_leido_por_orden(id_orden, 'empleado')

    mensajes = MensajeChat.listar_por_orden(id_orden)
    return jsonify(mensajes)

@bp_chat.route('/chat/<int:id_orden>/enviar', methods=['POST'])
def enviar_mensaje(id_orden):
    # valida que haya una sesion iniciada
    if 'usuario_id' not in session and 'cliente_id' not in session:
        return jsonify({"error": "No autorizado"}), 401

    data = request.get_json() or {}
    texto = data.get('mensaje', '').strip()
    como = data.get('como', '')
    
    # determinar el rol activo segun parametro 'como' o por defecto
    es_cliente = (como == 'cliente' and 'cliente_id' in session) or ('cliente_id' in session and 'usuario_id' not in session)

    # si es cliente, validar que la orden le pertenezca
    if es_cliente:
        if not _cliente_tiene_acceso_a_orden(id_orden, session['cliente_id']):
            return jsonify({"error": "No autorizado para esta orden"}), 403

    if not texto:
        return jsonify({"error": "El mensaje no puede estar vacio"}), 400
        
    if "<" in texto or ">" in texto:
        return jsonify({"error": "El mensaje contiene caracteres no permitidos"}), 400

    # construir el mensaje segun quien envie
    if es_cliente:
        msg = MensajeChat(
            orden_trabajo_id=id_orden,
            remitente_tipo='cliente',
            cliente_id=session['cliente_id'],
            mensaje=texto
        )
    else:
        msg = MensajeChat(
            orden_trabajo_id=id_orden,
            remitente_tipo='empleado',
            empleado_id=session['usuario_id'],
            mensaje=texto
        )

    id_msg = msg.registrar()
    if id_msg:
        return jsonify({"status": "ok", "id_mensaje": id_msg})
    return jsonify({"error": "Error al guardar el mensaje"}), 500
