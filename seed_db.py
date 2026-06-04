import sys
import os

# asegurar que la ruta base este en sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.append(base_dir)

import datetime
from config.database import DB
from werkzeug.security import generate_password_hash

# importar clases del modelo (paradigma oop)
from modelos.roles import Rol
from modelos.empleado import Empleado
from modelos.cliente import Cliente
from modelos.equipo import Equipo
from modelos.orden_trabajo import OrdenTrabajo
from modelos.inventario import Inventario
from modelos.presupuesto import Presupuesto
from modelos.factura import Factura
from modelos.seguimiento import Seguimiento
from modelos.detalle_orden import DetalleOrden
from modelos.control_calidad import ControlCalidad

def seed():
    cursor = DB.cursor()
    print("iniciando el poblado (seeding) de la base de datos...")

    # desactivar fk checks para vaciar de forma segura
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    
    tablas = [
        "roles", "empleado", "legajo_empleado", "cliente", 
        "catalogo_inventario", "equipo", "orden_trabajo", 
        "detalle_orden", "presupuesto", "factura", 
        "seguimiento_estados", "control_calidad", "turno"
    ]
    
    for t in tablas:
        try:
            cursor.execute(f"TRUNCATE TABLE {t}")
            print(f"tabla '{t}' limpia.")
        except Exception as e:
            print(f"error al limpiar tabla '{t}': {e}")
            
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    DB.commit()
    cursor.close()

    # 1. registrar roles
    print("registrando roles...")
    r1_id = Rol("Administrador").registrar()
    r2_id = Rol("Recepcionista").registrar()
    r3_id = Rol("Tecnico").registrar()

    # 2. registrar empleados
    print("registrando empleados...")
    emp_admin = Empleado("Admin General", "admin", "admin123", 1)
    id_admin = emp_admin.registrar()
    
    emp_recep = Empleado("Lucia Recepcionista", "recep", "123", 2)
    id_recep = emp_recep.registrar()
    
    emp_tecnico = Empleado("Mateo Tecnico", "tecnico", "123", 3)
    id_tecnico = emp_tecnico.registrar()

    # 3. registrar clientes con nombres comunes (pedido del usuario)
    print("registrando clientes...")
    c1 = Cliente("45000001", "Maximo Piriz", "maximo@gmail.com", "3704111222", "123")
    id_c1 = c1.registrar()
    
    c2 = Cliente("45000002", "Lautaro Torres", "lautaro@gmail.com", "3704333444", "123")
    id_c2 = c2.registrar()
    
    c3 = Cliente("45000003", "Julian Gonzalez", "julian@gmail.com", "3704555666", "123")
    id_c3 = c3.registrar()

    c4 = Cliente("45000004", "Maximo Gomez", "maximo.gomez@gmail.com", "3704666777", "123")
    id_c4 = c4.registrar()

    c5 = Cliente("45000005", "Maria Fernandez", "maria.fer@gmail.com", "3704888999", "123")
    id_c5 = c5.registrar()

    c6 = Cliente("45000006", "Carlos Rodriguez", "carlos.rod@gmail.com", "3704999000", "123")
    id_c6 = c6.registrar()

    c7 = Cliente("45000007", "Ana Martinez", "ana.martinez@gmail.com", "3704222333", "123")
    id_c7 = c7.registrar()

    # 4. registrar catalogo de inventario robusto (pedido del usuario)
    print("registrando repuestos y mano de obra...")
    
    # repuestos fisicos
    items_fisicos = [
        ("Memoria RAM DDR4 8GB Kingston 3200MHz", 25000, 15, 4, "https://www.compragamer.com/producto/Memoria_Kingston_DDR4_8GB_3200MHz_Fury_Beast_12040"),
        ("Disco SSD Kingston 480GB SATA3", 42000, 10, 3, "https://www.compragamer.com/producto/Disco_Solido_SSD_Kingston_480GB_A400_SATA_III_2_5_8398"),
        ("Pasta Termica Arctic MX-4 (4g)", 12500, 8, 2, "https://articulo.mercadolibre.com.ar/MLA-933391789-pasta-termica-arctic-mx-4-4g-_JM"),
        ("Fuente Gigabyte 650W 80 Plus", 82000, 5, 2, "https://www.fullh4rd.com.ar/prod/26815/fuente-gigabyte-650w-80-plus-bronze-p650b"),
        ("Placa Madre Gigabyte A520M K V2 AM4", 95000, 4, 1, "https://www.compragamer.com/producto/Mother_Gigabyte_A520M_K_V2_AM4_15220"),
        ("Disco SSD M.2 NVMe WD Blue 1TB", 89000, 6, 2, "https://www.compragamer.com/producto/Disco_Solido_SSD_M_2_NVMe_WD_Blue_1TB_SN580_4150MB_s_PCIe_Gen4_15093"),
        ("Teclado Universal Notebook USB", 15000, 12, 3, "https://articulo.mercadolibre.com.ar/MLA-11223344-teclado-universal-usb"),
        ("Pantalla LED 15.6 Slim 30 pines", 85000, 3, 1, "https://articulo.mercadolibre.com.ar/MLA-99887766-pantalla-led-156-slim"),
        ("Cooler Fan 120mm RGB", 9500, 20, 5, "https://www.fullh4rd.com.ar/prod/26425/cooler-fan-id-cooling-tf-12025-black-argb"),
        ("Cable HDMI 1.8m v2.0", 4500, 30, 8, "https://articulo.mercadolibre.com.ar/MLA-66778899-cable-hdmi-18m"),
        ("Cargador Notebook Universal 90W", 28000, 7, 2, "https://articulo.mercadolibre.com.ar/MLA-55443322-cargador-notebook-90w"),
        ("Pila CMOS CR2032 Litio", 1500, 50, 10, "https://articulo.mercadolibre.com.ar/MLA-33221100-pila-cr2032"),
        ("Modulo Memoria RAM DDR5 16GB", 58000, 8, 2, "https://www.compragamer.com/producto/Memoria_Kingston_DDR5_16GB_5600MHz_Fury_Beast_14163"),
        ("Disco Duro Externo 1TB Adata", 72000, 5, 2, "https://www.fullh4rd.com.ar/prod/26107/disco-externo-1tb-adata-hd330-black")
    ]
    
    db_inventario = {}
    import random
    for nombre, precio, stock, minimo, url in items_fisicos:
        stock_aleatorio = random.randint(30, 50)
        minimo_fijo = 10
        inv = Inventario("Repuesto_Fisico", nombre, precio, stock_aleatorio, minimo_fijo, url)
        db_inventario[nombre] = inv.registrar()

    # servicios de mano de obra
    items_servicios = [
        ("Diagnostico Tecnico General", 10000),
        ("Limpieza Fisica Completa y Pasta Termica", 18000),
        ("Formateo e Instalacion de Windows 11 + Drivers", 20000),
        ("Reparacion Compleja Placa Madre", 38000),
        ("Ensamblaje y Optimizacion de Computadora", 25000),
        ("Backup de Datos e Informacion", 15000),
        ("Cambio de Pantalla Notebook", 18000),
        ("Soldadura de Pin de Carga", 25000),
        ("Clonacion de Disco a SSD", 12000)
    ]
    
    for nombre, precio in items_servicios:
        inv = Inventario("Servicio_ManoObra", nombre, precio, 0, 0, "")
        db_inventario[nombre] = inv.registrar()

    # 5. crear ordenes de trabajo para cada cliente en distintos estados
    print("creando escenarios de ordenes de trabajo...")

    # cliente 1: maximo piriz (escenarios a, b, c, d, e, f)
    
    # orden 1: recien ingresado (para revision)
    eq1 = Equipo("SN-DELL-111", "Dell Inspiron 3000", "Notebook", id_c1)
    id_eq1 = eq1.registrar()
    ot1 = OrdenTrabajo(id_eq1, id_recep, estado_general="Para Revisión", detalles_visuales="tapa superior rayada, bisagra derecha floja")
    id_ot1 = ot1.registrar()
    Seguimiento.registrar_hito(id_ot1, "Ingresado", "el equipo ingreso al laboratorio para su revision inicial.")

    # orden 2: en diagnostico
    eq2 = Equipo("SN-ASUS-222", "ASUS ZenBook 14", "Notebook", id_c1)
    id_eq2 = eq2.registrar()
    ot2 = OrdenTrabajo(id_eq2, id_recep, estado_general="En Diagnóstico", detalles_visuales="pantalla con marcas leves, teclado desgastado")
    id_ot2 = ot2.registrar()
    Seguimiento.registrar_hito(id_ot2, "Ingresado", "el equipo ingreso al laboratorio para su revision inicial.")
    Seguimiento.registrar_hito(id_ot2, "En Diagnóstico", "el tecnico comenzo el diagnostico del equipo.")

    # orden 3: esperando respuesta (presupuesto generado)
    eq3 = Equipo("SN-GIGABYTE-333", "Sentey Gamer Core i5", "PC de Escritorio", id_c1)
    id_eq3 = eq3.registrar()
    pres3 = Presupuesto(40500) # diagnostico(10000) + pasta(12500) + limpieza(18000)
    id_pres3 = pres3.registrar()
    ot3 = OrdenTrabajo(id_eq3, id_recep, id_presupuesto=id_pres3, estado_general="Esperando Respuesta", detalles_visuales="polvo acumulado en rejillas, le falta un tornillo lateral")
    id_ot3 = ot3.registrar()
    DetalleOrden(1, 10000, id_ot3, db_inventario["Diagnostico Tecnico General"]).registrar()
    DetalleOrden(1, 12500, id_ot3, db_inventario["Pasta Termica Arctic MX-4 (4g)"]).registrar()
    DetalleOrden(1, 18000, id_ot3, db_inventario["Limpieza Fisica Completa y Pasta Termica"]).registrar()
    Seguimiento.registrar_hito(id_ot3, "Ingresado", "el equipo ingreso al laboratorio.")
    Seguimiento.registrar_hito(id_ot3, "En Diagnóstico", "el diagnostico determino fallas por temperatura.")
    Seguimiento.registrar_hito(id_ot3, "Esperando Respuesta", "presupuesto formal de $40500 enviado al cliente.")

    # orden 4: en reparacion (presupuesto aprobado)
    eq4 = Equipo("SN-HP-444", "HP Pavilion 15", "Notebook", id_c1)
    id_eq4 = eq4.registrar()
    pres4 = Presupuesto(35000) # diagnostico(10000) + ram 8gb(25000)
    id_pres4 = pres4.registrar()
    Presupuesto.actualizar_estado(id_pres4, "Aprobado")
    ot4 = OrdenTrabajo(id_eq4, id_recep, id_presupuesto=id_pres4, estado_general="En Reparación", detalles_visuales="carcasa sin marcas notorias")
    id_ot4 = ot4.registrar()
    DetalleOrden(1, 10000, id_ot4, db_inventario["Diagnostico Tecnico General"], estado_detalle="Reservado").registrar()
    DetalleOrden(1, 25000, id_ot4, db_inventario["Memoria RAM DDR4 8GB Kingston 3200MHz"], estado_detalle="Reservado").registrar()
    Seguimiento.registrar_hito(id_ot4, "Ingresado", "el equipo ingreso al laboratorio.")
    Seguimiento.registrar_hito(id_ot4, "En Diagnóstico", "se diagnostico cuello de botella en memoria ram.")
    Seguimiento.registrar_hito(id_ot4, "Esperando Respuesta", "presupuesto enviado.")
    Seguimiento.registrar_hito(id_ot4, "En Reparación", "el cliente aprobo. repuestos reservados en stock.")

    # orden 5: listo para entregar
    eq5 = Equipo("SN-MAC-555", "MacBook Air M1", "Notebook", id_c1)
    id_eq5 = eq5.registrar()
    pres5 = Presupuesto(30000) # diagnostico(10000) + windows(20000)
    id_pres5 = pres5.registrar()
    Presupuesto.actualizar_estado(id_pres5, "Aprobado")
    ot5 = OrdenTrabajo(id_eq5, id_recep, id_presupuesto=id_pres5, estado_general="Listo para Entregar", detalles_visuales="rayaduras leves en tapa inferior")
    id_ot5 = ot5.registrar()
    DetalleOrden(1, 10000, id_ot5, db_inventario["Diagnostico Tecnico General"], estado_detalle="Reservado").registrar()
    DetalleOrden(1, 20000, id_ot5, db_inventario["Formateo e Instalacion de Windows 11 + Drivers"], estado_detalle="Reservado").registrar()
    ControlCalidad(id_ot5, id_tecnico, "38 c en carga", "geekbench completado", "sistema operativo limpio y optimizado.").registrar()
    Seguimiento.registrar_hito(id_ot5, "Ingresado", "ingreso al taller.")
    Seguimiento.registrar_hito(id_ot5, "En Diagnóstico", "se requiere formateo y cambio de s.o.")
    Seguimiento.registrar_hito(id_ot5, "Esperando Respuesta", "presupuesto aprobado.")
    Seguimiento.registrar_hito(id_ot5, "En Reparación", "formateo realizado.")
    Seguimiento.registrar_hito(id_ot5, "Listo para Entregar", "control de calidad aprobado. listo para retiro.")

    # orden 6: finalizado (con factura tipo b cobrada)
    eq6 = Equipo("SN-THINK-666", "Lenovo ThinkPad T480", "Notebook", id_c1)
    id_eq6 = eq6.registrar()
    pres6 = Presupuesto(18000) # limpieza(18000)
    id_pres6 = pres6.registrar()
    Presupuesto.actualizar_estado(id_pres6, "Aprobado")
    ot6 = OrdenTrabajo(id_eq6, id_recep, id_presupuesto=id_pres6, estado_general="Finalizado", detalles_visuales="desgaste normal por uso")
    id_ot6 = ot6.registrar()
    DetalleOrden(1, 18000, id_ot6, db_inventario["Limpieza Fisica Completa y Pasta Termica"], estado_detalle="Consumido").registrar()
    fact6 = Factura(id_ot6, 18000, "Transferencia", "B", "45000001")
    id_fact6 = fact6.registrar()
    Seguimiento.registrar_hito(id_ot6, "Ingresado", "equipo ingreso.")
    Seguimiento.registrar_hito(id_ot6, "En Diagnóstico", "se recomendo limpieza preventiva.")
    Seguimiento.registrar_hito(id_ot6, "Esperando Respuesta", "presupuesto aprobado.")
    Seguimiento.registrar_hito(id_ot6, "En Reparación", "mantenimiento realizado.")
    Seguimiento.registrar_hito(id_ot6, "Listo para Entregar", "qa completado con exito.")
    Seguimiento.registrar_hito(id_ot6, "Finalizado", "factura tipo b generada. pago recibido.")


    # cliente 2: lautaro torres (para revision)
    eq7 = Equipo("SN-ACER-777", "Acer Aspire 3", "Notebook", id_c2)
    id_eq7 = eq7.registrar()
    ot7 = OrdenTrabajo(id_eq7, id_recep, estado_general="Para Revisión", detalles_visuales="no enciende despues de un corte de luz, olor a quemado")
    id_ot7 = ot7.registrar()
    Seguimiento.registrar_hito(id_ot7, "Ingresado", "el equipo ingreso con posible corto en placa de video o fuente de alimentacion interna.")

    # cliente 3: julian gonzalez (en diagnostico)
    eq8 = Equipo("SN-MSI-888", "MSI GF63 Thin", "Notebook", id_c3)
    id_eq8 = eq8.registrar()
    ot8 = OrdenTrabajo(id_eq8, id_recep, estado_general="En Diagnóstico", detalles_visuales="calentamiento excesivo, ventiladores ruidosos")
    id_ot8 = ot8.registrar()
    Seguimiento.registrar_hito(id_ot8, "Ingresado", "ingreso para mantenimiento térmico.")
    Seguimiento.registrar_hito(id_ot8, "En Diagnóstico", "tecnico analizando curva de ventilador y estado de pasta termica de fabrica.")

    # cliente 4: maximo gomez (esperando respuesta)
    eq9 = Equipo("SN-OFFICE-999", "PC de Escritorio Oficina", "PC de Escritorio", id_c4)
    id_eq9 = eq9.registrar()
    pres9 = Presupuesto(64000) # ssd 480gb (42000) + diagnostico (10000) + clonacion (12000)
    id_pres9 = pres9.registrar()
    ot9 = OrdenTrabajo(id_eq9, id_recep, id_presupuesto=id_pres9, estado_general="Esperando Respuesta", detalles_visuales="lentitud extrema al encender y abrir navegadores")
    id_ot9 = ot9.registrar()
    DetalleOrden(1, 10000, id_ot9, db_inventario["Diagnostico Tecnico General"]).registrar()
    DetalleOrden(1, 42000, id_ot9, db_inventario["Disco SSD Kingston 480GB SATA3"]).registrar()
    DetalleOrden(1, 12000, id_ot9, db_inventario["Clonacion de Disco a SSD"]).registrar()
    Seguimiento.registrar_hito(id_ot9, "Ingresado", "el equipo ingreso lento.")
    Seguimiento.registrar_hito(id_ot9, "En Diagnóstico", "se determino que el disco mecanico esta dañado. se sugiere cambio a ssd y clonacion de datos.")
    Seguimiento.registrar_hito(id_ot9, "Esperando Respuesta", "presupuesto formal de $64000 generado y enviado.")

    # cliente 5: maria fernandez (en reparacion)
    eq10 = Equipo("SN-HP14-000", "Notebook HP 14-dq", "Notebook", id_c5)
    id_eq10 = eq10.registrar()
    pres10 = Presupuesto(113000) # pantalla (85000) + diagnostico (10000) + cambio (18000)
    id_pres10 = pres10.registrar()
    Presupuesto.actualizar_estado(id_pres10, "Aprobado")
    ot10 = OrdenTrabajo(id_eq10, id_recep, id_presupuesto=id_pres10, estado_general="En Reparación", detalles_visuales="pantalla parpadea y tiene lineas horizontales al mover la tapa")
    id_ot10 = ot10.registrar()
    DetalleOrden(1, 10000, id_ot10, db_inventario["Diagnostico Tecnico General"], estado_detalle="Reservado").registrar()
    DetalleOrden(1, 85000, id_ot10, db_inventario["Pantalla LED 15.6 Slim 30 pines"], estado_detalle="Reservado").registrar()
    DetalleOrden(1, 18000, id_ot10, db_inventario["Cambio de Pantalla Notebook"], estado_detalle="Reservado").registrar()
    Seguimiento.registrar_hito(id_ot10, "Ingresado", "ingresado por falla en pantalla.")
    Seguimiento.registrar_hito(id_ot10, "En Diagnóstico", "se constato daño fisico en la pantalla lcd led.")
    Seguimiento.registrar_hito(id_ot10, "Esperando Respuesta", "presupuesto de cambio de modulo aprobado por la cliente.")
    Seguimiento.registrar_hito(id_ot10, "En Reparación", "modulo de repuesto recibido. instalando nueva pantalla.")

    # cliente 6: carlos rodriguez (listo para entregar)
    eq11 = Equipo("SN-SAMSUNG-123", "Samsung Galaxy Book", "Notebook", id_c6)
    id_eq11 = eq11.registrar()
    pres11 = Presupuesto(43000) # teclado (15000) + diagnostico (10000) + cambio (18000)
    id_pres11 = pres11.registrar()
    Presupuesto.actualizar_estado(id_pres11, "Aprobado")
    ot11 = OrdenTrabajo(id_eq11, id_recep, id_presupuesto=id_pres11, estado_general="Listo para Entregar", detalles_visuales="teclado falla en filas enteras, salpicadura de agua")
    id_ot11 = ot11.registrar()
    DetalleOrden(1, 10000, id_ot11, db_inventario["Diagnostico Tecnico General"], estado_detalle="Reservado").registrar()
    DetalleOrden(1, 15000, id_ot11, db_inventario["Teclado Universal Notebook USB"], estado_detalle="Reservado").registrar()
    DetalleOrden(1, 18000, id_ot11, db_inventario["Cambio de Pantalla Notebook"], estado_detalle="Reservado").registrar()
    ControlCalidad(id_ot11, id_tecnico, "teclas probadas", "funcionamiento correcto de usb y teclado", "reemplazo exitoso y secado de placa interna.").registrar()
    Seguimiento.registrar_hito(id_ot11, "Ingresado", "ingreso por corto de teclado.")
    Seguimiento.registrar_hito(id_ot11, "En Diagnóstico", "teclado dañado por humedad. placa madre intacta.")
    Seguimiento.registrar_hito(id_ot11, "Esperando Respuesta", "presupuesto aprobado.")
    Seguimiento.registrar_hito(id_ot11, "En Reparación", "teclado cambiado e internal clean completado.")
    Seguimiento.registrar_hito(id_ot11, "Listo para Entregar", "qa superado. equipo armado listo para entrega.")

    # cliente 7: ana martinez (finalizado - factura tipo a)
    eq12 = Equipo("SN-RYZEN-999", "PC de Escritorio Gamer Ryzen 5", "PC de Escritorio", id_c7)
    id_eq12 = eq12.registrar()
    pres12 = Presupuesto(43000) # limpieza (18000) + ensamblaje (25000)
    id_pres12 = pres12.registrar()
    Presupuesto.actualizar_estado(id_pres12, "Aprobado")
    ot12 = OrdenTrabajo(id_eq12, id_recep, id_presupuesto=id_pres12, estado_general="Finalizado", detalles_visuales="hacer mantenimiento completo e instalar refrigeracion liquida")
    id_ot12 = ot12.registrar()
    DetalleOrden(1, 18000, id_ot12, db_inventario["Limpieza Fisica Completa y Pasta Termica"], estado_detalle="Consumido").registrar()
    DetalleOrden(1, 25000, id_ot12, db_inventario["Ensamblaje y Optimizacion de Computadora"], estado_detalle="Consumido").registrar()
    # factura tipo a para cliente inscripto
    fact12 = Factura(id_ot12, 43000, "Efectivo", "A", "30-45000007-9")
    id_fact12 = fact12.registrar()
    Seguimiento.registrar_hito(id_ot12, "Ingresado", "equipo gamer ingresado para optimizacion.")
    Seguimiento.registrar_hito(id_ot12, "En Diagnóstico", "mantenimiento y ensamblaje planeado.")
    Seguimiento.registrar_hito(id_ot12, "Esperando Respuesta", "presupuesto aprobado.")
    Seguimiento.registrar_hito(id_ot12, "En Reparación", "limpieza profunda e instalacion completadas.")
    Seguimiento.registrar_hito(id_ot12, "Listo para Entregar", "temperaturas maximas de 62 c en estres. qa ok.")
    Seguimiento.registrar_hito(id_ot12, "Finalizado", "factura tipo a generada bajo cuit 30-45000007-9. pago en efectivo recibido.")

    print("seeding completado con exito!")

if __name__ == "__main__":
    seed()
