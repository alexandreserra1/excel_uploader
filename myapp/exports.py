from django.http import HttpResponse
import pandas as pd
from .models import Contrato
from datetime import datetime

def export_to_excel(queryset, filename=None):
    """
    Função genérica para exportar queryset para Excel
    """
    if filename is None:
        filename = f"contratos_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    # Converter queryset para DataFrame
    df = pd.DataFrame.from_records(queryset.values())
    
    # Converter campos datetime para timezone unaware
    datetime_columns = ['data_inclusao']  # Adicione outros campos datetime se houver
    for col in datetime_columns:
        if col in df.columns:
            df[col] = df[col].dt.tz_localize(None)
    
    # Criar response com Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Salvar DataFrame como Excel
    df.to_excel(response, index=False)
    return response

def export_matriz_diaria():
    """
    Função específica para exportar a matriz diária com formatação específica
    """
    hoje = datetime.now().date()
    queryset = Contrato.objects.filter(data_inclusao__date=hoje)
    
    # Criar DataFrame
    df = pd.DataFrame.from_records(queryset.values())
    
    # Agrupar dados conforme necessário
    matriz = df.groupby(['corretor', 'status']).agg({
        'producao_bruta': 'sum',
        'producao_liquida': 'sum',
        'id': 'count'  # conta quantidade de contratos
    }).reset_index()
    
    # Formatar Excel
    writer = pd.ExcelWriter(f"matriz_diaria_{hoje.strftime('%Y%m%d')}.xlsx", engine='xlsxwriter')
    matriz.to_excel(writer, sheet_name='Matriz', index=False)
    
    # Adicionar formatação
    workbook = writer.book
    worksheet = writer.sheets['Matriz']
    
    # Adicionar formatos monetários, cores, etc.
    
    return writer 