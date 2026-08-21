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

from django.core.wsgi import get_wsgi_application
_django_app = get_wsgi_application()

def _ensure_db_initialized():
    if os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        from django.conf import settings
        if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
            return

        db_flag = Path('/tmp/db_initialized')
        tmp_db = Path('/tmp/db.sqlite3')
        
        if not db_flag.exists():
            try:
                os.makedirs(Path('/tmp'), exist_ok=True)
                base_db = BASE_DIR / 'db.sqlite3'
                if base_db.exists() and base_db.stat().st_size > 0:
                    import shutil
                    shutil.copyfile(base_db, tmp_db)
                else:
                    from django.core.management import call_command
                    call_command('migrate', interactive=False)
                    call_command('seed_data')
                
                with open(db_flag, 'w') as f:
                    f.write('initialized')
            except Exception as e:
                print("Vercel DB Init Warning:", e)
                try:
                    from django.core.management import call_command
                    call_command('migrate', interactive=False)
                    call_command('seed_data')
                    with open(db_flag, 'w') as f:
                        f.write('initialized')
                except Exception as err2:
                    print("Critical DB init error:", err2)

def app(environ, start_response):
    _ensure_db_initialized()
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
