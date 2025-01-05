from django import forms
from .models import Encuesta, Pregunta, Opcion, Respuesta


class EncuestaForm(forms.ModelForm):
    class Meta:
        model = Encuesta
        fields = ["titulo"]


class PreguntaForm(forms.ModelForm):
    class Meta:
        model = Pregunta
        fields = ["enunciado"]


class OpcionForm(forms.ModelForm):
    class Meta:
        model = Opcion
        fields = ["texto"]


class RespuestaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        opciones = kwargs.pop("opciones")
        # Las opciones deben ser una lista de objetos Opcion
        choices = [(o.pk, o.texto) for o in opciones]
        super().__init__(*args, **kwargs)
        opcion_field = forms.ChoiceField(choices=choices, widget=forms.RadioSelect, required=True)
        self.fields["opcion"] = opcion_field


class BaseRespuestaFormSet(forms.BaseFormSet):
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs["opciones"] = kwargs["opciones"][index]
        return kwargs

