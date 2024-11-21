from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from ..models import Contrato

def get_painel_recusas_data():
    """
    Retorna dados para o painel de recusas
    """
    hoje = datetime.now().date()
    ultimos_30_dias = hoje - timedelta(days=30)

    return {
        'total_recusas': Contrato.objects.filter(status='Recusado').count(),
        'recusas_hoje': Contrato.objects.filter(
            status='Recusado',
            data_inclusao__date=hoje
        ).count(),
        'recusas_por_status': Contrato.objects.filter(
            status='Recusado'
        ).values('status_do_contrato').annotate(
            total=Count('id')
        ).order_by('-total'),
        'recusas_por_corretor': Contrato.objects.filter(
            status='Recusado'
        ).values('corretor').annotate(
            total=Count('id')
        ).order_by('-total'),
        'grafico_recusas': Contrato.objects.filter(
            status='Recusado',
            data_inclusao__date__gte=ultimos_30_dias
        ).values('data_inclusao__date').annotate(
            total=Count('id')
        ).order_by('data_inclusao__date')
    }

def get_painel_saldos_data():
    """
    Retorna dados para o painel de saldos
    """
    hoje = datetime.now().date()
    ultimos_30_dias = hoje - timedelta(days=30)

    return {
        'total_saldos': Contrato.objects.filter(
            valor_saldo__gt=0
        ).aggregate(
            total=Sum('valor_saldo'),
            quantidade=Count('id')
        ),
        'saldos_por_status': Contrato.objects.filter(
            valor_saldo__gt=0
        ).values('status').annotate(
            total=Sum('valor_saldo'),
            quantidade=Count('id')
        ).order_by('-total'),
        'saldos_por_corretor': Contrato.objects.filter(
            valor_saldo__gt=0
        ).values('corretor').annotate(
            total=Sum('valor_saldo'),
            quantidade=Count('id')
        ).order_by('-total'),
        'grafico_saldos': Contrato.objects.filter(
            valor_saldo__gt=0,
            data_inclusao__date__gte=ultimos_30_dias
        ).values('data_inclusao__date').annotate(
            total=Sum('valor_saldo')
        ).order_by('data_inclusao__date')
    }
