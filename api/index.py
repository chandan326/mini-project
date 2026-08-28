"""Vercel entry point.

Vercel detects the exported WSGI application directly.  Keeping this module
small avoids wrapping Django in a handler with an incompatible invocation
signature.
"""

from config.wsgi import application

app = application
