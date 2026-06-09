import requests

s = requests.Session()
r = s.post('http://localhost:5050/login', data={'usuario': 'admin', 'password': '123456'}, allow_redirects=True)
print(f"Dashboard Status: {r.status_code}")

# Buscar errores reales en el HTML
if 'Traceback' in r.text:
    print("TRACEBACK encontrado!")
elif 'Internal Server Error' in r.text:
    print("500 ERROR encontrado!")
elif 'error' in r.text[:500].lower():
    # Check if it's just the word "error" in normal context
    import re
    # Look for actual error flash messages
    flash_errors = re.findall(r'alert-danger[^>]*>(.*?)</div', r.text, re.DOTALL)
    if flash_errors:
        for fe in flash_errors:
            print(f"Flash error: {fe.strip()[:200]}")
    else:
        print("No real errors - 'error' was in normal page context")
else:
    print("Dashboard cargado sin errores")

# Test gestionar_orden
r2 = s.get('http://localhost:5050/gestionar_orden/1')
print(f"\nGestionar OT#1: {r2.status_code}")
if 'Traceback' in r2.text:
    print("  TRACEBACK!")
    import re
    tb = re.findall(r'<pre[^>]*>(.*?)</pre>', r2.text, re.DOTALL)
    for t in tb[:1]:
        print(f"  {t[:500]}")

# Test detalle_historial
r3 = s.get('http://localhost:5050/detalle_historial/1')
print(f"Detalle OT#1: {r3.status_code}")
if 'Traceback' in r3.text:
    print("  TRACEBACK!")

# Test cotizar_orden
r4 = s.get('http://localhost:5050/cotizar_orden/3')
print(f"Cotizar OT#3: {r4.status_code}")
if 'Traceback' in r4.text:
    print("  TRACEBACK!")

# Test facturar_orden
r5 = s.get('http://localhost:5050/facturar/5')
print(f"Facturar OT#5: {r5.status_code}")
if 'Traceback' in r5.text:
    print("  TRACEBACK!")

# Test portal cliente
s2 = requests.Session()
r6 = s2.post('http://localhost:5050/tracking', data={'dni': '45000001', 'password_web': '123456'}, allow_redirects=True)
print(f"\nPortal Cliente: {r6.status_code}")
if 'Traceback' in r6.text:
    print("  TRACEBACK!")
elif 'portal' in r6.url or 'portal_cliente' in r6.text.lower():
    print("  Portal cargado OK")
else:
    print(f"  URL final: {r6.url}")
    if 'Datos incorrectos' in r6.text:
        print("  Datos incorrectos")

# Test seguimiento público con un tracking code
r7 = s.get('http://localhost:5050/seguimiento/OT-XD6VNN')
print(f"Seguimiento publico: {r7.status_code}")
if 'Traceback' in r7.text:
    print("  TRACEBACK!")

print("\nTests completados!")
