import os
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from .forms import PerguntaForm
from dotenv import load_dotenv
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import HistoricoPergunta  

load_dotenv()

def extrair_texto_da_url(url):
    resposta = requests.get(url)
    sopa = BeautifulSoup(resposta.text, 'html.parser')
    return sopa.get_text()

def perguntar_llama(texto, pergunta):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('API_KEY')}",
        "Content-Type": "application/json"
    }

    # Simula "páginas" de até 1000 caracteres
    chunk_size = 1000
    chunk_list = [texto[i:i+chunk_size] for i in range(0, len(texto), chunk_size)]
    texto_final = "\n".join(chunk_list)

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "Responda com base no conteúdo fornecido."},
            {"role": "user", "content": f"Texto extraído:\n{texto_final}\n\nPergunta:\n{pergunta}"}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        resposta = response.json()['choices'][0]['message']['content']
        return resposta, len(chunk_list)
    else:
        return f"Erro ao chamar a LLM: {response.status_code} - {response.text}", 0

def index(request):
    resposta = None
    total_paginas = 0

    if request.method == 'POST':
        form = PerguntaForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            pergunta = form.cleaned_data['pergunta']
            texto = extrair_texto_da_url(url)
            resposta, total_paginas = perguntar_llama(texto, pergunta)

            # Salva no histórico
            HistoricoPergunta.objects.create(
                url=url,
                pergunta=pergunta,
                resposta=resposta
            )
    else:
        form = PerguntaForm()

    return render(request, 'portal/index.html', {
        'form': form,
        'resposta': resposta,
        'total_paginas': total_paginas
    })

from django.template.loader import get_template
from xhtml2pdf import pisa

def baixar_pdf(request):
    url = request.GET.get('url', '')
    pergunta = request.GET.get('pergunta', '')
    resposta = request.GET.get('resposta', '')

    template_path = 'portal/pdf_template.html'
    context = {'url': url, 'pergunta': pergunta, 'resposta': resposta}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resposta.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f'Erro ao gerar PDF: {pisa_status.err}')
    return response

def historico(request):
    registros = HistoricoPergunta.objects.order_by('-data')
    return render(request, 'portal/historico.html', {'registros': registros})
