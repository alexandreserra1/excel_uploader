# myapp/utils.py

import pandas as pd
import unicodedata
from datetime import datetime
from .models import Contrato

def normalize_column_name(name):
    """
    Função para normalizar os nomes das colunas:
    - Remove espaços extras.
    - Converte para minúsculas.
    - Remove acentos e caracteres especiais.
    """
    name = ' '.join(name.strip().split()).lower()
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return name

def process_file(file, update_mode=False):
    """
    Processa o arquivo enviado (CSV ou Excel)
    update_mode: Se True, atualiza registros existentes. Se False, cria novos registros
    """
    # Determinar extensão do arquivo
    file_name = file.name.lower()
    
    try:
        # Ler arquivo baseado na extensão
        if file_name.endswith('.csv'):
            df = pd.read_csv(file, sep=';', encoding='latin1')
        elif file_name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            raise ValueError("Formato de arquivo não suportado. Use CSV ou XLSX.")

        # Normalizar nomes das colunas
        df.columns = [normalize_column_name(col) for col in df.columns]
        
        # Aplicar mapeamento de colunas
        df = map_columns(df)
        
        # Converter datas
        date_columns = ['data_nascimento', 'data_da_formalizacao', 'previsao_chegada_saldo']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Processar registros
        registros_processados = 0
        
        for _, row in df.iterrows():
            dados = {col: row[col] for col in df.columns if col in COLUMN_MAPPING.values()}
            
            if update_mode:
                # Modo atualização - procura pelo ADE
                if 'ade' in dados:
                    contrato = Contrato.objects.filter(ade=dados['ade']).first()
                    if contrato:
                        for key, value in dados.items():
                            setattr(contrato, key, value)
                        contrato.save()
                        registros_processados += 1
            else:
                # Modo criação - novo registro
                Contrato.objects.create(**dados)
                registros_processados += 1

        return {
            'success': True,
            'message': f'{registros_processados} registros processados com sucesso',
            'registros_processados': registros_processados
        }

    except Exception as e:
        return {
            'success': False,
            'message': f'Erro ao processar arquivo: {str(e)}',
            'registros_processados': 0
        }

# Dicionário de mapeamento das colunas do arquivo para os campos do modelo
COLUMN_MAPPING = {
    'corretor': 'corretor',
    'digitador': 'digitador',
    'codigo loja': 'codigo_loja',
    'sala': 'sala',
    'contrato': 'contrato',
    'cliente': 'cliente',
    'cpf do cliente': 'cpf_do_cliente',
    'rg do cliente': 'rg_do_cliente',
    'nome da mae': 'nome_da_mae',
    'data nascimento': 'data_nascimento',
    'cep': 'cep',
    'cidade': 'cidade',
    'uf': 'uf',
    'matricula': 'matricula',
    'especie do beneficio': 'especie_do_beneficio',
    'uf do beneficio': 'uf_do_beneficio',
    'salario': 'salario',
    'telefone residencial': 'telefone_residencial',
    'telefone comercial': 'telefone_comercial',
    'telefone celular': 'telefone_celular',
    'recebe beneficio cartao': 'recebe_beneficio_cartao',
    'contrato portado': 'contrato_portado',
    'ade': 'ade',
    'tipo pagamento': 'tipo_pagamento',
    'banco': 'banco',
    'agencia': 'agencia',
    'dv agencia': 'dv_agencia',
    'conta': 'conta',
    'dv conta': 'dv_conta',
    'tipo de conta': 'tipo_de_conta',
    'banco emprestimo': 'banco_emprestimo',
    'orgao': 'orgao',
    'operacao': 'operacao',
    'status do contrato': 'status_do_contrato',
    'formalizacao digital': 'formalizacao_digital',
    'pendente de formalizacao': 'pendente_de_formalizacao',
    'link formalizacao': 'link_formalizacao',
    'data da digitacao do contrato no banco': 'data_digitacao_banco',
    'data da digitacao do contrato no sistema': 'data_digitacao_sistema',
    'data de pagamento': 'data_pagamento',
    'data pagamento do saldo': 'data_pagamento_saldo',
    'data de despacho do beneficio': 'data_despacho_beneficio',
    'tabela': 'tabela',
    'prazo': 'prazo',
    'producao bruta': 'producao_bruta',
    'producao bruta com ajuste': 'producao_bruta_com_ajuste',
    'producao liquida': 'producao_liquida',
    'producao liquida com ajuste': 'producao_liquida_com_ajuste',
    'cliente novo': 'cliente_novo',
    'total valor parcelas': 'total_valor_parcelas',
    'clonado': 'clonado',
    'valor operacao operacional': 'valor_operacao_operacional',
    'valor cliente operacional': 'valor_cliente_operacional',
    'valor parcela operacional': 'valor_parcela_operacional',
    'origem': 'origem',
    'valor base': 'valor_base',
    'valor base com ajuste': 'valor_base_com_ajuste',
    'banco origem nome 1': 'banco_origem_nome_1',
    'banco origem prazo 1': 'banco_origem_prazo_1',
    'banco origem parcelas pagas 1': 'banco_origem_parcelas_pagas_1',
    'banco origem valor parcela 1': 'banco_origem_valor_parcela_1',
    'banco origem valor quitacao 1': 'banco_origem_valor_quitacao_1',
    'campo extra': 'campo_extra',
    'observacao': 'observacao',
    'observação': 'observacao',
    'caixa do contrato': 'caixa_do_contrato',
    'sexo': 'sexo',
    'data da formalizacao': 'data_da_formalizacao',
    'previsao chegada saldo': 'previsao_chegada_saldo',
    'tipo chave pix': 'tipo_chave_pix',
    'chave pix': 'chave_pix',
    'status de acordo com padrao status contrato': 'status_de_acordo_com_padrao_status_contrato',
    'data do status': 'data_do_status',
    # Tratamento para colunas com caracteres invisíveis
    '\u200e ': 'coluna_invisivel_1',
    '\u200e .1': 'coluna_invisivel_2',
    # Adicione outros mapeamentos conforme necessário
}

def map_columns(df):
    """
    Função para aplicar o mapeamento das colunas no DataFrame.
    """
    # Normalizar os nomes das colunas
    df.columns = [normalize_column_name(col) for col in df.columns]
    # Aplicar o mapeamento
    df.rename(columns=COLUMN_MAPPING, inplace=True)
    # Imprimir colunas após o mapeamento
    print(f"Colunas após o mapeamento: {df.columns.tolist()}")
    # Identificar colunas não mapeadas
    unmapped_columns = set(df.columns) - set(COLUMN_MAPPING.values())
    # Remover colunas não mapeadas
    df.drop(columns=unmapped_columns, inplace=True)
    if unmapped_columns:
        print(f"Atenção: As seguintes colunas não foram mapeadas e serão ignoradas: {unmapped_columns}")
    return df
