# Resumen Completo del Desarrollo: SGOL-IT

Este documento recopila de manera detallada todas las implementaciones, mejoras y correcciones realizadas en el **Sistema de Gestión Operativa para Laboratorio IT (SGOL-IT)** desde el inicio del proyecto. El sistema cumple rigurosamente con los requerimientos funcionales (RF) y no funcionales (RNF) del proyecto, respetando la arquitectura de base de datos relacional y adoptando prácticas modernas de desarrollo de software.

---

## 🛠️ Arquitectura del Sistema y Base de Datos

### 1. Migración Completa a POO (Fase 1)
* **Separación de Lógica y Datos:** Se eliminaron las consultas SQL directas en las rutas de la aplicación (`app.py`), delegando toda la responsabilidad de acceso a base de datos en clases del modelo de objetos.
* **Capa de Modelos (`modelos/`):**
  * `Cliente`: Controla el registro de clientes, validación de credenciales y cambio de contraseñas.
  * `Empleado`: Administra el personal, encriptación de claves, alta/baja lógica e historial.
  * `Equipo`: Gestiona los dispositivos ingresados al laboratorio.
  * `OrdenTrabajo`: Controla el ciclo de vida de los servicios técnicos (estados, diagnósticos, asignaciones).
  * `DetalleOrden`: Gestiona la relación de repuestos y mano de obra aplicados a cada orden de trabajo.
  * `Inventario`: Administra el catálogo de repuestos y servicios técnicos disponibles.
  * `Factura`: Registra la facturación y los métodos de pago.
  * `Presupuesto`: Controla el estado de aprobación de las cotizaciones por parte del cliente.
  * `Seguimiento`: Registra los hitos y auditoría de cambios de estado en la reparación.
  * `ControlCalidad`: Almacena las pruebas de benchmark y temperaturas requeridas para habilitar la entrega del equipo.

---

## 🔒 Seguridad y Gestión de Sesiones

### 2. Cifrado de Contraseñas (Fase 2)
* **Hashing Seguro:** Integración de la biblioteca `werkzeug.security` para el cifrado seguro de contraseñas utilizando hashes `scrypt` tanto para empleados como para clientes.
* **Ampliación de Columnas en Base de Datos:** Se detectó que las contraseñas se truncaban debido al límite de `VARCHAR(45)` en la base de datos original. Se modificaron las tablas a `VARCHAR(255)` para almacenar correctamente los hashes completos de 162 caracteres.

### 3. Cambio Obligatorio de Contraseña (Fase 3)
* **Política de Claves por Defecto:** Al ingresar con claves iniciales (`admin123`, `tecnico123`, `recep123`, `123`), el sistema detecta que es una contraseña por defecto.
* **Interceptor Global (`before_request`):** Se bloquea la navegación por el sistema y se redirige forzadamente al usuario a la vista `/cambiar_password_obligatorio` hasta que configure una clave personalizada y segura.

### 4. Alta/Baja Lógica de Empleados (Fase 4)
* **Preservación de Historial:** Para evitar violaciones de integridad referencial al borrar empleados con registros vinculados, se reemplazó la eliminación física por la baja lógica.
* **Atributo `Activo`:** Se añadió el campo `Activo` en la tabla `empleado` y se habilitó un panel dinámico para que el Administrador active o desactive cuentas de personal con un solo clic.

---

## 🎨 Diseño Visual y Experiencia de Usuario (UX)

### 5. Estética Cyber-Laboratorio Premium
* **Glassmorphism:** Diseño oscuro neón utilizando efectos de difuminado y bordes brillantes.
* **Tipografía Avanzada:** Integración de las fuentes Google Fonts *Inter* y *Outfit*.
* **Control de Autocompletado:** Implementación de técnicas anti-autocompletado para prevenir que navegadores (Chrome/Edge) llenen formularios técnicos con datos anteriores.
* **Legibilidad y Contraste:** Corrección del color de fondo de las opciones de menú y textos grises para una lectura cómoda.

---

## 📈 Dashboard Estadístico e Invoicing (Fase 5)

### 6. Métricas y Gráficos para el Administrador
* **Integración de Chart.js:** Se diseñó un panel dinámico interactivo con 4 gráficos:
  1. *Facturación Mensual Histórica* (Gráfico de área neón con gradientes).
  2. *Métodos de Pago* (Gráfico circular de distribución de cobros).
  3. *Repuestos vs Mano de Obra* (Gráfico de dona comparativo).
  4. *Eficiencia de Técnicos* (Gráfico de barras con cantidad de órdenes finalizadas por persona).
* **Métricas Financieras Rápidas:** Tarjetas con el acumulado histórico de facturación y cantidad total de órdenes completadas.

---

## 🐛 Correcciones y Robustez del Sistema (Fase 6)

### 7. Solución a Errores Críticos y Regresiones
* **SQL Crash en Turnos Web:** Se añadió la inicialización segura y automática de la tabla `turno` al ingresar al módulo de turnos, evitando colapsos si la base de datos estaba vacía.
* **Acceso y Roles del Admin:** Se habilitó al Administrador (`rol_id = 1`) para realizar pruebas y operaciones de todos los roles (Técnico y Recepcionista) directamente desde su Dashboard, sin necesidad de cerrar sesión.
* **Bloqueo de Cotizaciones en $0:** Se añadió una validación en la cotización que impide emitir presupuestos vacíos o en $0, evitando que el flujo quede atascado o se generen cobros nulos.
* **Carga de Repuestos en Diagnóstico:** Se flexibilizó la edición de la lista de materiales para que los técnicos puedan agregar repuestos tanto en estado `Para Revisión` como en `En Diagnóstico`.

### 8. Fallback de Scraping e Integridad de Accesos
* **Buscador de HardGamers como Fallback de Scraping:** Para eludir las barreras anti-bot de MercadoLibre y los sitios SPA dinámicos como CompraGamer, se implementó un scraper de búsqueda en **HardGamers** (usando `text=`). Cuando falla el scraping directo, se extraen palabras clave del slug de la URL o descripción local, se realiza una búsqueda de mercado y se valida mediante coincidencia porcentual de tokens. El sistema devuelve el precio real y actualiza el enlace "Ver ref. 🔗" en el inventario con el link del producto exacto comparado.
* **Resolución de Error de Duplicidad en Órdenes de Trabajo:** Se corrigió el error `Duplicate entry '' for key 'Codigo_Tracking_web'` al registrar una segunda orden de trabajo. Se migró la consulta SQL directa al uso del modelo `OrdenTrabajo` y su método `.registrar()`, garantizando que la creación de toda orden genere y almacene un código de seguimiento web único (`OT-XXXXXX`).
* **Sincronización de Credenciales para Clientes Preexistentes:** Se detectó que si un cliente se registraba inicialmente solicitando un turno web (con la contraseña por defecto `"123"`), y posteriormente el recepcionista le asignaba otra contraseña temporal en el local, el sistema no la actualizaba. Se implementó una sincronización automática (`Cliente.actualizar_password`) durante la creación de la orden de trabajo para sobrescribir credenciales temporales previas.
* **Normalización Dinámica de Entrada de DNI en Login:** Se implementó una limpieza automática basada en expresiones regulares (`re.sub`) en el inicio de sesión del portal de autogestión de clientes para ignorar cualquier punto, espacio o guion introducido en el campo del DNI, garantizando un cotejo robusto contra el formato numérico de la base de datos.
* **Portabilización del Poblador de Base de Datos (`seed_db.py`):** Se dinamizó la declaración de la ruta del proyecto usando `os.path` en lugar de una ruta absoluta propia de otra máquina, permitiendo ejecutar y resembrar la base de datos sin errores de entorno.

---

## 🛠️ Nuevas Funcionalidades e Integraciones Recientes (Fase Actual)

### 9. Control de Garantía y Selección de Servicio/Síntoma
* **Declaración de Garantía:** Se añadió la opción obligatoria para que el cliente indique si su equipo posee garantía al solicitar un turno online. Esto se propaga al proceso de recepción y se almacena en la orden de trabajo.
* **Tipos de Servicio / Síntomas:** Se incorporó un campo selectivo con los principales tipos de servicio tanto en los turnos web como en la recepción de órdenes manuales, logrando que el recepcionista cuente con opciones predefinidas y que, si la orden proviene de un turno web, el servicio se pre-seleccione de forma automática.
* **Migración de Esquema Dinámica:** Se implementaron validaciones automáticas `ALTER TABLE` que agregan las columnas `Garantia` y `Servicio` a las tablas `turno` y `orden_trabajo` en tiempo de ejecución al entrar al módulo de turnos para prevenir fallas por falta de campos en la base de datos.

### 10. Impresión de Ticket de Recepción por Duplicado
* **Formato de Comprobante Duplicado:** Al generar exitosamente una orden de trabajo, el recepcionista es redirigido de manera automática a la vista `/imprimir_ticket/<id_orden>`.
* **Copia Cliente y Copia Empresa:** La página del ticket renderiza dos bloques de comprobante idénticos en una misma hoja, con datos detallados del cliente, del dispositivo (tipo, modelo, número de serie, garantía, síntoma/servicio) y áreas para las firmas físicas del cliente y el operador, separados por una línea punteada de corte con tijeras (`✂️`).
* **Estilos y Autodisparo de Impresión (`@media print`):** Se diseñó una barra superior no imprimible con controles rápidos, y se aplicaron estilos CSS de impresión que transforman el fondo en blanco con letras de alto contraste para ahorro de tinta, ocultando cabeceras y menús del sitio. Un script de JavaScript abre automáticamente el cuadro de diálogo de impresión del sistema al cargar la página.

### 11. Carga de Fotografías por el Técnico en Reparación
* **Evolución del Registro Visual:** Se implementó una sección de subida de archivos múltiples en la vista de gestión del laboratorio técnico. Los técnicos pueden subir hasta 4 imágenes simultáneas para ilustrar problemas o el estado interno durante el diagnóstico o reparación.
* **Migración a Tipo `TEXT`:** Se modificó la columna `Fotos` de la tabla `orden_trabajo` a tipo `TEXT` para permitir almacenar una lista ilimitada de nombres de imágenes separadas por comas, previniendo truncamiento de caracteres.
* **Persistencia Acumulativa y Bitácora:** Las nuevas fotos cargadas por el técnico no eliminan las fotos iniciales de la recepción, sino que se concatenan. Cada subida genera además un hito en el historial de `Seguimiento` del equipo para auditoría e información al cliente.


