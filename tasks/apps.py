from django.apps import AppConfig

from django.apps import AppConfig
from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver
class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasks"

    def ready(self):
        # Ejecuta el comando después de que la base de datos haya sido migrada
        post_migrate.connect(self.run_send_task_email, sender=self)

    def run_send_task_email(self, sender, **kwargs):
        call_command('send_task_email')


