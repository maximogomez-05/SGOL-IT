from config.database import DB

def crear_rutinas():
    cursor = DB.cursor()
    
    # 1. Trigger: Evitar que el stock sea negativo
    trigger_sql = """
    CREATE TRIGGER trg_stock_minimo BEFORE UPDATE ON catalogo_inventario
    FOR EACH ROW
    BEGIN
        IF NEW.Stock_Disponible < 0 THEN
            SET NEW.Stock_Disponible = 0;
        END IF;
    END;
    """
    
    # 2. Procedure 1: Obtener Alertas de Stock
    proc1_sql = """
    CREATE PROCEDURE sp_obtener_alertas_stock()
    BEGIN
        SELECT Descripcion, Stock_Disponible, Stock_Minimo 
        FROM catalogo_inventario 
        WHERE Tipo_Item = 'Repuesto_Fisico' AND Stock_Disponible <= Stock_Minimo;
    END;
    """
    
    # 3. Procedure 2: Obtener Ordenes Recientes
    proc2_sql = """
    CREATE PROCEDURE sp_obtener_ordenes_recientes()
    BEGIN
        SELECT ot.ID_OT, ot.Codigo_Tracking_web as Codigo_Tracking, 
               eq.Marca, eq.Modelo, ot.Estado_General, 
               DATE_FORMAT(ot.Fecha_Creacion, '%d/%m/%Y %H:%i') as fecha, cl.Nombre_Completo as Cliente
        FROM orden_trabajo ot
        JOIN equipo eq ON ot.Equipo_ID_Equipo = eq.ID_Equipo
        JOIN cliente cl ON eq.Cliente_ID_Cliente = cl.ID_Cliente
        WHERE ot.Estado_General NOT IN ('Finalizado', 'Rechazado')
        ORDER BY ot.ID_OT DESC
        LIMIT 5;
    END;
    """
    
    # Drop existing if they exist
    try: cursor.execute("DROP TRIGGER IF EXISTS trg_stock_minimo;")
    except: pass
    try: cursor.execute("DROP PROCEDURE IF EXISTS sp_obtener_alertas_stock;")
    except: pass
    try: cursor.execute("DROP PROCEDURE IF EXISTS sp_obtener_ordenes_recientes;")
    except: pass
    
    try:
        print("Creando Trigger...")
        cursor.execute(trigger_sql)
        print("Trigger creado con exito.")
        
        print("Creando Procedure 1...")
        cursor.execute(proc1_sql)
        print("Procedure 1 creado con exito.")
        
        print("Creando Procedure 2...")
        cursor.execute(proc2_sql)
        print("Procedure 2 creado con exito.")
        
        DB.commit()
        print("Todas las rutinas fueron creadas con exito!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()

if __name__ == '__main__':
    crear_rutinas()
