from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('baixar-pdf/', views.baixar_pdf, name='baixar_pdf'),
]
