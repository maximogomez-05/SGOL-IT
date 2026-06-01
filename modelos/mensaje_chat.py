from config.database import DB
import datetime

class MensajeChat:
    def __init__(self, orden_trabajo_id, remitente_tipo, mensaje, empleado_id=None, cliente_id=None, leido=0, fecha_envio=None, id_mensaje=None):
        self.id_mensaje = id_mensaje
        self.orden_trabajo_id = orden_trabajo_id
        self.remitente_tipo = remitente_tipo # 'cliente' o 'empleado'
        self.empleado_id = empleado_id
        self.cliente_id = cliente_id
        self.mensaje = mensaje
        self.fecha_envio = fecha_envio if fecha_envio else datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.leido = leido
        self._asegurar_tabla_chat()

    def _asegurar_tabla_chat(self):
        # crea la tabla de chat si no existe en la base de datos
        cursor = DB.cursor()
        try:
            sql = """
            CREATE TABLE IF NOT EXISTS mensaje_chat (
                id_mensaje INT AUTO_INCREMENT PRIMARY KEY,
                orden_trabajo_id INT NOT NULL,
                remitente_tipo VARCHAR(10) NOT NULL,
                empleado_id INT NULL,
                cliente_id INT NULL,
                mensaje TEXT NOT NULL,
                fecha_envio DATETIME NOT NULL,
                leido TINYINT DEFAULT 0,
                FOREIGN KEY (orden_trabajo_id) REFERENCES orden_trabajo(ID_OT) ON DELETE CASCADE,
                FOREIGN KEY (empleado_id) REFERENCES empleado(ID_Empleado) ON DELETE SET NULL,
                FOREIGN KEY (cliente_id) REFERENCES cliente(ID_Cliente) ON DELETE SET NULL
            )
            """
            cursor.execute(sql)
            DB.commit()
        except Exception as e:
            print(f"error al crear tabla mensaje_chat: {e}")
        finally:
            cursor.close()

    def registrar(self):
        # guarda un mensaje de chat en la base de datos
        cursor = DB.cursor()
        try:
            sql = """INSERT INTO mensaje_chat 
                     (orden_trabajo_id, remitente_tipo, empleado_id, cliente_id, mensaje, fecha_envio, leido) 
                     VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            val = (self.orden_trabajo_id, self.remitente_tipo, self.empleado_id, self.cliente_id, self.mensaje, self.fecha_envio, self.leido)
            cursor.execute(sql, val)
            DB.commit()
            self.id_mensaje = cursor.lastrowid
            return self.id_mensaje
        except Exception as e:
            print(f"error al registrar mensaje de chat: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return None
        finally:
            cursor.close()

    @staticmethod
    def listar_por_orden(id_orden):
        # lista todos los mensajes de una orden de trabajo con nombres legibles
        cursor = DB.cursor(dictionary=True)
        try:
            sql = """
                SELECT mc.id_mensaje, mc.orden_trabajo_id, mc.remitente_tipo, mc.mensaje, 
                       mc.fecha_envio, mc.leido,
                       COALESCE(e.Nombre_Completo, 'Soporte') as empleado_nombre,
                       COALESCE(c.Nombre_Completo, 'Cliente') as cliente_nombre
                FROM mensaje_chat mc
                LEFT JOIN empleado e ON mc.empleado_id = e.ID_Empleado
                LEFT JOIN cliente c ON mc.cliente_id = c.ID_Cliente
                WHERE mc.orden_trabajo_id = %s
                ORDER BY mc.fecha_envio ASC
            """
            cursor.execute(sql, (id_orden,))
            res = cursor.fetchall()
            for r in res:
                if r.get('fecha_envio'):
                    r['fecha_envio'] = r['fecha_envio'].strftime('%Y-%m-%d %H:%M:%S')
            return res
        except Exception as e:
            print(f"error al listar mensajes por orden: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def marcar_leido_por_orden(id_orden, para_remitente):
        # marca como leidos los mensajes que corresponden a un destinatario
        cursor = DB.cursor()
        try:
            sql = "UPDATE mensaje_chat SET leido = 1 WHERE orden_trabajo_id = %s AND remitente_tipo != %s"
            cursor.execute(sql, (id_orden, para_remitente))
            DB.commit()
            return True
        except Exception as e:
            print(f"error al marcar mensajes leidos: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()
