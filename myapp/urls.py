# myapp/urls.py

from django.urls import path
from .views import (
    ContratoListCreateView,
    ContratoDetailView,
    ContratoAdeDetailView,
    upload_base_completa,
    upload_atualizacao_ade,
)

urlpatterns = [
    path('upload/', upload_base_completa, name='upload-base-completa'),
    path('upload-atualizacao/', upload_atualizacao_ade, name='upload-atualizacao-ade'),
    path('contratos/', ContratoListCreateView.as_view(), name='contrato-list'),
    path('contratos/<int:pk>/', ContratoDetailView.as_view(), name='contrato-detail'),
    path('contratos/ade/<str:ade>/', ContratoAdeDetailView.as_view(), name='contrato-ade-detail'),
]
