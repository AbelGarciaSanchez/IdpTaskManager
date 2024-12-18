import os
import django
from django.core.management import call_command

# Establecer las configuraciones de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "idp.settings")
django.setup()

# Ejecutar el comando send_task_email
call_command('send_task_email')
