from django.urls import path
from . import views
from .views import index, baixar_pdf, historico


urlpatterns = [
    path('', views.index, name='index'),
    path('baixar-pdf/', views.baixar_pdf, name='baixar_pdf'),
    path('historico/', historico, name='historico'),
]
