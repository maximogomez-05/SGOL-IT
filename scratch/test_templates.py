import os
import jinja2

def test_templates():
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    print(f"Checking templates in: {templates_dir}")
    
    loader = jinja2.FileSystemLoader(templates_dir)
    env = jinja2.Environment(loader=loader)
    
    templates_to_test = [
        'solicitar_turno.html',
        'ingreso_equipo.html',
        'ticket_recepcion.html',
        'seguimiento.html',
        'portal_cliente.html'
    ]
    
    success = True
    for template_name in templates_to_test:
        try:
            env.get_template(template_name)
            print(f"[OK] {template_name}: Compiled successfully.")
        except Exception as e:
            print(f"[ERROR] {template_name}: Failed to compile! Error: {e}")
            success = False
            
    if success:
        print("\nAll templates compiled successfully!")
    else:
        print("\nSome templates failed to compile!")
        exit(1)

if __name__ == '__main__':
    test_templates()
