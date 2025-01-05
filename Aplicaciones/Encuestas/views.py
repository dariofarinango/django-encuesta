from django import forms
from django.forms import formset_factory
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Encuesta,  Pregunta, Respuesta, Envio, Opcion
from .forms import EncuestaForm, PreguntaForm, OpcionForm, RespuestaForm, BaseRespuestaFormSet
#para hacer el conteo de las respuestas



# -----------------------listado de las enceutas---------------------

def encuesta_list(request):
    """El usuario puede ver todas sus encuestas"""
    encuestas = Encuesta.objects.all().order_by("-creada_en")  # Sin filtro de "esta_activa"
    encuesta = encuestas.first()  # O la lógica que necesites para obtener una encuesta específica
    return render(request, "encuesta/lista.html", {"encuestas": encuestas, "encuesta": encuesta})


#----------------------listado en curos de las encuestas----------
def encuestas_en_curso(request):
    """Muestra las encuestas que están en curso."""
    encuestas = Encuesta.objects.filter(esta_activa=True).order_by("-creada_en")
    return render(request, "encuesta/encurso.html", {"encuestas": encuestas})





def detalle(request, pk):
    """El usuario puede ver una encuesta activa"""
    try:
        encuesta = Encuesta.objects.prefetch_related("pregunta_set__opcion_set").get(
            pk=pk, esta_activa=True
        )
    except Encuesta.DoesNotExist:
        raise Http404()

    preguntas = encuesta.pregunta_set.all()

    # Calcular los resultados.
    for pregunta in preguntas:
        opcion_pks = pregunta.opcion_set.values_list("pk", flat=True)
        total_respuestas = Respuesta.objects.filter(opcion_id__in=opcion_pks).count()
        for opcion in pregunta.opcion_set.all():
            num_respuestas = Respuesta.objects.filter(opcion=opcion).count()
            opcion.percent = 100.0 * num_respuestas / total_respuestas if total_respuestas else 0

    host = request.get_host()
    public_path = reverse("encuesta-iniciar", args=[pk])
    public_url = f"{request.scheme}://{host}{public_path}"
    num_envios = encuesta.envio_set.filter(esta_completo=True).count()
    return render(
        request,
        "encuesta/detalle.html",
        {
            "encuesta": encuesta,
            "public_url": public_url,
            "preguntas": preguntas,
            "num_envios": num_envios,
        },
    )




def crear(request):
    """El usuario puede crear una nueva encuesta"""
    if request.method == "POST":
        form = EncuestaForm(request.POST)
        if form.is_valid():
            encuesta = form.save(commit=False)
            encuesta.save()
            return redirect("encuesta-editar", pk=encuesta.id)
    else:
        form = EncuestaForm()

    return render(request, "encuesta/crear.html", {"form": form})

def eliminar(request, pk):
    """El usuario puede eliminar una encuesta existente"""
    encuesta = get_object_or_404(Encuesta, pk=pk)
    if request.method == "POST":
        encuesta.delete()

    return redirect("encuesta-lista")

def editar(request, pk):
    """El usuario puede agregar preguntas a una encuesta en borrador y luego activarla"""
    try:
        encuesta = Encuesta.objects.prefetch_related("pregunta_set__opcion_set").get(
            pk=pk, esta_activa=False
        )
    except Encuesta.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        encuesta.esta_activa = True
        encuesta.save()
        return redirect("encuesta-detalle", pk=pk)
    else:
        preguntas = encuesta.pregunta_set.all()
        return render(request, "encuesta/editar.html", {"encuesta": encuesta, "preguntas": preguntas})

def pregunta_crear(request, pk):
    """El usuario puede agregar una pregunta a una encuesta en borrador"""
    encuesta = get_object_or_404(Encuesta, pk=pk)
    if request.method == "POST":
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.encuesta = encuesta
            pregunta.save()
            return redirect("encuesta-opcion-crear", encuesta_pk=pk, pregunta_pk=pregunta.pk)
    else:
        form = PreguntaForm()

    return render(request, "encuesta/pregunta.html", {"encuesta": encuesta, "form": form})

def opcion_crear(request, encuesta_pk, pregunta_pk):
    """El usuario puede agregar opciones a una pregunta de encuesta"""
    encuesta = get_object_or_404(Encuesta, pk=encuesta_pk)
    pregunta = Pregunta.objects.get(pk=pregunta_pk)
    if request.method == "POST":
        form = OpcionForm(request.POST)
        if form.is_valid():
            opcion = form.save(commit=False)
            opcion.pregunta_id = pregunta_pk
            opcion.save()
    else:
        form = OpcionForm()

    opciones = pregunta.opcion_set.all()
    return render(
        request,
        "encuesta/opciones.html",
        {"encuesta": encuesta, "pregunta": pregunta, "opciones": opciones, "form": form},
    )

def iniciar(request, pk):
    """El encuestado puede iniciar una encuesta"""
    encuesta = get_object_or_404(Encuesta, pk=pk, esta_activa=True)
    if request.method == "POST":
        envio = Envio.objects.create(encuesta=encuesta)
        return redirect("encuesta-enviar", encuesta_pk=pk, envio_pk=envio.pk)

    return render(request, "encuesta/iniciar.html", {"encuesta": encuesta})

def enviar(request, encuesta_pk, envio_pk):
    """El encuestado envía sus respuestas completadas"""
    try:
        encuesta = Encuesta.objects.prefetch_related("pregunta_set__opcion_set").get(
            pk=encuesta_pk, esta_activa=True
        )
    except Encuesta.DoesNotExist:
        raise Http404()

    try:
        envio = encuesta.envio_set.get(pk=envio_pk, esta_completo=False)
    except Envio.DoesNotExist:
        raise Http404()

    preguntas = encuesta.pregunta_set.all()
    opciones = [p.opcion_set.all() for p in preguntas]
    form_kwargs = {"empty_permitted": False, "opciones": opciones}
    RespuestaFormSet = formset_factory(RespuestaForm, extra=len(preguntas), formset=BaseRespuestaFormSet)
    if request.method == "POST":
        formset = RespuestaFormSet(request.POST, form_kwargs=form_kwargs)
        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    Respuesta.objects.create(
                        opcion_id=form.cleaned_data["opcion"], envio_id=envio_pk,
                    )

                envio.esta_completo = True
                envio.save()
            return redirect("encuesta-gracias", pk=encuesta_pk)

    else:
        formset = RespuestaFormSet(form_kwargs=form_kwargs)

    pregunta_forms = zip(preguntas, formset)
    return render(
        request,
        "encuesta/enviar.html",
        {"encuesta": encuesta, "pregunta_forms": pregunta_forms, "formset": formset},
    )

def gracias(request, pk):
    """El encuestado recibe un mensaje de agradecimiento"""
    encuesta = get_object_or_404(Encuesta, pk=pk, esta_activa=True)
    return render(request, "encuesta/gracias.html", {"encuesta": encuesta})

#----------------la grafica de la encuesta en curso----------------
def resultados(request):
    """Muestra los resultados de todas las encuestas activas con porcentajes de respuestas."""
    encuestas = Encuesta.objects.filter(esta_activa=True)  # Encuestas activas

    resultados = []
    for encuesta in encuestas:
        # Obtenemos las preguntas de la encuesta
        encuesta_resultados = []
        for pregunta in encuesta.pregunta_set.all():
            # Obtenemos las opciones de cada pregunta
            opciones = pregunta.opcion_set.all()
            total_respuestas = Respuesta.objects.filter(opcion__pregunta=pregunta).count()

            # Calculamos las respuestas por opción y el porcentaje
            opciones_respuestas = []
            for opcion in opciones:
                conteo = Respuesta.objects.filter(opcion=opcion).count()
                porcentaje = (conteo / total_respuestas * 100) if total_respuestas > 0 else 0
                opciones_respuestas.append({
                    'opcion': opcion.texto,
                    'conteo': conteo,
                    'porcentaje': round(porcentaje, 2)  # Redondeamos a dos decimales
                })

            encuesta_resultados.append({
                'pregunta': pregunta.enunciado,
                'opciones': opciones_respuestas,
            })

        # Agregamos los resultados de la encuesta
        resultados.append({
            'titulo': encuesta.titulo,
            'resultados': encuesta_resultados,
            'num_envios': encuesta.envio_set.filter(esta_completo=True).count(),
        })

    return render(request, "encuesta/resultados.html", {
        "resultados": resultados,
    })

#----------------------------configuraicon de la en cuesta--------------
def configuracion(request):
    """Vista para modificar configuraciones de la encuesta"""
    encuesta = Encuesta.objects.first()  # Se obtiene la primera encuesta, puedes adaptarlo como quieras.
    
    if request.method == "POST":
        form = EncuestaForm(request.POST, instance=encuesta)
        if form.is_valid():
            form.save()
    else:
        form = EncuestaForm(instance=encuesta)

    return render(request, "encuesta/configuracion.html", {"form": form, "encuesta": encuesta})