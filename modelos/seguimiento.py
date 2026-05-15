from config.database import DB
import datetime

class Seguimiento:
    @staticmethod
    def registrar_hito(id_orden, estado, comentario):
        cursor = DB.cursor()
        fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sql = """INSERT INTO Seguimiento_Estados 
                 (Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion, Orden_Trabajo_ID_OT) 
                 VALUES (%s, %s, %s, %s)"""
        val = (estado, comentario, fecha, id_orden)
        cursor.execute(sql, val)
        DB.commit()
        cursor.close()