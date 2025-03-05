"""
WSGI config for hyper_pets_backend project in development.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyper_pets_backend.dev.settings')

application = get_wsgi_application()
