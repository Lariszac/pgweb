from django import forms

class PerguntaForm(forms.Form):
    url = forms.URLField(label='URL do site', required=True)
    pergunta = forms.CharField(label='Sua pergunta', widget=forms.Textarea, required=True)