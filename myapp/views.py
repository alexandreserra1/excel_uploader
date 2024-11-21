# myapp/views.py

from django.shortcuts import render, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Contrato
from .serializers import ContratoSerializer
from django.shortcuts import get_object_or_404
from .forms import UploadFileForm
from .utils import map_columns  # Importa a função de mapeamento
import pandas as pd
from django.utils import timezone
from decimal import Decimal
import datetime
from dateutil.parser import parse as parse_datetime  # Importação atualizada
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from django.db.models import Q
from django.db.models import Count, Sum
from rest_framework.decorators import api_view
from .dashboards.views import get_painel_recusas_data, get_painel_saldos_data
from .exports import export_to_excel, export_matriz_diaria

# View para upload da base completa
def upload_base_completa(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], atualizar=False)
            return redirect('contrato-list')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

# View para upload de atualização por ADE
def upload_atualizacao_ade(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'], atualizar=True)
            return redirect('contrato-list')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def handle_uploaded_file(f, atualizar=False):
    if f.name.endswith('.csv'):
        encodings_to_try = ['utf-8', 'latin1', 'cp1252']
        for encoding in encodings_to_try:
            try:
                f.seek(0)
                try:
                    df = pd.read_csv(f, encoding=encoding, on_bad_lines='skip', sep=';', quotechar='"')
                except:
                    f.seek(0)
                    df = pd.read_csv(f, encoding=encoding, on_bad_lines='skip', sep=',', quotechar='"')
                break  # Se conseguir ler, sai do loop
            except UnicodeDecodeError:
                continue
            except pd.errors.ParserError as e:
                print(f"Erro ao analisar o arquivo CSV: {e}")
                continue
        else:
            print("Não foi possível ler o arquivo CSV com as codificações testadas.")
            return
    elif f.name.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(f)
    else:
        print("Formato de arquivo não suportado.")
        return
    print(f"DataFrame lido com {df.shape[0]} linhas e {df.shape[1]} colunas.")
    print(df.head())

    # Aplica o mapeamento das colunas
    df = map_columns(df)
    
    
    # Verificar se 'ade' está presente no DataFrame após o mapeamento
    if atualizar and 'ade' not in df.columns:
        print("Erro: A coluna 'ade' não está presente no arquivo para atualização.")
        return
    

    # Normaliza o campo 'ade' para maiúsculas, se existir
    if 'ade' in df.columns:
        df['ade'] = df['ade'].astype(str).str.strip().str.upper()
        #remover linnhas onde 'ade' esta vazio ou nulo
        df = df[df['ade'].notnull() & (df['ade'].str.strip() != '')]
    elif atualizar:
        # Se estiver atualizando e 'ade' não está presente, não faz sentido continuar
        print("Erro: A coluna 'ade' é necessária para atualização e não foi encontrada.")
        return
        

    # Obtém os campos do modelo Contrato e seus tipos
    field_types = {field.name: field.get_internal_type() for field in Contrato._meta.get_fields()}
    model_fields = list(field_types.keys())

    # Filtra apenas as colunas que existem no modelo
    df = df[[col for col in df.columns if col in model_fields]]

    # Listas de campos por tipo
    date_fields = [name for name, field_type in field_types.items() if field_type == 'DateField']
    datetime_fields = [name for name, field_type in field_types.items() if field_type == 'DateTimeField']
    decimal_fields = [name for name, field_type in field_types.items() if field_type == 'FloatField']
    boolean_fields = [name for name, field_type in field_types.items() if field_type == 'BooleanField']
    integer_fields = [name for name, field_type in field_types.items() if field_type == 'IntegerField']

    # Adicione esta função dentro do handle_uploaded_file
    def clean_number(value):
        if pd.isnull(value) or str(value).strip() in ['', '-']:
            return None
        try:
            # Remove R$ e outros símbolos monetários
            value_str = str(value).replace('R$', '').replace('$', '')
            # Remove pontos de milhar e converte vírgula para ponto
            value_str = value_str.replace('.', '').replace(',', '.')
            # Remove espaços e outros caracteres
            value_str = value_str.strip()
            return float(value_str)
        except:
            return None

    # Limpar todos os campos numéricos antes de criar o contrato
    numeric_fields = ['salario', 'producao_bruta', 'producao_bruta_com_ajuste', 
                     'producao_liquida', 'producao_liquida_com_ajuste', 
                     'valor_base', 'valor_base_com_ajuste',
                     'valor_operacao_operacional', 'valor_cliente_operacional',
                     'valor_parcela_operacional', 'total_valor_parcelas',
                     'banco_origem_valor_parcela_1', 'banco_origem_valor_quitacao_1']

    # Limpar os campos numéricos no DataFrame
    for field in numeric_fields:
        if field in df.columns:
            df[field] = df[field].apply(clean_number)

    # Itera sobre as linhas do DataFrame com um contador de linha
    for line_number, (index, row) in enumerate(df.iterrows(), start=1):
        data = row.to_dict()
        # Tratar dados
        cleaned_data = {}
        for field in data:
            value = data[field]
            if pd.isnull(value):
                value = None
            else:
                if field in date_fields:
                    try:
                        if isinstance(value, (datetime.datetime, datetime.date)):
                            value = value.date()
                        elif value and str(value).strip() != '00/00/0000':  # Ignora datas inválidas
                            value = parse_datetime(str(value), dayfirst=True, fuzzy=True).date()
                        else:
                            value = None
                    except Exception as e:
                        print(f"Erro ao converter data no campo '{field}' na linha {line_number}: {e}")
                        value = None
                elif field in boolean_fields:
                    # Tratar campos booleanos
                    if str(value).strip().lower() in ['true', '1', 'sim', 'yes']:
                        value = True
                    elif str(value).strip().lower() in ['false', '0', 'nao', 'não', 'no']:
                        value = False
                    else:
                        value = False
                elif field in integer_fields:
                    # Tratar campos inteiros
                    try:
                        value = int(float(value))
                    except Exception as e:
                        print(f"Erro ao converter inteiro no campo '{field}' na linha {line_number}: {e}")
                        value = None
                else:
                    # Outros campos
                    value = str(value).strip()
            cleaned_data[field] = value

        # Definir 'data_inclusao' se não estiver presente
        cleaned_data.setdefault('data_inclusao', timezone.now())

        # Verifica se é para atualizar ou criar novo
        if atualizar:
            # Atualização por ADE
            ade_value = cleaned_data.get('ade')
            if ade_value and ade_value.strip():
                # Normalize 'ade_value' para maiúsculas
                ade_value = ade_value.upper().strip()
                contratos = Contrato.objects.filter(ade__iexact=ade_value)
                if contratos.exists():
                    # Atualizar o(s) contrato(s) existente(s)
                    for contrato in contratos:
                        # Atualizar campos do contrato com os dados do arquivo
                        for field, value in cleaned_data.items():
                            if value is not None:
                                setattr(contrato, field, value)
                        contrato.save()
                        print(f"Contrato com ADE '{ade_value}' atualizado na linha {line_number}.")
                else:
                    print(f"Nenhum contrato encontrado com ADE '{ade_value}' na linha {line_number}.")
            else:
                print(f"ADE não fornecido ou vazio na linha {line_number}.")
        else:
            # Criação de novos contratos
            try:
                Contrato.objects.create(**cleaned_data)
                print(f"Contrato criado na linha {line_number}.")
            except Exception as e:
                print(f"Erro ao criar o contrato na linha {line_number}: {e}")


# API Views
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100  # número de registros por página
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ContratoFilter(filters.FilterSet):
    cliente = filters.CharFilter(lookup_expr='icontains')
    ade = filters.CharFilter(lookup_expr='iexact')
    data_inclusao = filters.DateFromToRangeFilter()

    class Meta:
        model = Contrato
        fields = ['cliente', 'ade', 'data_inclusao']

class ContratoListCreateView(APIView):
    pagination_class = StandardResultsSetPagination
    filterset_class = ContratoFilter
    search_fields = ['cliente', 'cpf_do_cliente', 'ade', 'contrato']

    @method_decorator(cache_page(60 * 5))  # cache por 5 minutos
    def get(self, request):
        contratos = Contrato.objects.all().order_by('-data_inclusao')
        
        # Aplicar busca
        search = request.GET.get('search')
        if search:
            q_objects = Q()
            for field in self.search_fields:
                q_objects |= Q(**{f"{field}__icontains": search})
            contratos = contratos.filter(q_objects)

        # Aplicar filtros
        filterset = self.filterset_class(request.GET, queryset=contratos)
        if filterset.is_valid():
            contratos = filterset.qs

        # Paginação corrigida
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(contratos, request)
        serializer = ContratoSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)  # Método correto

    def post(self, request):
        serializer = ContratoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContratoDetailView(APIView):
    """
    API view para recuperar, atualizar e deletar um contrato.
    """

    def get_object(self, pk):
        return get_object_or_404(Contrato, pk=pk)

    def get(self, request, pk):
        contrato = self.get_object(pk)
        serializer = ContratoSerializer(contrato)
        return Response(serializer.data)

    def put(self, request, pk):
        contrato = self.get_object(pk)
        serializer = ContratoSerializer(contrato, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        contrato = self.get_object(pk)
        contrato.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ContratoAdeDetailView(APIView):
    """
    API view para recuperar e atualizar contrato por ADE.
    """

    def get(self, request, ade):
        ade = ade.strip().upper()
        contrato = Contrato.objects.filter(ade__iexact=ade).order_by('-data_inclusao').first()
        if contrato is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ContratoSerializer(contrato)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, ade):
        ade = ade.strip().upper()
        contratos = Contrato.objects.filter(ade__iexact=ade)
        if not contratos.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        for contrato in contratos:
            serializer = ContratoSerializer(contrato, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Contratos atualizados com sucesso."}, status=status.HTTP_200_OK)

@api_view(['GET'])
def export_contratos_excel(request):
    """
    Endpoint para exportar todos os contratos para Excel
    """
    queryset = Contrato.objects.all()
    return export_to_excel(queryset)

@api_view(['GET'])
def export_matriz_diaria(request):
    """
    Endpoint para exportar a matriz diária
    """
    return export_matriz_diaria()

def painel_recusas(request):
    """
    View para renderizar o painel de recusas
    """
    data = get_painel_recusas_data()
    return render(request, 'dashboards/recusas.html', data)

def painel_saldos(request):
    """
    View para renderizar o painel de saldos
    """
    data = get_painel_saldos_data()
    return render(request, 'dashboards/saldos.html', data)

