from config.database import ConexionBD
import datetime

class Seguimiento:
    @staticmethod
    def registrar_hito(id_ot, estado, comentario):
        """Guarda un avance en la linea de tiempo (Tabla Seguimiento_Estados)."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = """INSERT INTO Seguimiento_Estados 
                         (Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion, Orden_Trabajo_ID_OT) 
                         VALUES (%s, %s, %s, %s)"""
                cursor.execute(sql, (estado, comentario, datetime.datetime.now(), id_ot))
                conexion.commit()
            finally:
                cursor.close()
                db.desconectar()

    @staticmethod
    def consultar_tracking(codigo_web):
        """Busca toda la informacion de una OT para el cliente."""
        db = ConexionBD()
        conexion = db.conectar()
        if conexion:
            try:
                cursor = conexion.cursor()
              
                sql = """
                    SELECT ot.ID_OT, ot.Estado_General, e.Marca_Modelo, e.Numero_Serie
                    FROM Orden_Trabajo ot
                    JOIN Equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo
                    WHERE ot.Codigo_Tracking_Web = %s
                """
                cursor.execute(sql, (codigo_web,))
                info_ot = cursor.fetchone()
                
                if info_ot:
                    # Traemos la linea de tiempo
                    cursor.execute("""
                        SELECT Estado_Alcanzado, Comentario_Frontal, Fecha_Actualizacion 
                        FROM Seguimiento_Estados 
                        WHERE Orden_Trabajo_ID_OT = %s 
                        ORDER BY Fecha_Actualizacion DESC
                    """, (info_ot[0],))
                    historial = cursor.fetchall()
                    
                    return {"info": info_ot, "historial": historial}
                return None
            finally:
                cursor.close()
                db.desconectar()
        return None