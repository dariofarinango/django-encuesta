# Create your models here.

from django.db import models

from django.utils import timezone

class Encuesta(models.Model):
    """Una encuesta creada por un usuario."""

    titulo = models.CharField(max_length=64)
    esta_activa = models.BooleanField(default=False)

    creada_en = models.DateTimeField(default=timezone.now)

class Pregunta(models.Model):
    """Una pregunta en una encuesta"""

    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    enunciado = models.CharField(max_length=128)

class Opcion(models.Model):
    """Una opción de elección múltiple disponible como parte de una pregunta de encuesta."""

    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    texto = models.CharField(max_length=128)

class Envio(models.Model):
    """Un conjunto de respuestas a las preguntas de una encuesta."""

    encuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(default=timezone.now)
    esta_completo = models.BooleanField(default=False)

class Respuesta(models.Model):
    """Una respuesta a una pregunta de encuesta."""

    envio = models.ForeignKey(Envio, on_delete=models.CASCADE)
    opcion = models.ForeignKey(Opcion, on_delete=models.CASCADE)
