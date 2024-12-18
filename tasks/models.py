# Importar el módulo datetime para trabajar con fechas y horas
import datetime
# Importar modelos de Django para definir el esquema de la base de datos
from django.db import models
# Importar el modelo User de Django para manejar usuarios
from django.contrib.auth.models import User

# Definición de la clase Profile que extiende el modelo de Django
class Profile(models.Model):
    # Relación uno a uno con el modelo User; se eliminará el perfil si se elimina el usuario
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo para la imagen de perfil, puede estar vacío o ser nulo
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    # Método para representar el objeto como una cadena
    def __str__(self):
        return self.user.username  # Retorna el nombre de usuario del perfil

class Task(models.Model):
    # Campos existentes
    title = models.CharField(max_length=30)
    description = models.TextField(blank=True, max_length=300)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='task_images/', null=True, blank=True)
    deadline = models.DateTimeField(null=False, blank=False, default=datetime.datetime.now)  
    email = models.EmailField(blank=True, null=True)


    

    def save(self, *args, **kwargs):
        if self.deadline:
            # Limpiamos los segundos y microsegundos
            self.deadline = self.deadline.replace(second=0, microsecond=0)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title + ' by ' + self.user.username
