# myapp/admin.py

from django.contrib import admin
from .models import Contrato

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'contrato', 'status', 'data_inclusao')
    search_fields = ('cliente', 'cpf_do_cliente', 'contrato')
