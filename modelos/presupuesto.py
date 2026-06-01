from config.database import DB

class Presupuesto:
    def __init__(self, monto_total_cotizado, presupuesto_preliminar_web=0.0):
        self.monto_total_cotizado = monto_total_cotizado
        self.estado_presupuesto = "Pendiente de Aprobacion"
        self.comprobante_impreso = "WEB"
        self.presupuesto_preliminar_web = presupuesto_preliminar_web

    def registrar(self):
        cursor = DB.cursor()
        sql = """INSERT INTO Presupuesto 
                 (Monto_Total_Cotizado, Estado_Presupuesto, Comprobante_Impreso, Presupuesto_Preliminar_Web) 
                 VALUES (%s, %s, %s, %s)"""
        val = (self.monto_total_cotizado, self.estado_presupuesto, self.comprobante_impreso, 
               self.presupuesto_preliminar_web)
        cursor.execute(sql, val)
        DB.commit()
        
        # Necesitamos devolver el ID que MySQL le dio a este presupuesto para vincularlo a la OT
        id_generado = cursor.lastrowid 
        cursor.close()
        return id_generado

    @staticmethod
    def actualizar_estado(id_presupuesto, estado):
        cursor = DB.cursor()
        try:
            cursor.execute("UPDATE presupuesto SET Estado_Presupuesto = %s WHERE ID_Presupuesto = %s", (estado, id_presupuesto))
            DB.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar estado del presupuesto: {e}")
            try:
                DB.conexion.rollback()
            except:
                pass
            return False
        finally:
            cursor.close()