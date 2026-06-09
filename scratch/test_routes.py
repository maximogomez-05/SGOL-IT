import requests

# Test login
s = requests.Session()
r = s.post('http://localhost:5050/login', data={'usuario': 'admin', 'password': '123456'}, allow_redirects=False)
print(f"Login -> Status: {r.status_code}, Location: {r.headers.get('Location', 'N/A')}")

if r.status_code == 302:
    # Follow redirect
    r2 = s.get('http://localhost:5050' + r.headers['Location'])
    print(f"Dashboard -> Status: {r2.status_code}, Len: {len(r2.text)}")
    if 'error' in r2.text.lower() or '500' in r2.text:
        print("!! ERROR en dashboard")
        # Extract error
        import re
        errors = re.findall(r'<pre[^>]*>(.*?)</pre>', r2.text, re.DOTALL)
        for e in errors[:3]:
            print(f"  Error: {e[:200]}")
    
    # Test all routes
    routes = [
        '/historial_general',
        '/laboratorio', 
        '/turnos',
        '/presupuestos_pendientes',
        '/entregas_pendientes',
        '/inventario',
        '/facturas',
    ]
    
    for route in routes:
        try:
            r3 = s.get(f'http://localhost:5050{route}')
            status = 'OK' if r3.status_code == 200 else f'ERR({r3.status_code})'
            has_error = 'TRACEBACK' if 'Traceback' in r3.text or 'Internal Server Error' in r3.text else ''
            print(f"  {route} -> {status} {has_error}")
            if has_error:
                import re
                errors = re.findall(r'<pre[^>]*>(.*?)</pre>', r3.text, re.DOTALL)
                for e in errors[:1]:
                    print(f"    -> {e[:300]}")
        except Exception as ex:
            print(f"  {route} -> EXCEPTION: {ex}")
else:
    print("Login FAILED - no redirect")
    if 'Credenciales' in r.text:
        print("  -> Credenciales invalidas")
