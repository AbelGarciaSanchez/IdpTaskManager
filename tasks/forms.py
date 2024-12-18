# Importamos las librerías necesarias de Django
from django import forms  # Módulo para crear formularios en Django
from django.contrib.auth.models import User  # Modelo User para gestionar usuarios
from .models import Task, Profile  # Importamos los modelos Task y Profile definidos en el mismo módulo

# Formulario para editar la tarea
from datetime import datetime

from django import forms
from .models import Task

from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'important', 'image', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control mb-2'}),
            'description': forms.Textarea(attrs={'class': 'form-control mb-2'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input mb-2'}),
            # Formateamos el 'deadline' para que no muestre los segundos
            'deadline': forms.DateTimeInput(
                attrs={'class': 'form-control mb-2', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'  # Formato sin segundos
            ),
        }

    def clean_deadline(self):
        # Aseguramos que la fecha no contenga segundos al guardarla
        deadline = self.cleaned_data['deadline']
        # Establecemos los segundos a 00 si es necesario
        return deadline.replace(second=0)


class ProfileForm(forms.ModelForm):
    # Agregar los campos del modelo User al formulario
    username = forms.CharField(  # Campo para el nombre de usuario
        max_length=150,  # Longitud máxima del campo
        required=True,  # Campo requerido
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'})  # Widget personalizado
    )
    email = forms.EmailField(  # Campo para el correo electrónico
        required=True,  # Campo requerido
        widget=forms.EmailInput(attrs={'class': 'form-control mb-2'})  # Widget personalizado
    )
    
    # El campo de foto de perfil pertenece al modelo Profile
    profile_picture = forms.ImageField(  # Campo para cargar una imagen
        required=False,  # Campo no requerido
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file mb-2'})  # Widget para subir archivos
    )

    class Meta:
        model = Profile  # Especificamos que este formulario está basado en el modelo Profile
        fields = ['profile_picture']  # Solo incluimos el campo profile_picture del modelo Profile

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.get('instance').user  # Accedemos al objeto User relacionado con el Profile
        super().__init__(*args, **kwargs)  # Llamamos al inicializador de la clase padre
        # Inicializamos los campos de User (username y email)
        if user_instance:  # Verificamos si el objeto User existe
            self.fields['username'].initial = user_instance.username  # Establecemos el valor inicial del campo username
            self.fields['email'].initial = user_instance.email  # Establecemos el valor inicial del campo email

