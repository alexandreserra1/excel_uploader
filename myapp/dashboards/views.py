from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from ..models import Contrato

def get_painel_recusas_data():
    """
    Calcula estatísticas de recusas baseado nos dados do banco
    """
    hoje = datetime.now().date()
    ultimos_30_dias = hoje - timedelta(days=30)
    
    # Filtra contratos recusados
    recusados = Contrato.objects.filter(status='Recusado')
    
    # Calcula estatísticas
    dados = {
        'total_recusas': recusados.count(),
        'recusas_hoje': recusados.filter(data_inclusao__date=hoje).count(),
        
        # Agrupamento por status do contrato
        'recusas_por_status': list(recusados.values('status_do_contrato')
            .annotate(total=Count('id'))
            .order_by('-total')),
            
        # Agrupamento por corretor
        'recusas_por_corretor': list(recusados.values('corretor')
            .annotate(total=Count('id'))
            .order_by('-total')),
            
        # Gráfico dos últimos 30 dias
        'grafico_recusas': list(recusados
            .filter(data_inclusao__date__gte=ultimos_30_dias)
            .values('data_inclusao__date')
            .annotate(total=Count('id'))
            .order_by('data_inclusao__date'))
    }
    
    return dados

def get_painel_saldos_data():
    """
    Calcula estatísticas de saldos baseado nos dados do banco
    """
    hoje = datetime.now().date()
    ultimos_30_dias = hoje - timedelta(days=30)
    
    # Filtra contratos com saldo
    com_saldo = Contrato.objects.filter(valor_saldo__gt=0)
    
    # Calcula estatísticas
    dados = {
        'total_saldos': {
            'total': com_saldo.aggregate(total=Sum('valor_saldo'))['total'] or 0,
            'quantidade': com_saldo.count()
        },
        
        # Agrupamento por status
        'saldos_por_status': list(com_saldo.values('status')
            .annotate(
                total=Sum('valor_saldo'),
                quantidade=Count('id')
            ).order_by('-total')),
            
        # Agrupamento por corretor
        'saldos_por_corretor': list(com_saldo.values('corretor')
            .annotate(
                total=Sum('valor_saldo'),
                quantidade=Count('id')
            ).order_by('-total')),
            
        # Gráfico dos últimos 30 dias
        'grafico_saldos': list(com_saldo
            .filter(data_inclusao__date__gte=ultimos_30_dias)
            .values('data_inclusao__date')
            .annotate(total=Sum('valor_saldo'))
            .order_by('data_inclusao__date'))
    }
    
    return dados
