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
        tmp_db = tmp_dir / 'db.sqlite3'
        
        if not tmp_db.exists() or tmp_db.stat().st_size == 0:
            base_db = BASE_DIR / 'db.sqlite3'
            copied = False
            if base_db.exists() and base_db.stat().st_size > 0:
                try:
                    import shutil
                    shutil.copyfile(str(base_db), str(tmp_db))
                    copied = True
                except Exception as e:
                    print("Vercel DB Copy Error:", e)
            
            if not copied or not tmp_db.exists() or tmp_db.stat().st_size == 0:
                try:
                    import django
                    django.setup()
                    from django.core.management import call_command
                    call_command('migrate', interactive=False)
                    call_command('seed_data')
                except Exception as e:
                    print("Vercel DB Migrate Error:", e)

# Run DB initialization before Django setup
_ensure_db_initialized()

# Initialize Django WSGI application
import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
handler = app
