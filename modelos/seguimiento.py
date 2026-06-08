from config.database import DB
import datetime

class Seguimiento:
    @staticmethod
    def registrar_hito(id_orden, estado, comentario):
        cursor = DB.cursor()
        try:
            fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sql = """INSERT INTO Seguimiento_Estados 
                     (Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion, Orden_Trabajo_ID_OT) 
                     VALUES (%s, %s, %s, %s)"""
            val = (estado, comentario, fecha, id_orden)
            cursor.execute(sql, val)
            DB.commit()
        except Exception as e:
            print(f"Error al registrar hito de seguimiento: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
        finally:
            cursor.close()

    @staticmethod
    def listar_todos():
        """Retorna todos los hitos registrados en orden cronológico descendente."""
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT ID_Seguimiento, Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion, Orden_Trabajo_ID_OT FROM seguimiento_estados ORDER BY Fecha_Actualizacion DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al listar seguimientos: {e}")
            return []
        finally:
            cursor.close()

    @staticmethod
    def buscar_por_orden(id_orden):
        """Retorna los hitos de seguimiento para una orden específica."""
        cursor = DB.cursor(dictionary=True)
        try:
            cursor.execute("SELECT Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion FROM seguimiento_estados WHERE Orden_Trabajo_ID_OT = %s ORDER BY Fecha_Actualizacion DESC", (id_orden,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al buscar seguimientos por orden: {e}")
            return []
        finally:
            cursor.close()