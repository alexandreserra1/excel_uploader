# myapp/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Página inicial (Upload)
    path('', views.upload_base_completa, name='upload-base-completa'),
    path('upload-atualizacao/', views.upload_atualizacao_ade, name='upload-atualizacao-ade'),
    
    # Exportação
    path('export/excel/', views.export_contratos_excel, name='export-excel'),
    path('export/matriz-diaria/', views.export_matriz_diaria, name='export-matriz'),
    
    # Painéis
    path('dashboard/recusas/', views.painel_recusas, name='painel-recusas'),
    path('dashboard/saldos/', views.painel_saldos, name='painel-saldos'),
    
    # Adicionar estas rotas para API
    path('api/contratos/', views.ContratoListCreateView.as_view(), name='contrato-list'),
    path('api/contratos/<int:pk>/', views.ContratoDetailView.as_view(), name='contrato-detail'),
    path('api/contratos/ade/<str:ade>/', views.ContratoAdeDetailView.as_view(), name='contrato-ade'),
]
