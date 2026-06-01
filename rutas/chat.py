from flask import Blueprint, request, jsonify, session
from modelos.mensaje_chat import MensajeChat

bp_chat = Blueprint('chat', __name__)

@bp_chat.route('/chat/<int:id_orden>', methods=['GET'])
def obtener_mensajes(id_orden):
    # valida que haya una sesion iniciada
    if 'usuario_id' not in session and 'cliente_id' not in session:
        return jsonify({"error": "No autorizado"}), 401
    
    # determina quien lee el mensaje para marcarlo como leido
    if 'cliente_id' in session:
        # si es cliente, marcar como leido lo enviado por empleados
        MensajeChat.marcar_leido_por_orden(id_orden, 'cliente')
    else:
        # si es empleado, marcar como leido lo enviado por clientes
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

    if not texto:
        return jsonify({"error": "El mensaje no puede estar vacio"}), 400

    # construir el mensaje segun quien envie
    if 'cliente_id' in session:
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
