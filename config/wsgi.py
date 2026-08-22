import os
import sys
from pathlib import Path

# Ensure project root directory is on sys.path
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
                print("Vercel DB Init Notice:", e)

_ensure_db_initialized()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

def vercel_app(environ, start_response):
    return application(environ, start_response)

app = vercel_app
