from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

# import de los blueprints
from rutas.auth import bp_auth
from rutas.dashboard import bp_dashboard
from rutas.ordenes import bp_ordenes
from rutas.facturacion import bp_facturacion
from rutas.personal import bp_personal
from rutas.inventario import bp_inventario
from rutas.chat import bp_chat

app = Flask(__name__)

# clave secreta de la sesion
app.secret_key = "sgolit_2026_secure_key"

# configs para subir fotos de los equipos
UPLOAD_FOLDER = 'static/uploads/equipos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# registro de blueprints
app.register_blueprint(bp_auth)
app.register_blueprint(bp_dashboard)
app.register_blueprint(bp_ordenes)
app.register_blueprint(bp_facturacion)
app.register_blueprint(bp_personal)
app.register_blueprint(bp_inventario)
app.register_blueprint(bp_chat)

# crea la carpeta de fotos si no existe
os.makedirs(os.path.join(app.root_path, UPLOAD_FOLDER), exist_ok=True)

# migraciones de base de datos al iniciar
def ejecutar_migraciones():
    from config.database import DB
    cursor = DB.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM cliente LIKE 'Password_Cambiada'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE cliente ADD COLUMN Password_Cambiada TINYINT(1) DEFAULT 0")
            DB.commit()
            print("[MIGRACIÓN] Columna Password_Cambiada agregada a tabla cliente.")
    except Exception as e:
        print(f"[MIGRACIÓN] Error: {e}")
    finally:
        cursor.close()

with app.app_context():
    ejecutar_migraciones()

@app.before_request
def check_forced_password_change():
    # rutas libres al cambiar password
    allowed_routes = [
        'auth.cambiar_password_obligatorio', 
        'auth.logout', 
        'auth.logout_cliente', 
        'auth.inicio', 
        'auth.login', 
        'auth.tracking_login', 
        'static'
    ]
    if request.endpoint and request.endpoint not in allowed_routes:
        if session.get('force_password_change'):
            flash("Debes personalizar tu contraseña antes de continuar.", "warning")
            return redirect(url_for('auth.cambiar_password_obligatorio'))

# error handlers globales
@app.errorhandler(404)
def pagina_no_encontrada(e):
    return render_template('login.html', error="Página no encontrada."), 404

if __name__ == '__main__':
    app.run(debug=True)