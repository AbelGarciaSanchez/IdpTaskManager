# TaskManager
## Introducción
TaskManager es una plataforma diseñada para facilitar la creación, gestión y seguimiento de tareas. Este proyecto busca mejorar la experiencia del usuario al proporcionar herramientas eficientes para administrar tareas tanto en entornos laborales como en el día a día personal.
## Identificación de las Necesidades del Proyecto
### 1. Gestión de Tareas
La gestión de tareas es una necesidad fundamental que permite organizar, priorizar y realizar un seguimiento eficiente de las actividades pendientes. TaskManager se enfoca en ofrecer una solución integral que mejore la productividad y la organización personal a través de una interfaz intuitiva.
### 2. Creación de Tareas
Los usuarios podrán crear nuevas tareas de manera rápida y sencilla, indicando:
- **Título**: Nombre descriptivo que permite identificar la tarea.
- **Descripción**: Información adicional sobre la actividad.
- **Fecha**: Plazos que ayudan a priorizar y organizar tareas.
- **Importancia**: Clasificación según la relevancia, para una mejor gestión del tiempo.
### 3. Actualización de Tareas
TaskManager permite modificar y actualizar tareas según el progreso. Las funcionalidades incluyen:
- Marcar tareas como completadas.
- Edición de detalles como descripción, fecha de vencimiento o importancia.
### 4. Eliminación de Tareas
Los usuarios pueden eliminar tareas que ya no son relevantes, ayudando a mantener la lista de tareas organizada y optimizando el uso del sistema.
### 5. Visualización Clara
Una interfaz eficiente permite a los usuarios visualizar rápidamente las tareas pendientes y completadas.
### 6. Accesibilidad
La plataforma es accesible desde distintos dispositivos, facilitando la gestión de tareas en cualquier lugar.
## Análisis y Comparativa con Alternativas del Mercado
A pesar de la existencia de aplicaciones como Todoist, Trello y Asana, TaskManager se distingue por su simplicidad, eficiencia y accesibilidad en la gestión de tareas individuales.
## Justificación del Proyecto
La necesidad de una plataforma eficiente para la gestión de tareas y proyectos ha dado origen a TaskManager, que brinda una solución práctica y fácil de usar, garantizando una experiencia de usuario fluida.
## Uso de Stack Tecnológico
### 1. Back-End
- **Python con Django**: Para la lógica del back-end, permitiendo un desarrollo rápido y eficiente.
- **Bootstrap 5**: Para estilos y diseño de la interfaz.
- **Base de datos integrada con Django**: Para un desarrollo ágil.
### 2. Front-End
- **Bootstrap 5**: Diseño y estilos responsivos.
- **Visual Studio Code**: Herramienta para el desarrollo del front-end con React.
## Flujo de Trabajo de TaskManager
```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant Database
    User->>Frontend: Crear Tarea
    Frontend->>Backend: Enviar datos de la tarea
    Backend->>Database: Guardar tarea
    Database-->>Backend: Confirmación
    Backend-->>Frontend: Tarea creada
    Frontend-->>User: Mostrar tarea
