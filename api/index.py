import os
import sys
from pathlib import Path

# Ensure root project directory is on sys.path for Django imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

application = get_wsgi_application()

# Auto-initialize database schema and seed data on Vercel serverless start
if os.getenv('VERCEL') and not os.path.exists('/tmp/db_initialized'):
    try:
        call_command('migrate', interactive=False)
        call_command('seed_data')
        with open('/tmp/db_initialized', 'w') as f:
            f.write('initialized')
    except Exception as e:
        print("Vercel auto initialization notice:", e)

# Vercel entrypoint
app = application
