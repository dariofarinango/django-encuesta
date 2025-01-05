from django.urls import path, include  # Agregamos include

from django.conf import settings  # Importamos la configuración de Django
from . import views  # Importamos las vistas del archivo views.py

urlpatterns = [
    # Rutas para encuestas
    path("", views.encuesta_list, name="encuesta-lista"),  # Página de lista de encuestas
    path("encuesta/<int:pk>/", views.detalle, name="encuesta-detalle"),  # Detalle de encuesta
    path("encuesta/crear/", views.crear, name="encuesta-crear"),  # Crear una nueva encuesta
    path("encuesta/<int:pk>/eliminar/", views.eliminar, name="encuesta-eliminar"),  # Eliminar una encuesta
    path("encuesta/<int:pk>/editar/", views.editar, name="encuesta-editar"),  # Editar una encuesta

    # Rutas para gestionar preguntas y opciones
    path("encuesta/<int:pk>/pregunta/crear/", views.pregunta_crear, name="encuesta-pregunta-crear"),  # Crear una pregunta
    path("encuesta/<int:encuesta_pk>/pregunta/<int:pregunta_pk>/opcion/crear/", views.opcion_crear, name="encuesta-opcion-crear"),  # Crear una opción

    # Rutas para iniciar y enviar respuestas de una encuesta
    
    path("encuesta/<int:pk>/iniciar/", views.iniciar, name="encuesta-iniciar"),  # Iniciar encuesta
    path("encuesta/<int:encuesta_pk>/enviar/<int:envio_pk>/", views.enviar, name="encuesta-enviar"),  # Enviar respuestas

    # Ruta para mostrar mensaje de agradecimiento después de enviar las respuestas
    path("encuesta/<int:pk>/gracias/", views.gracias, name="encuesta-gracias"),  

    # -----------------------listado de las enceutas encur.html---------------------
    path("encuestas/en-curso/", views.encuestas_en_curso, name="encuesta-en-curso"),
    #-----------------------url de resultado.html--------------------
    path('resultados/', views.resultados, name='resultados'),
        # --------------configuracion de la encuetas---------------------
    path('configuracion/', views.configuracion, name='configuracion'),  # Ruta de configuración

    


]

# Agregar el panel de depuración si estamos en modo de desarrollo
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns