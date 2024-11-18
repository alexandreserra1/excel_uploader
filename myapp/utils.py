# myapp/utils.py

import unicodedata

def normalize_column_name(name):
    """
    Função para normalizar os nomes das colunas:
    - Remove espaços extras.
    - Converte para minúsculas.
    - Remove acentos e caracteres especiais.
    """
    # Remove espaços extras e converte para minúsculas
    name = ' '.join(name.strip().split()).lower()
    # Remove acentos e caracteres especiais
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    return name

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
    'ade vinculada': 'ade_vinculada',
    'tipo pagamento': 'tipo_pagamento',
    'banco': 'banco',
    'agencia': 'agencia',
    'dv agencia': 'dv_agencia',
    'no conta': 'numero_conta',
    'nº conta': 'numero_conta',  # Mapeamento adicional para 'Nº Conta'
    'dv conta': 'dv_conta',
    'tipo de conta': 'tipo_de_conta',
    'banco emprestimo': 'banco_emprestimo',
    'orgao (convenio)': 'orgao_convenio',
    'operacao': 'operacao',
    'status do contrato': 'status_do_contrato',
    'formalizacao digital': 'formalizacao_digital',
    'formalização digital': 'formalizacao_digital',  # Com acento
    'pendente de formalizacao': 'pendente_de_formalizacao',
    'pendente de formalização': 'pendente_de_formalizacao',  # Com acento
    'link formalizacao': 'link_formalizacao',
    'data da digitacao do contrato no banco': 'data_da_digitacao_do_contrato_no_banco',
    'data da digitacao do contrato no sistema': 'data_da_digitacao_do_contrato_no_sistema',
    'data de pagamento': 'data_de_pagamento',
    'data pagamento do saldo': 'data_pagamento_do_saldo',
    'data de despacho do beneficio (ddb)': 'data_de_despacho_do_beneficio',
    'tabela': 'tabela',
    'prazo': 'prazo',
    'producao bruta': 'producao_bruta',
    'producao bruta com ajuste de %': 'producao_bruta_com_ajuste',
    'producao liquida': 'producao_liquida',
    'producao liquida com ajuste de %': 'producao_liquida_com_ajuste',
    'cliente novo': 'cliente_novo',
    'total valor parcelas': 'total_valor_parcelas',
    'clonado': 'clonado',
    'valor operacao operacional': 'valor_operacao_operacional',
    'valor cliente operacional': 'valor_cliente_operacional',
    'valor parcela operacional': 'valor_parcela_operacional',
    'origem': 'origem',
    'valor base': 'valor_base',
    'valor base com ajuste de %': 'valor_base_com_ajuste',
    'banco origem nome 1': 'banco_origem_nome_1',
    'banco origem prazo 1': 'banco_origem_prazo_1',
    'banco origem parcelas pagas 1': 'banco_origem_parcelas_pagas_1',
    'banco origem valor parcela 1': 'banco_origem_valor_parcela_1',
    'banco origem valor quitacao 1': 'banco_origem_valor_quitacao_1',
    'banco origem valor quitação 1': 'banco_origem_valor_quitacao_1',  # Com acento
    'campo extra': 'campo_extra',
    'observacao': 'observacao',
    'observação': 'observacao',  # Com acento
    'caixa do contrato': 'caixa_do_contrato',
    'sexo': 'sexo',
    'data da formalizacao': 'data_da_formalizacao',
    'data da formalização': 'data_da_formalizacao',  # Com acento
    'previsao chegada saldo': 'previsao_chegada_saldo',
    'previsão chegada saldo': 'previsao_chegada_saldo',  # Com acento
    'tipo chave pix': 'tipo_chave_pix',
    'chave pix': 'chave_pix',
    'status de acordo com padrao status contrato': 'status_de_acordo_com_padrao_status_contrato',
    'status de acordo com padrão status contrato': 'status_de_acordo_com_padrao_status_contrato',  # Com acento
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
