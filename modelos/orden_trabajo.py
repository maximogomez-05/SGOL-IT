from config.database import DB
import datetime

class OrdenTrabajo:
    def __init__(self, id_equipo, id_empleado, id_presupuesto=None):
        self.estado_general = "Para Revisión"
        self.fecha_creacion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.id_equipo = id_equipo
        self.id_empleado = id_empleado
        self.id_presupuesto = id_presupuesto

    def registrar(self):
        cursor = DB.cursor()
        sql = """INSERT INTO Orden_Trabajo 
                 (Estado_General, Fecha_Creacion, Equipo_ID_Equipo, Empleado_ID_Empleado, Presupuesto_ID_Presupuesto) 
                 VALUES (%s, %s, %s, %s, %s)"""
        val = (self.estado_general, self.fecha_creacion, self.id_equipo, self.id_empleado, self.id_presupuesto)
        cursor.execute(sql, val)
        DB.commit()
        id_generado = cursor.lastrowid
        cursor.close()
        return id_generado

    @staticmethod
    def buscar_pendientes():
        cursor = DB.cursor(dictionary=True)
        sql = """SELECT ot.ID_OT as id_orden, ot.ID_OT as codigo, 
                 CONCAT(e.Marca_Modelo, ' - ', e.Tipo_Dispositivo) as equipo, 
                 ot.Estado_General as estado, ot.Diagnostico_Final as diagnostico_final,
                 ot.Equipo_ID_Equipo as id_equipo
                 FROM Orden_Trabajo ot 
                 LEFT JOIN Equipo e ON ot.Equipo_ID_Equipo = e.ID_Equipo"""
        cursor.execute(sql)
        resultados = cursor.fetchall()
        cursor.close()
        return resultados

    @staticmethod
    def actualizar_estado(id_orden, estado):
        cursor = DB.cursor()
        cursor.execute("UPDATE Orden_Trabajo SET Estado_General = %s WHERE ID_OT = %s", (estado, id_orden))
        DB.commit()
        cursor.close()