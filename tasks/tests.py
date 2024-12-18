import tempfile
import os
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from io import BytesIO
from PIL import Image
from django.conf import settings
from .models import Task
from django.utils import timezone
from django.core.paginator import Paginator


class SignupTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear un usuario y perfil asociados para las pruebas
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile = Profile.objects.create(user=self.user)

        # Configurar un directorio temporal para almacenar los archivos en las pruebas
        self.test_media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.test_media_root

    def tearDown(self):
        """Limpiar los archivos temporales después de las pruebas"""
        if os.path.exists(self.test_media_root):
            os.rmdir(self.test_media_root)

    def test_signup_passwords_do_not_match(self):
        """Test case for signup with non-matching passwords"""
        data = {
            'username': 'newuser',
            'password1': 'password123',
            'password2': 'password124',  # Contraseñas no coinciden
            'email': 'newuser@example.com'
        }

        response = self.client.post(reverse('signup'), data)

        # Verificar que el formulario se vuelve a cargar con un mensaje de error
        self.assertContains(response, 'Las contraseñas no coinciden')

   

    def test_create_profile_when_not_exists(self):
        """Test case where profile is created if it doesn't exist"""
        # Crear un nuevo usuario que no tiene un perfil
        new_user = User.objects.create_user(username='newuser', password='password123')
        
        # Simular el inicio de sesión de este nuevo usuario
        self.client.login(username='newuser', password='password123')
        
        response = self.client.get(reverse('edit_profile'))  # Accedemos a la vista
        # Verificar que se crea un perfil automáticamente para el nuevo usuario
        self.assertTrue(Profile.objects.filter(user=new_user).exists())
        
        # Verificar que la vista se carga correctamente
        self.assertEqual(response.status_code, 200)


class EditProfileTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear un usuario y perfil asociados para las pruebas
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile = Profile.objects.create(user=self.user)

    def test_edit_profile_get_request(self):
        """Test GET request to edit profile page"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('edit_profile'))
    
        # Verificar que el status es 200 (ok) y que se está renderizando el formulario
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')
        # Verificar que el formulario contiene los campos de 'username' y 'email'
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')

    def test_edit_profile_post_valid_data(self):
        """Test POST request to update profile with valid data"""
        self.client.login(username='testuser', password='password123')

        # Crear una imagen temporal para probar
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        # Crear un archivo simulado para la imagen
        uploaded_image = SimpleUploadedFile('test_image.jpg', image_io.read(), content_type='image/jpeg')

        data = {
            'username': 'newusername',
            'email': 'newemail@example.com',
            'profile_picture': uploaded_image,  # Usamos una imagen válida
        }
        response = self.client.post(reverse('edit_profile'), data)
        
        # Verificar que los datos fueron guardados correctamente
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertTrue(self.profile.profile_picture)  # Verificar que la imagen ha sido guardada
        
        # Verificar el mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Profile updated successfully!')
        self.assertRedirects(response, reverse('profile'))  # Verificar que se redirige correctamente
class SignoutTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear un usuario para probar el logout
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_signout_redirects_to_home(self):
        """Verificar que el usuario es redirigido a la página de inicio después de hacer logout"""
        # Iniciar sesión con el usuario
        self.client.login(username='testuser', password='password123')
        
        # Verificar que el usuario está autenticado antes del logout
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        
        # Realizar la solicitud de logout
        response = self.client.get(reverse('signout'))  # Llamar a la vista de logout
        
        # Verificar que el usuario ha sido desconectado (la sesión debe estar cerrada)
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Verificar que el usuario es redirigido a la página de inicio
        self.assertRedirects(response, reverse('home'))


class SigninTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(username='testuser', password='password123')
    
    def test_signin_get_request(self):
        """Test GET request to signin page"""
        # Realizar una solicitud GET para acceder al formulario de inicio de sesión
        response = self.client.get(reverse('signin'))

        # Verificar que el formulario se está renderizando correctamente
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signin.html')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
    
    def test_signin_post_valid_data(self):
        """Test POST request to signin with valid credentials"""
        # Realizar una solicitud POST con los datos de inicio de sesión correctos
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(reverse('signin'), data)

        # Verificar que el usuario ha iniciado sesión correctamente y es redirigido
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertRedirects(response, reverse('tasks'))  # Verifica la redirección a la página 'tasks'

    def test_signin_post_invalid_data(self):
        """Test POST request to signin with invalid credentials"""
        # Realizar una solicitud POST con credenciales incorrectas
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('signin'), data)

        # Verificar que se muestra el error correspondiente
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario o contraseña incorrectos')

    def test_signin_post_empty_fields(self):
        """Test POST request with empty username or password"""
        # Realizar una solicitud POST con campos vacíos
        data = {
            'username': '',  # Usuario vacío
            'password': 'password123'
        }
        response = self.client.post(reverse('signin'), data)

        # Verificar que se muestra el error de campos vacíos
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El nombre de usuario y la contraseña no pueden estar vacíos')

        # Realizar una solicitud POST con el campo 'username' vacío
        data = {
            'username': 'testuser',
            'password': ''
        }
        response = self.client.post(reverse('signin'), data)

        # Verificar que se muestra el error de campos vacíos
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'El nombre de usuario y la contraseña no pueden estar vacíos')

class CreateTaskTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Crear un usuario para las pruebas
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.login(username='testuser', password='password123')

    def test_create_task_get_request(self):
        """Test GET request to create task page"""
        # Realizar una solicitud GET para acceder al formulario de creación de tarea
        response = self.client.get(reverse('create_task'))

        # Verificar que el formulario de tarea se está renderizando correctamente
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="description"')

    


class TaskDetailViewTest(TestCase):

    def setUp(self):
        """Set up test user and task"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            user=self.user
        )
        self.client.login(username='testuser', password='12345')

    

    def test_task_detail_post_valid(self):
        """Test that the task is updated with valid data on POST request"""
        updated_data = {
            'title': 'Updated Task',
            'description': 'This is an updated task description',
            'important': False,
            'deadline': '2024-12-31T23:59',
        }
        
        response = self.client.post(reverse('task_detail', kwargs={'task_id': self.task.id}), updated_data)

        # Verificar que la tarea se ha redirigido correctamente a la página de tareas
        self.assertRedirects(response, reverse('tasks'))
        
        # Verificar que la tarea se ha actualizado en la base de datos
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.description, 'This is an updated task description')

   


class CompleteTaskViewTest(TestCase):

    def setUp(self):
        """Set up test user and tasks"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            user=self.user
        )
        self.client.login(username='testuser', password='12345')

    def test_complete_task_post(self):
        """Test completing a task successfully"""
        task_id = self.task.id
        
        # Realizar la solicitud POST para completar la tarea
        response = self.client.post(reverse('complete_task', kwargs={'task_id': task_id}))

        # Verificar que la respuesta redirige a la página de tareas
        self.assertRedirects(response, reverse('tasks'))
        
        # Verificar que la fecha de finalización de la tarea ha sido actualizada
        self.task.refresh_from_db()
        self.assertIsNotNone(self.task.datecompleted)
        self.assertTrue(self.task.datecompleted <= timezone.now())

    def test_complete_task_not_owner(self):
        """Test that a user cannot complete a task that doesn't belong to them"""
        self.client.login(username='otheruser', password='12345')
        task_id = self.task.id

        # Intentar completar la tarea que pertenece a otro usuario
        response = self.client.post(reverse('complete_task', kwargs={'task_id': task_id}))

        # Verificar que se recibe un error 404, ya que el usuario no es el propietario
        self.assertEqual(response.status_code, 404)

    def test_complete_task_task_not_found(self):
        """Test that the task returns a 404 if the task does not exist"""
        # Crear un ID de tarea no existente
        non_existent_task_id = 9999
        
        # Intentar completar una tarea que no existe
        response = self.client.post(reverse('complete_task', kwargs={'task_id': non_existent_task_id}))

        # Verificar que la respuesta es un error 404
        self.assertEqual(response.status_code, 404)

class DeleteTaskViewTest(TestCase):

    def setUp(self):
        """Set up test user and tasks"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        
        self.task = Task.objects.create(
            title='Test Task',
            description='This is a test task',
            user=self.user
        )
        self.client.login(username='testuser', password='12345')

    def test_delete_task_post(self):
        """Test deleting a task successfully"""
        task_id = self.task.id

        # Realizar la solicitud POST para eliminar la tarea
        response = self.client.post(reverse('delete_task', kwargs={'task_id': task_id}))

        # Verificar que la respuesta redirige a la página de tareas
        self.assertRedirects(response, reverse('tasks'))

        # Verificar que la tarea ha sido eliminada de la base de datos
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=task_id)

    def test_delete_task_not_owner(self):
        """Test that a user cannot delete a task that doesn't belong to them"""
        self.client.login(username='otheruser', password='12345')
        task_id = self.task.id

        # Intentar eliminar la tarea que pertenece a otro usuario
        response = self.client.post(reverse('delete_task', kwargs={'task_id': task_id}))

        # Verificar que se recibe un error 404, ya que el usuario no es el propietario
        self.assertEqual(response.status_code, 404)

    def test_delete_task_task_not_found(self):
        """Test that the task returns a 404 if the task does not exist"""
        # Crear un ID de tarea no existente
        non_existent_task_id = 9999
        
        # Intentar eliminar una tarea que no existe
        response = self.client.post(reverse('delete_task', kwargs={'task_id': non_existent_task_id}))

        # Verificar que la respuesta es un error 404
        self.assertEqual(response.status_code, 404)




class TasksCompletedViewTest(TestCase):

    def setUp(self):
        """Set up test user and tasks"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        
        # Crear tareas completadas para el usuario de prueba
        self.completed_task_1 = Task.objects.create(
            title='Completed Task 1',
            description='Description 1',
            user=self.user,
            datecompleted=timezone.now()
        )
        self.completed_task_2 = Task.objects.create(
            title='Completed Task 2',
            description='Description 2',
            user=self.user,
            datecompleted=timezone.now()
        )
        self.completed_task_3 = Task.objects.create(
            title='Completed Task 3',
            description='Description 3',
            user=self.user,
            datecompleted=timezone.now()
        )
        self.completed_task_4 = Task.objects.create(
            title='Completed Task 4',
            description='Description 4',
            user=self.user,
            datecompleted=timezone.now()
        )
        self.completed_task_5 = Task.objects.create(
            title='Completed Task 5',
            description='Description 5',
            user=self.user,
            datecompleted=timezone.now()
        )
        
        # Tareas completadas para otro usuario
        self.other_user_task = Task.objects.create(
            title='Other User Task',
            description='Description for another user',
            user=self.other_user,
            datecompleted=timezone.now()
        )

        self.client.login(username='testuser', password='12345')



    def test_tasks_completed_no_tasks(self):
        """Test that the tasks_completed view shows no tasks if there are none for the user"""
        # Borrar las tareas completadas para el usuario de prueba
        Task.objects.filter(user=self.user).delete()

        response = self.client.get(reverse('tasks_completed'))

        # Verificar que la respuesta es 200 OK
        self.assertEqual(response.status_code, 200)

        # Verificar que no hay tareas en la página
        self.assertNotContains(response, 'Completed Task 1')
        self.assertNotContains(response, 'Completed Task 2')

    

    def test_tasks_completed_user_not_owner(self):
        """Test that a user cannot see tasks from another user"""
        # Hacer login con otro usuario
        self.client.login(username='otheruser', password='12345')

        response = self.client.get(reverse('tasks_completed'))

        # Verificar que el usuario "otheruser" no puede ver las tareas del primer usuario
        self.assertNotContains(response, 'Completed Task 1')
        self.assertNotContains(response, 'Completed Task 2')
        self.assertNotContains(response, 'Completed Task 3')
        self.assertNotContains(response, 'Completed Task 4')
        self.assertNotContains(response, 'Completed Task 5')

        # Verificar que solo ve su propia tarea
        self.assertContains(response, 'Other User Task')


