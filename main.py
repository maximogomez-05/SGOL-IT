import sys
from auth.login import Autenticacion
from modelos.empleado import Empleado
from modelos.cliente import Cliente
from modelos.equipo import Equipo
from modelos.orden_trabajo import OrdenTrabajo
from modelos.inventario import Inventario
from modelos.control_calidad import ControlCalidad
from modelos.seguimiento import Seguimiento
from modelos.factura import Factura
from modelos.presupuesto import Presupuesto


def pedir_texto(mensaje, min_len=3):
    while True:
        valor = input(mensaje).strip()
        if len(valor) >= min_len and not valor.isnumeric():
            return valor
        print(f"Error: Ingrese un texto valido (minimo {min_len} caracteres).")

def pedir_cadena(mensaje, min_len=1):
    while True:
        valor = input(mensaje).strip()
        if len(valor) >= min_len:
            return valor
        print(f"Error: El campo no puede estar vacio.")

def pedir_dni(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and 7 <= len(valor) <= 8:
            return valor
        print("Error: DNI invalido (debe tener entre 7 y 8 digitos numericos).")

def pedir_email(mensaje):
    while True:
        valor = input(mensaje).strip()
        if '@' in valor and '.' in valor.split('@')[-1]:
            return valor
        print("Error: Formato de correo electronico invalido.")

def pedir_telefono(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit() and 8 <= len(valor) <= 15:
            return valor
        print("Error: Telefono invalido (solo numeros).")

def pedir_password(mensaje, min_len=6):
    while True:
        valor = input(mensaje).strip()
        if len(valor) >= min_len:
            return valor
        print(f"Error: La contraseña debe tener al menos {min_len} caracteres.")

def pedir_entero(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit():
            return int(valor)
        print("Error: Ingrese un numero entero.")

def pedir_decimal(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            numero = float(valor)
            if numero >= 0: return numero
            print("Error: El valor no puede ser negativo.")
        except ValueError:
            print("Error: Ingrese un numero valido (ej: 1500.50).")



def menu_administrador(id_empleado, nombre_empleado):
    while True:
        print("\n" + "="*40)
        print(f" PANEL ADMINISTRATIVO - {nombre_empleado}")
        print("="*40)
        print("1. Registrar nuevo empleado")
        print("2. Gestionar Inventario (Precios/Stock)")
        print("3. Salir / Cerrar Sesion")
        opcion = input("Seleccione: ")

        if opcion == '1':
            print("\n--- ALTA DE PERSONAL ---")
            nom = pedir_texto("Nombre completo: ")
            log = pedir_cadena("Usuario de login: ", 4)
            pas = pedir_password("Contraseña: ")
            print("Roles: [1] Admin [2] Recepcion [3] Tecnico")
            rol = input("ID del Rol: ")
            Empleado(nom, log, pas, rol).registrar()
            
        elif opcion == '2':
            print("\n--- CATALOGO DE INVENTARIO ---")
            print("1. Ver lista de items | 2. Agregar nuevo item")
            sub = input("Opcion: ")
            if sub == '1':
                items = Inventario.listar_todo()
                if not items: print("Inventario vacio.")
                for i in items:
                    print(f"ID: {i['id']} | {i['descripcion']} | ${i['precio']} | Stock: {i['stock']}")
            elif sub == '2':
                tipo = "Repuesto_Fisico" if input("¿Es repuesto? (s/n): ").lower() == 's' else "Servicio_ManoObra"
                desc = pedir_texto("Descripcion: ")
                pre = pedir_decimal("Precio Actual: ")
                stk = pedir_entero("Stock inicial: ") if tipo == "Repuesto_Fisico" else None
                url = input("URL de referencia (opcional): ")
                Inventario(tipo, desc, pre, stk, url).registrar()
        elif opcion == '3': break


def menu_recepcionista(id_empleado, nombre_empleado):
    while True:
        print("\n" + "="*40)
        print(f" PANEL DE RECEPCION - {nombre_empleado}")
        print("="*40)
        print("1. Ingresar Equipo (Enviar a revisión técnica)")
        print("2. Gestionar Presupuestos (Contactar Cliente)")
        print("3. Facturacion y Entrega de Equipo")
        print("4. Salir / Cerrar Sesion")
        opcion = input("Seleccione: ")
        
        if opcion == '1':
            print("\n--- INGRESO DE EQUIPO ---")
            dni = pedir_dni("DNI del Cliente: ")
            clie = Cliente.buscar_por_dni(dni)
            if clie:
                print(f"Cliente identificado: {clie['nombre']}")
                id_c = clie['id']
            else:
                print("Cliente nuevo. Registre sus datos:")
                id_c = Cliente(dni, pedir_texto("Nombre: "), pedir_email("Email: "), pedir_telefono("Tel: "), pedir_password("Pass Web: ")).registrar()
            
            id_e = Equipo(pedir_cadena("Numero de Serie: "), pedir_texto("Modelo: "), pedir_texto("Tipo: "), id_c).registrar()
            
            # Se crea la OT sin presupuesto. Nace en estado "Para Revisión".
            OrdenTrabajo(id_e, id_empleado, id_presupuesto=None).registrar()
            
        elif opcion == '2':
            print("\n--- EQUIPOS ESPERANDO APROBACION DE PRESUPUESTO ---")
            ordenes = OrdenTrabajo.buscar_pendientes()
            esperando = [o for o in ordenes if o['estado'] == 'Esperando Aprobación']
            
            if not esperando:
                print("No hay equipos esperando aprobación del cliente.")
                continue
                
            for o in esperando:
                print(f"ID Orden: {o['id_orden']} | Ticket: {o['codigo']} | {o['equipo']}")
                
            id_sel = input("\nIngrese ID de Orden para gestionar (Enter para cancelar): ")
            if not id_sel.isdigit(): continue
            id_sel = int(id_sel)
            
            # Buscar el equipo asociado a esta OT para el presupuesto
            ot_seleccionada = next((o for o in esperando if o['id_orden'] == id_sel), None)
            if not ot_seleccionada: continue

            # Traer el informe del técnico desde el tracking web
            tracking = Seguimiento.consultar_tracking(ot_seleccionada['codigo'])
            if tracking and tracking['historial']:
                print("\n--- INFORME DEL TECNICO ---")
                # El último historial es el informe del técnico
                print(f"DIAGNOSTICO: {tracking['historial'][0][1]}") 
                print("---------------------------")
            
            print("\nTras contactar al cliente con este diagnóstico:")
            print("[1] El cliente ACEPTA el presupuesto")
            print("[2] El cliente RECHAZA (Solo se cobra diagnóstico)")
            decision = input("Decisión: ")

            if decision == '1':
                monto = pedir_decimal("Monto Total Acordado (Diagnóstico + Repuestos) $: ")
                # Generamos Presupuesto y lo vinculamos
                id_p = Presupuesto(monto, 0, ot_seleccionada['id_equipo'], "Aprobado").registrar()
                OrdenTrabajo.vincular_presupuesto(id_sel, id_p)
                OrdenTrabajo.actualizar_estado(id_sel, "En Reparación")
                Seguimiento.registrar_hito(id_sel, "En Reparación", "Presupuesto aprobado por el cliente. Iniciando trabajos.")
                print(" Presupuesto aprobado. El equipo volvió al panel del técnico.")

            elif decision == '2':
                monto = pedir_decimal("Costo de la Consulta/Diagnóstico $: ")
                id_p = Presupuesto(monto, 0, ot_seleccionada['id_equipo'], "Rechazado").registrar()
                OrdenTrabajo.vincular_presupuesto(id_sel, id_p)
                OrdenTrabajo.actualizar_estado(id_sel, "Rechazado - Solo Cobrar Consulta")
                Seguimiento.registrar_hito(id_sel, "Cancelado", "Presupuesto rechazado. Se devolverá el equipo cobrando revisión.")
                
                print("\n IMPORTANTE: Para poder facturar, debés cargar el ítem de 'Consulta/Diagnóstico' a la orden.")
                items = Inventario.listar_todo()
                for i in items: print(f"ID: {i['id']} | {i['descripcion']} | ${i['precio']}")
                id_i = pedir_entero("Ingrese el ID del ítem de Consulta: ")
                OrdenTrabajo.agregar_item_a_orden(id_sel, id_i, 1)
                print(" Orden cancelada y lista para cobro en caja.")

        elif opcion == '3':
            print("\n--- EQUIPOS LISTOS PARA RETIRO ---")
            ordenes = OrdenTrabajo.buscar_pendientes()
            listos = [o for o in ordenes if o['estado'] in ('Reparado', 'Rechazado - Solo Cobrar Consulta')]
            
            if not listos:
                print("No hay equipos esperando facturación/entrega.")
                continue
                
            for o in listos:
                print(f"ID: {o['id_orden']} | Ticket: {o['codigo']} | {o['equipo']} | Estado: {o['estado']}")
                
            id_sel = input("\nID de Orden a cobrar (Enter para cancelar): ")
            if not id_sel.isdigit(): continue
            
            factura_data = OrdenTrabajo.generar_factura(id_sel)
            if factura_data and factura_data['detalles']:
                print("\n" + "-"*35)
                print(" RESUMEN DE CARGOS")
                print("-"*35)
                for d in factura_data['detalles']:
                    print(f"{d['cantidad']}x {d['descripcion']} (${d['precio_unit']}) = ${d['subtotal']}")
                print("-" * 35)
                print(f"TOTAL A PAGAR: ${factura_data['total']}")
                    
                if input("\n¿Confirmar pago y entrega? (s/n): ").lower() == 's':
                    print("\nMetodos: [1] Efectivo [2] Tarjeta [3] Transferencia")
                    met_pago = {'1': 'Efectivo', '2': 'Tarjeta', '3': 'Transferencia'}.get(input("Metodo: "), 'Otro')

                    if Factura(id_sel, factura_data['total'], met_pago).registrar():
                        if OrdenTrabajo.actualizar_estado(id_sel, "Entregado"):
                            Seguimiento.registrar_hito(id_sel, "Entregado", f"Pago via {met_pago}. Equipo retirado por el cliente.")
                            print(" Cobro registrado y orden cerrada exitosamente.")
            else:
                print(" Error: No hay ítems cargados en esta orden para facturar.")

        elif opcion == '4': break


def menu_tecnico(id_empleado, nombre_empleado):
    while True:
        print("\n" + "="*40)
        print(f" PANEL TECNICO - {nombre_empleado}")
        print("="*40)
        ordenes = OrdenTrabajo.buscar_pendientes()
        # El tecnico solo ve lo que tiene que revisar o reparar
        trabajos_tecnico = [o for o in ordenes if o['estado'] in ('Para Revisión', 'En Reparación')]
        
        if not trabajos_tecnico: 
            print("Sin trabajos pendientes en el laboratorio."); break
            
        for o in trabajos_tecnico:
            print(f"ID: {o['id_orden']} | Ticket: {o['codigo']} | {o['equipo']} | ESTADO: {o['estado']}")
        
        id_sel = input("\nID de Orden a gestionar (Enter para salir): ")
        if not id_sel.isdigit(): break
        id_sel = int(id_sel)

        # Buscar en que estado esta la orden seleccionada
        ot_seleccionada = next((o for o in trabajos_tecnico if o['id_orden'] == id_sel), None)
        if not ot_seleccionada: continue

        if ot_seleccionada['estado'] == 'Para Revisión':
            print("\n--- REVISION Y DIAGNOSTICO ---")
            informe = pedir_texto("Escriba el diagnóstico y repuestos necesarios para la Recepcionista:\n> ")
            OrdenTrabajo.actualizar_estado(id_sel, "Esperando Aprobación")
            Seguimiento.registrar_hito(id_sel, "Esperando Aprobación", informe)
            print(" Informe enviado a recepción. Esperando decisión del cliente.")
            
        elif ot_seleccionada['estado'] == 'En Reparación':
            print("\n--- GESTION DE REPARACION ---")
            print("1. Cargar Repuesto/Servicio (Descuenta Stock)")
            print("2. Registrar Control Calidad")
            print("3. Cambiar Estado / Finalizar Reparación")
            acc = input("Seleccione: ")

            if acc == '1':
                items = Inventario.listar_todo()
                for i in items: print(f"ID: {i['id']} | {i['descripcion']} | ${i['precio']}")
                id_i = pedir_entero("ID Item: ")
                cant = pedir_entero("Cantidad: ")
                OrdenTrabajo.agregar_item_a_orden(id_sel, id_i, cant)

            elif acc == '2':
                soft = pedir_texto("Software Benchmark: ")
                temp = pedir_cadena("Temperaturas: ")
                if ControlCalidad(id_sel, soft, temp).registrar_prueba():
                    print(" Calidad registrada.")

            elif acc == '3':
                print("[1] En Reparacion [2] Reparado (Finalizar)")
                est_op = input("Estado: ")
                if est_op == '2':
                    if not ControlCalidad.verificar_aprobacion(id_sel):
                        print(" ERROR: Debe registrar Control de Calidad antes de finalizar.")
                        continue
                    est_txt = "Reparado"
                else: 
                    est_txt = "En Reparacion"

                if OrdenTrabajo.actualizar_estado(id_sel, est_txt):
                    com = input("Comentario para el cliente: ")
                    Seguimiento.registrar_hito(id_sel, est_txt, com)
                    print(" Estado actualizado.")

        elif input("Presione Enter para continuar u otra tecla para salir al login...") == "": continue
        else: break



def main():
    auth = Autenticacion()
    while True:
        print("\n" + "╔" + "═"*44 + "╗")
        print("║      SISTEMA INTEGRAL DE GESTION SGOL-IT     ║")
        print("╚" + "═"*44 + "╝")
        print("1. Acceso Personal Autorizado (Login)")
        print("2. Portal del Cliente (Seguimiento de Equipo)")
        print("3. Cerrar Sistema")
        op = input("\nSeleccione una opcion: ")

        if op == '1':
            user = input("Usuario: ")
            pw = input("Password: ")
            res = auth.iniciar_sesion(user, pw)
            if res:
                print(f"\nBIENVENIDO {res['nombre']} ({res['nombre_rol']})")
                if res['rol_id'] == 1: menu_administrador(res['id'], res['nombre'])
                elif res['rol_id'] == 2: menu_recepcionista(res['id'], res['nombre'])
                elif res['rol_id'] == 3: menu_tecnico(res['id'], res['nombre'])
            else: print(" Credenciales invalidas.")

        elif op == '2':
            cod = input("\nIngrese su Codigo de Tracking (ej: OT-1234): ").strip()
            data = Seguimiento.consultar_tracking(cod)
            if data:
                print(f"\nEQUIPO: {data['info'][2]} | ESTADO ACTUAL: {data['info'][1]}")
                print("-" * 15 + " HISTORIAL DE SEGUIMIENTO " + "-" * 15)
                for h in data['historial']: print(f"[{h[2]}] {h[0]}: {h[1]}")
            else: print(" El codigo ingresado no es valido.")

        elif op == '3': 
            print("Apagando servidores..."); sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSaliendo del sistema...")
        sys.exit()