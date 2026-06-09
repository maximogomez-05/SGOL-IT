import sys
sys.path.insert(0, '.')
from config.database import DB

cursor = DB.cursor()

# Actualizar stored procedure
cursor.execute("DROP PROCEDURE IF EXISTS sp_obtener_ordenes_recientes")

sp_sql = """
CREATE PROCEDURE sp_obtener_ordenes_recientes()
BEGIN
    SELECT ot.ID_OT, ot.Codigo_Tracking_web as Codigo_Tracking, 
           CONCAT(eq.Marca, ' ', eq.Modelo) as Marca, eq.Tipo_Dispositivo as Modelo, ot.Estado_General, 
           DATE_FORMAT(ot.Fecha_Creacion, '%d/%m/%Y %H:%i') as fecha, cl.Nombre_Completo as Cliente
    FROM orden_trabajo ot
    JOIN equipo eq ON ot.Equipo_ID_Equipo = eq.ID_Equipo
    JOIN cliente cl ON eq.Cliente_ID_Cliente = cl.ID_Cliente
    WHERE ot.Estado_General NOT IN ('Finalizado', 'Rechazado')
    ORDER BY ot.ID_OT DESC
    LIMIT 5;
END
"""
cursor.execute(sp_sql)
DB.commit()
cursor.close()
print("SP sp_obtener_ordenes_recientes actualizado OK")
