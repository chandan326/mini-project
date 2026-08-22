import os
import sys
import traceback
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def _ensure_db_initialized():
    if os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        tmp_dir = Path('/tmp')
        tmp_dir.mkdir(parents=True, exist_ok=True)
        db_flag = tmp_dir / 'db_initialized'
        tmp_db = tmp_dir / 'db.sqlite3'
        
        if not db_flag.exists():
            try:
                base_db = BASE_DIR / 'db.sqlite3'
                if base_db.exists() and base_db.stat().st_size > 0:
                    import shutil
                    shutil.copyfile(base_db, tmp_db)
                else:
                    import django
                    django.setup()
                    from django.core.management import call_command
                    call_command('migrate', interactive=False)
                    call_command('seed_data')
                
                db_flag.write_text('initialized')
            except Exception as e:
                print("Vercel DB Init Warning:", e)

# Run DB initialization before Django setup
_ensure_db_initialized()

# Initialize Django WSGI application
import django
django.setup()

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
