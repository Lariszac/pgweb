from django.db import models

# Create your models here.

from django.db import models

class HistoricoPergunta(models.Model):
    url = models.URLField()
    pergunta = models.TextField()
    resposta = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
