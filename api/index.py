import os
import sys
import traceback
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django
import django
django.setup()

# Auto-migrate and seed database on Vercel
if os.getenv('VERCEL'):
    try:
        from django.core.management import call_command
        call_command('migrate', interactive=False)
        call_command('seed_data')
    except Exception as e:
        print("Vercel DB Init Notice:", e)

from django.core.wsgi import get_wsgi_application

_django_app = get_wsgi_application()

def app(environ, start_response):
    try:
        return _django_app(environ, start_response)
    except Exception:
        err_msg = traceback.format_exc()
        status = '500 Internal Server Error'
        output = f"<h1>Django Application Error</h1><pre>{err_msg}</pre>".encode('utf-8')
        response_headers = [('Content-Type', 'text/html; charset=utf-8'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]

handler = app
