from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from tasks.models import Task
from datetime import timedelta

class Command(BaseCommand):
    help = 'Envía un recordatorio por correo electrónico cuando una tarea esté a un día de su plazo'

    def handle(self, *args, **kwargs):
        now = timezone.now()  # Hora actual del sistema
        self.stdout.write(self.style.SUCCESS(f'Hora actual del sistema: {now}'))

        tasks_to_remind = Task.objects.all()  # Obtén todas las tareas
        for task in tasks_to_remind:
            time_difference = task.deadline - now

            if time_difference <= timedelta(days=1) and time_difference > timedelta(days=0):
                self.stdout.write(self.style.SUCCESS(f'Tarea encontrada: "{task.title}" con fecha de vencimiento {task.deadline} y le quedan exactamente 24 horas.'))

                if task.user.email:
                    try:
                        send_mail(
                            'Recordatorio de tarea a punto de vencer',
                            f'Tu tarea "{task.title}" está a punto de vencer. El plazo es: {task.deadline}',
                            'no.replay.taskmanager@gmail.com',  # Cambia esto por un correo electrónico de tu elección
                            [task.user.email],
                            fail_silently=False,
                        )
                        self.stdout.write(self.style.SUCCESS(f'Correo enviado a {task.user.email} para la tarea {task.title}'))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error al enviar correo a {task.user.email} para la tarea {task.title}: {e}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No hay correo electrónico asociado para el usuario de la tarea "{task.title}"'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Tarea no necesita recordatorio: "{task.title}" con fecha de vencimiento {task.deadline}'))
