import os
import sys
import traceback
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

def _ensure_db_initialized():
    if os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        try:
            tmp_db = Path('/tmp/db.sqlite3')
            if not tmp_db.exists() or tmp_db.stat().st_size == 0:
                base_db = BASE_DIR / 'db.sqlite3'
                if base_db.exists() and base_db.stat().st_size > 0:
                    import shutil
                    shutil.copyfile(str(base_db), str(tmp_db))
        except Exception as e:
            print("Vercel DB setup notice:", e)

# Copy pre-seeded DB if running in Vercel serverless container
_ensure_db_initialized()

# Initialize Django WSGI application
import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
handler = app
