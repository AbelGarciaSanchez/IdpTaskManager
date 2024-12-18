from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required
import re 
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from .forms import ProfileForm  
from django.contrib import messages
from django.core.paginator import Paginator


# Vista que requiere autenticación para mostrar el perfil del usuario.
@login_required
def profile(request):
    # Renderiza la plantilla 'profile.html' para mostrar el perfil del usuario.
    return render(request, 'profile.html') 

@login_required
def edit_profile(request):
    # Obtener o crear el perfil del usuario actual.
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Verificamos si la solicitud es un POST.
    if request.method == 'POST':
        # Creamos un formulario con los datos del perfil.
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        # Validamos el formulario.
        if form.is_valid():
            # Obtener los datos del formulario
            user = request.user
            new_username = form.cleaned_data.get('username')
            new_email = form.cleaned_data.get('email')

            # Validación para el username
            if new_username != user.username:
                # Comprobamos si el nuevo nombre de usuario ya está en uso por otro usuario.
                if User.objects.filter(username=new_username).exists():
                    form.add_error('username', 'Este nombre de usuario ya está en uso.')
                    return render(request, 'edit_profile.html', {'form': form})

            # Validación para el email
            if new_email != user.email:
                # Comprobamos si el nuevo email ya está en uso por otro usuario.
                if User.objects.filter(email=new_email).exists():
                    form.add_error('email', 'Este correo electrónico ya está en uso.')
                    return render(request, 'edit_profile.html', {'form': form})

            # Si los valores han cambiado, actualizamos los datos del usuario
            if new_username != user.username:
                user.username = new_username  # Actualizamos el username
            if new_email != user.email:
                user.email = new_email  # Actualizamos el email
            user.save()  # Guardamos los cambios en el usuario.

            # Guardamos los cambios en el perfil
            form.save()

            # Mensaje de éxito al usuario.
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')  # Redirigimos al perfil después de guardar.

        else:
            # Si hay errores, mostramos el formulario nuevamente con los errores.
            messages.error(request, 'Please correct the errors in the form.')
            return render(request, 'edit_profile.html', {'form': form})  # Pasamos el formulario con los errores.

    else:
        # Si la solicitud es un GET, mostramos el formulario con los datos del perfil.
        form = ProfileForm(instance=profile)

    # Renderizamos la plantilla para editar el perfil con el formulario.
    return render(request, 'edit_profile.html', {'form': form})


# Vista para mostrar la página principal.
def home(request):
    # Renderiza la plantilla 'home.html'.
    return render(request, "home.html")



def signup(request):
    errors = []  # Lista para acumular todos los errores.

    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Verificación de la longitud de la contraseña
        if len(password1) < 8:
            errors.append('La contraseña debe tener al menos 8 caracteres.')

        # Verificar si la contraseña contiene espacios
        if ' ' in password1:
            errors.append('La contraseña no puede contener espacios.')

        # Verificar si las contraseñas coinciden
        if password1 != password2:
            errors.append('Las contraseñas no coinciden.')
        
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            errors.append('El correo electrónico ya está registrado.')

        # Si hay errores, renderizamos la página con todos los errores
        if errors:
            return render(request, 'signup.html', {
                'errors': errors,  # Pasamos la lista de errores
                'form_data': request.POST  # Para mantener los datos del formulario
            })
        
        try:
            user = User.objects.create_user(
                username=request.POST['username'],
                password=password1,
                email=email
            )
            user.save()
            profile = Profile(user=user)
            if 'profile_picture' in request.FILES:
                profile.profile_picture = request.FILES['profile_picture']
            profile.save()

            return redirect('home')

        except IntegrityError:
            errors.append('El nombre de usuario ya existe.')

            return render(request, 'signup.html', {
                'errors': errors,
                'form_data': request.POST,
            })

    return render(request, 'signup.html')






# Vista para mostrar las tareas pendientes del usuario autenticado.
@login_required
def tasks(request):
    # Filtramos las tareas que no están completadas y pertenecen al usuario actual.
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)

    # Configuramos el paginador para mostrar 4 tareas por página.
    paginator = Paginator(tasks, 4)

    # Obtenemos el número de página desde la solicitud (GET).
    page_number = request.GET.get('page')

    # Obtenemos las tareas para la página actual.
    page_obj = paginator.get_page(page_number)

    # Renderizamos la plantilla 'tasks.html' con las tareas paginadas.
    return render(request, 'tasks.html', {'page_obj': page_obj})

# Vista para cerrar sesión del usuario autenticado.
@login_required
def signout(request):
    logout(request)  # Cerramos la sesión del usuario.
    return redirect('home')  # Redirigimos a la página principal.

# Vista para iniciar sesión.
def signin(request):
    # Verificamos si la solicitud es un GET.
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm  # Mostramos el formulario de autenticación.
        })
    else:
        # Obtenemos el nombre de usuario y la contraseña del formulario.
        username = request.POST['username']
        password = request.POST['password']

        # Verificamos que los campos no estén vacíos.
        if not username or not password:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'El nombre de usuario y la contraseña no pueden estar vacíos'
            })

        # Intentamos autenticar al usuario.
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Si la autenticación falla, mostramos un mensaje de error.
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Usuario o contraseña incorrectos'
            })
        else:
            # Si la autenticación es exitosa, iniciamos sesión y redirigimos a tareas.
            login(request, user)
            return redirect('tasks')




def create_task(request):
    # Verificamos si la solicitud es un POST.
    if request.method == 'POST':
        # Creamos un formulario con los datos de la tarea.
        form = TaskForm(request.POST, request.FILES)
        
        # Validamos si el formulario es válido
        if form.is_valid():
            new_task = form.save(commit=False)

            # Verificamos si la fecha límite está en el pasado
            if new_task.deadline and new_task.deadline < timezone.now():
                form.add_error('deadline', 'La fecha límite no puede ser anterior al momento actual.')
                return render(request, 'create_task.html', {'form': form})
            
            # Limitar los segundos a 00 al momento de guardar la tarea
            if new_task.deadline:
                new_task.deadline = new_task.deadline.replace(second=0, microsecond=0)

            new_task.user = request.user  # Asignamos la tarea al usuario actual.
            new_task.email = request.user.email  # Asignamos el correo del usuario al campo email.
            new_task.save()  # Guardamos la tarea en la base de datos.

            messages.success(request, 'Tarea creada exitosamente!')  # Mensaje de éxito.
            return redirect('tasks')  # Redirigimos a la lista de tareas.
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')
            return render(request, 'create_task.html', {'form': form})
    else:
        form = TaskForm()

    return render(request, 'create_task.html', {'form': form})




# Vista para mostrar los detalles de una tarea específica.
@login_required
def task_detail(request, task_id):
    # Obtenemos la tarea utilizando su ID y verificamos que pertenezca al usuario.
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'GET':
        form = TaskForm(instance=task)  # Creamos un formulario con los datos de la tarea.
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            form = TaskForm(request.POST, request.FILES, instance=task)  # Creamos el formulario con los datos del POST.
            
            # Verificamos si la fecha límite está en el futuro
            if form.is_valid():
                new_task = form.save(commit=False)
                
                # Validación: si la fecha límite es posterior a la fecha actual, mostrar error
                if new_task.deadline and new_task.deadline < timezone.now():
                    form.add_error('deadline', 'La fecha límite no puede ser anterior al momento actual.')
                    return render(request, 'task_detail.html', {'task': task, 'form': form})
                
                # Limitar los segundos a 00 al momento de guardar la tarea
                if new_task.deadline:
                    new_task.deadline = new_task.deadline.replace(second=0, microsecond=0)

                new_task.save()  # Guardamos los cambios en la tarea
                return redirect('tasks')  # Redirigimos a la lista de tareas

            # Si el formulario no es válido, mostramos los errores
            else:
                return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Por favor, corrija los errores en el formulario.'})

        except ValueError:
            # Si ocurre un error al actualizar, mostramos un mensaje de error.
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error al actualizar'})



@login_required
def complete_task(request, task_id):
    # Obtenemos la tarea utilizando su ID y verificamos que pertenezca al usuario.
    task = get_object_or_404(Task, pk=task_id, user=request.user)

    # Si la tarea ya está completada, no permitir cambios.
    if task.datecompleted:
        return redirect('tasks')  # Redirigir a la lista de tareas si la tarea ya está completada.

    if request.method == 'POST':
        task.datecompleted = timezone.now()  # Establecemos la fecha de completado.
        task.save()  # Guardamos los cambios en la tarea.
        return redirect('tasks')  # Redirigimos a la lista de tareas.

    return render(request, 'tasks/task_detail.html', {'task': task})

# Vista para eliminar una tarea.
@login_required
def delete_task(request, task_id):
    # Obtenemos la tarea utilizando su ID y verificamos que pertenezca al usuario.
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()  # Establecemos la fecha de completado antes de eliminar.
        task.delete()  # Eliminamos la tarea de la base de datos.
        return redirect('tasks')  # Redirigimos a la lista de tareas.

# Vista para mostrar las tareas completadas del usuario.
@login_required
def tasks_completed(request):
    # Filtramos las tareas que están completadas y pertenecen al usuario actual.
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    paginator = Paginator(tasks, 4)  # Configuramos el paginador para mostrar 4 tareas por página.
    page_number = request.GET.get('page')  # Obtenemos el número de página desde la solicitud.
    page_obj = paginator.get_page(page_number)  # Obtenemos las tareas para la página actual.

    # Renderizamos la plantilla 'tasks.html' con las tareas completadas paginadas.
    return render(request, 'tasks.html', {'page_obj': page_obj})

# Vista para mostrar todas las tareas (incluidas las completadas).
def task_list(request):
    tasks = Task.objects.all()  # Obtenemos todas las tareas de la base de datos.
    paginator = Paginator(tasks, 4)  # Configuramos el paginador para mostrar 4 tareas por página.
    page_number = request.GET.get('page')  # Obtenemos el número de página desde la solicitud.
    page_obj = paginator.get_page(page_number)  # Obtenemos las tareas para la página actual.
    
    # Renderizamos la plantilla 'task.html' con todas las tareas paginadas.
    return render(request, 'task.html', {'page_obj': page_obj})