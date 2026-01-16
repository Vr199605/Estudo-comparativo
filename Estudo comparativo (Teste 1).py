import streamlit as st
import pandas as pd
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import numpy as np
import io
import re

# Configuração da página
st.set_page_config(
    page_title="Comparativo Avançado de Seguros",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado avançado
st.markdown("""
<style>
    /* Cores principais */
    :root {
        --primary: #667eea;
        --secondary: #764ba2;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #3b82f6;
        --dark: #1f2937;
        --light: #f9fafb;
    }
    
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    /* Cards modernos */
    .modern-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid #e5e7eb;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
    }
    
    .modern-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    }
    
    /* Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
        transition: all 0.3s;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #10b981, #34d399);
        color: white;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b, #fbbf24);
        color: white;
    }
    
    /* Progress bars */
    .progress-container {
        width: 100%;
        background-color: #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
        height: 10px;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 10px;
        transition: width 1s ease-in-out;
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    /* Indicadores visuais */
    .indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    /* Estilo para campos de entrada com formatação automática */
    .formatted-input {
        font-family: monospace;
        text-align: right;
    }
    
    .formatted-input::placeholder {
        color: #999;
    }
    
    /* Resumo financeiro */
    .resumo-card {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    /* Animações */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# Função para calcular idade
def calcular_idade(data_nascimento):
    hoje = date.today()
    idade = relativedelta(hoje, data_nascimento).years
    return idade

# Função para formatar número brasileiro
def formatar_numero_brasileiro(valor):
    if pd.isna(valor) or valor is None or valor == "":
        return ""
    
    try:
        # Remover qualquer formatação existente
        valor_limpo = str(valor).replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        
        # Converter para float
        valor_float = float(valor_limpo)
        
        # Formatar com separadores brasileiros
        if valor_float == 0:
            return ""
        elif valor_float.is_integer():
            valor_str = f"{int(valor_float):,}".replace(",", ".")
            return valor_str
        else:
            valor_str = f"{valor_float:,.2f}"
            partes = valor_str.split('.')
            parte_inteira = partes[0].replace(',', '.')
            parte_decimal = partes[1] if len(partes) > 1 else '00'
            return f"{parte_inteira},{parte_decimal}"
    except:
        return ""

# Função para converter string formatada para float
def converter_string_para_float(valor_str):
    if pd.isna(valor_str) or valor_str is None or valor_str == "":
        return 0.0
    
    try:
        # Remover R$, espaços
        valor_limpo = str(valor_str).replace('R$', '').replace(' ', '')
        
        # Se já estiver no formato brasileiro (1.000,00)
        if ',' in valor_limpo and '.' in valor_limpo:
            # Remover pontos de milhar e converter vírgula para ponto
            valor_limpo = valor_limpo.replace('.', '').replace(',', '.')
        # Se estiver no formato americano (1,000.00)
        elif ',' in valor_limpo and '.' not in valor_limpo:
            valor_limpo = valor_limpo.replace(',', '.')
        # Se tiver apenas vírgula decimal (1000,00)
        elif ',' in valor_limpo:
            valor_limpo = valor_limpo.replace(',', '.')
        
        return float(valor_limpo)
    except:
        return 0.0

# Função para formatar valor em moeda brasileira
def formatar_moeda(valor):
    if pd.isna(valor) or valor is None or valor == 0:
        return "R$ 0,00"
    
    try:
        valor_float = float(valor)
        
        if valor_float.is_integer():
            valor_str = f"{int(valor_float):,}".replace(",", ".")
            return f"R$ {valor_str},00"
        else:
            valor_str = f"{valor_float:,.2f}"
            partes = valor_str.split('.')
            parte_inteira = partes[0].replace(',', '.')
            parte_decimal = partes[1] if len(partes) > 1 else '00'
            return f"R$ {parte_inteira},{parte_decimal}"
    except:
        return "R$ 0,00"

# Função para criar input com formatação automática
def criar_input_formatado(label, key, placeholder="0,00"):
    input_valor = st.text_input(
        label,
        value="",
        key=key,
        placeholder=placeholder
    )
    
    return converter_string_para_float(input_valor)

# Função para extrair prazo da observação
def extrair_prazo_observacao(observacao):
    """Extrai o prazo da observação em meses"""
    if not observacao:
        return None
    
    obs_lower = observacao.lower()
    
    # Procurar por padrões de prazo
    padrao_anos = re.search(r'(\d+)\s*anos?', obs_lower)
    if padrao_anos:
        anos = int(padrao_anos.group(1))
        return anos * 12
    
    padrao_meses = re.search(r'(\d+)\s*meses?', obs_lower)
    if padrao_meses:
        return int(padrao_meses.group(1))
    
    # Verificar se é vitalício
    if 'vitalício' in obs_lower or 'vitalicia' in obs_lower or 'vitalicio' in obs_lower:
        return 'vitalicio'
    
    return None

# Inicializar dados das seguradoras
@st.cache_data
def inicializar_dados():
    produtos_comuns = [
        "Whole Life",
        "Morte com Reenquadramento Etário", 
        "Morte Temporária",
        "Morte Acidental",
        "DIT (Afastamento do Trabalho)",
        "DIH (Internação Hospitalar)",
        "Doenças Graves",
        "Invalidez Acidental",
        "Invalidez por Doença",
        "Cirurgia",
        "Quebra de Ossos",
        "SAF (Seguro Acidente Familiar)"
    ]
    
    seguradoras = {
        "Tokyo Marine": {
            "cor": "#1E3A8A",
            "icone": "🌊",
            "descricao": "Multinacional japonesa com forte presença no mercado",
            "mensalidade_base": 320.00,
            "prazo_pagamento": 240,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 320.00, "observacao": "Vitalício Global"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 50.00, "observacao": "Vitalício Plus"},
                "Morte Temporária": {"capital": "", "mensalidade": 25.00, "observacao": "20 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 30.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 15.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 10.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 45.00, "observacao": "30 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 35.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 25.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 20.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 12.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 30.00, "observacao": "Familiar"}
            },
            "beneficios_adicionais": ["Cobertura internacional", "Assistência 24h global", "Resgate flexível"],
            "pontos_fortes": ["Multinacional sólida", "Coberturas amplas", "Serviço premium"],
            "taxa_ipca_padrao": 5.0
        },
        "Metlife": {
            "cor": "#FF0000",
            "icone": "🔴",
            "descricao": "Líder global em seguros com forte atuação corporativa",
            "mensalidade_base": 360.00,
            "prazo_pagamento": 260,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 360.00, "observacao": "MetLife"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 68.00, "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": 36.00, "observacao": "20 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 46.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 18.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 11.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 55.00, "observacao": "35 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 42.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 33.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 24.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 14.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 35.00, "observacao": "Familiar"}
            },
            "beneficios_adicionais": ["Atuação corporativa", "Benefícios empresariais", "Rede global"],
            "pontos_fortes": ["Força corporativa", "Benefícios para empresas", "Presença global"],
            "taxa_ipca_padrao": 5.1
        },
        "Porto Seguro": {
            "cor": "#FF6B35",
            "icone": "⚓",
            "descricao": "Uma das maiores seguradoras do Brasil, conhecida por automóveis",
            "mensalidade_base": 310.00,
            "prazo_pagamento": 240,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 310.00, "observacao": "Porto Vida"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 55.00, "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": 28.00, "observacao": "15 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 35.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 14.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 9.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 42.00, "observacao": "28 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 32.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 25.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 20.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 11.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 28.00, "observacao": "Familiar"}
            },
            "beneficios_adicionais": ["Assistência residencial", "Desconto em outros seguros", "App completo"],
            "pontos_fortes": ["Marca reconhecida", "Ampla rede", "Multi-produtos"],
            "taxa_ipca_padrao": 5.2
        },
        "Mag Seguros": {
            "cor": "#CC0000",
            "icone": "🟥",
            "descricao": "Seguradora com foco em seguros pessoais e familiares",
            "mensalidade_base": 230.00,
            "prazo_pagamento": 220,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 230.00, "observacao": "Mag Seguros"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 44.00, "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": 23.00, "observacao": "15 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 30.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 12.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 8.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 38.00, "observacao": "27 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 29.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 21.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 17.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 11.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 22.00, "observacao": "Familiar"}
            },
            "beneficios_adicionais": ["Foco familiar", "Atendimento personalizado", "Produtos simples"],
            "pontos_fortes": ["Atendimento próximo", "Produtos familiares", "Preço acessível"],
            "taxa_ipca_padrao": 4.9
        },
        "Prudential": {
            "cor": "#003366",
            "icone": "🔵",
            "descricao": "Multinacional americana com tradição em seguros de vida",
            "mensalidade_base": 330.00,
            "prazo_pagamento": 250,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 330.00, "observacao": "Prudential Life"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 62.00, "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": 33.00, "observacao": "20 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 42.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 16.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 10.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 48.00, "observacao": "32 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 37.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 29.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 22.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 13.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 31.00, "observacao": "Familiar"}
            },
            "beneficios_adicionais": ["Tradição centenária", "Foco em previdência", "Investimentos sólidos"],
            "pontos_fortes": ["Solidez financeira", "Foco em longo prazo", "Portfólio completo"],
            "taxa_ipca_padrao": 5.0
        },
        "Omint": {
            "cor": "#008080",
            "icone": "🔶",
            "descricao": "Especializada em saúde premium e seguros de alta renda",
            "mensalidade_base": 450.00,
            "prazo_pagamento": 180,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 450.00, "observacao": "Omint Premium"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 95.00, "observacao": "Vitalício Premium"},
                "Morte Temporária": {"capital": "", "mensalidade": 55.00, "observacao": "15 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 70.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 28.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 18.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 85.00, "observacao": "45 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 65.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 55.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 35.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 20.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 55.00, "observacao": "Familiar Premium"}
            },
            "beneficios_adicionais": ["Rede saúde premium", "Atendimento exclusivo", "Serviços diferenciados"],
            "pontos_fortes": ["Saúde premium", "Atendimento exclusivo", "Coberturas amplas"],
            "taxa_ipca_padrao": 5.0
        },
        "Icatu": {
            "cor": "#FF6600",
            "icone": "🟧",
            "descricao": "Foco em previdência e seguros de vida com rentabilidade",
            "mensalidade_base": 300.00,
            "prazo_pagamento": 280,
            "produtos": {
                "Whole Life": {"capital": "", "mensalidade": 300.00, "observacao": "Icatu Vida"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": 55.00, "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": 30.00, "observacao": "18 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": 37.00, "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": 14.00, "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": 9.00, "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": 43.00, "observacao": "30 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": 34.00, "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": 26.00, "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": 20.00, "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": 12.00, "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": 29.00, "observacao": "Familiar"}
            },
            "beneficios_adicionais": ["Foco em previdência", "Rentabilidade atrativa", "Produtos diferenciados"],
            "pontos_fortes": ["Rentabilidade", "Foco em acumulação", "Produtos inovadores"],
            "taxa_ipca_padrao": 4.8
        }
    }
    
    return seguradoras, produtos_comuns

# Função para calcular resumo financeiro com base nas observações
def calcular_resumo_financeiro(seguradora, dados, periodo_meses, taxa_ipca, tem_assistencia_domiciliar=False, tem_seguro_viagem=False):
    """Calcula o resumo financeiro considerando os prazos das coberturas"""
    
    resultados = {
        "mensal_whole_life": dados.get("mensalidade_base", 0),
        "prazo_meses": periodo_meses,
        "prazo_anos": periodo_meses / 12,
        "coberturas": {},
        "total_mensalidade": 0,
        "total_capital": 0,
        "total_investimento_sem_ipca": 0,
        "total_investimento_com_ipca": 0
    }
    
    # Calcular Whole Life (sempre vitalício)
    total_investimento_sem_ipca_whole_life = resultados["mensal_whole_life"] * resultados["prazo_meses"]
    
    if taxa_ipca > 0:
        fator_correcao = (1 + taxa_ipca/100) ** resultados["prazo_anos"]
        total_investimento_com_ipca_whole_life = total_investimento_sem_ipca_whole_life * fator_correcao
    else:
        total_investimento_com_ipca_whole_life = total_investimento_sem_ipca_whole_life
    
    resultados["total_investimento_sem_ipca"] += total_investimento_sem_ipca_whole_life
    resultados["total_investimento_com_ipca"] += total_investimento_com_ipca_whole_life
    
    # Calcular outras coberturas
    for produto, valores in dados["produtos"].items():
        if produto == "Whole Life":
            continue
            
        capital = valores.get("capital", 0)
        mensalidade = valores.get("mensalidade", 0)
        observacao = valores.get("observacao", "")
        
        # Extrair prazo da observação
        prazo_cobertura = extrair_prazo_observacao(observacao)
        
        if prazo_cobertura == "vitalicio":
            prazo_meses_cobertura = resultados["prazo_meses"]
        elif prazo_cobertura:
            prazo_meses_cobertura = prazo_cobertura
        else:
            prazo_meses_cobertura = resultados["prazo_meses"]  # Default para vitalício
        
        # Calcular investimento para esta cobertura
        total_investimento_cobertura = mensalidade * prazo_meses_cobertura
        
        resultados["coberturas"][produto] = {
            "capital": capital,
            "mensalidade": mensalidade,
            "observacao": observacao,
            "prazo_meses": prazo_meses_cobertura,
            "total_investimento": total_investimento_cobertura
        }
        
        resultados["total_mensalidade"] += mensalidade
        resultados["total_capital"] += capital
        resultados["total_investimento_sem_ipca"] += total_investimento_cobertura
        resultados["total_investimento_com_ipca"] += total_investimento_cobertura
    
    # Adicionar assistência domiciliar se selecionada
    if tem_assistencia_domiciliar:
        resultados["total_mensalidade"] += 15.00  # Valor médio
        resultados["total_capital"] += 2000.00   # Capital médio
    
    # Adicionar seguro viagem se selecionado
    if tem_seguro_viagem:
        resultados["total_mensalidade"] += 25.00  # Valor médio
        resultados["total_capital"] += 5000.00   # Capital médio
    
    return resultados

# Função para gerar TXT
def gerar_txt(nome_cliente, idade, seguradoras_selecionadas, resultados, recomendacao, seguradoras, periodos_meses, taxa_ipca):
    texto = "=" * 60 + "\n"
    texto += "ANÁLISE COMPLETA DE SEGUROS\n"
    texto += "=" * 60 + "\n\n"
    
    texto += f"Data: {datetime.now().strftime('%d/%m/%Y')}\n"
    texto += f"Cliente: {nome_cliente}\n"
    texto += f"Idade: {idade} anos\n"
    texto += f"Taxa IPCA considerada: {taxa_ipca}% a.a.\n\n"
    
    texto += "💰 RESUMO FINANCEIRO POR SEGURADORA\n"
    texto += "-" * 40 + "\n"
    
    for seguradora in seguradoras_selecionadas:
        if seguradora in resultados:
            dados = resultados[seguradora]
            texto += f"\n{seguradora}:\n"
            texto += f"  Mensalidade Whole Life: {formatar_moeda(dados['mensal_whole_life'])}\n"
            texto += f"  Prazo: {dados['prazo_meses']} meses\n"
            texto += f"  Total Investido (sem IPCA): {formatar_moeda(dados['total_investimento_sem_ipca'])}\n"
            texto += f"  Total Investido (com IPCA): {formatar_moeda(dados['total_investimento_com_ipca'])}\n"
            texto += f"  Capital Segurado Total: {formatar_moeda(dados['total_capital'])}\n"
            texto += f"  Mensalidade Total Coberturas: {formatar_moeda(dados['total_mensalidade'])}\n"
    
    texto += "\n🛡️ COBERTURAS DETALHADAS\n"
    texto += "-" * 40 + "\n"
    
    if 'recomendacao' in locals() and recomendacao in resultados:
        texto += f"\nSeguro Recomendado: {recomendacao}\n\n"
        dados = resultados[recomendacao]
        for produto, cobertura in dados['coberturas'].items():
            texto += f"✓ {produto}:\n"
            texto += f"  Capital: {formatar_moeda(cobertura['capital'])}\n"
            texto += f"  Mensalidade: {formatar_moeda(cobertura['mensalidade'])}\n"
            texto += f"  Prazo: {cobertura['prazo_meses']} meses\n"
            texto += f"  Observação: {cobertura['observacao']}\n\n"
    
    return texto

# Interface principal
def main():
    # Carregar dados
    seguradoras, produtos_comuns = inicializar_dados()
    
    # Cabeçalho principal
    st.markdown("""
    <div class='main-header'>
        <h1 style='font-size: 3rem; margin-bottom: 1rem;'>🛡️ COMPARADOR AVANÇADO DE SEGUROS</h1>
        <h3 style='font-weight: 300; margin-bottom: 2rem;'>Análise completa para tomada de decisão estratégica</h3>
        <div style='display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;'>
            <span class='badge badge-success'>7 Seguradoras</span>
            <span class='badge badge-warning'>Análise Personalizada</span>
            <span class='badge badge-success'>Resumo Financeiro</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com configurações
    with st.sidebar:
        st.markdown("## ⚙️ **CONFIGURAÇÕES**")
        
        st.markdown("### 👤 **Dados do Cliente**")
        nome_cliente = st.text_input("Nome do Cliente", value="Cliente Exemplo")
        
        data_nascimento = st.date_input(
            "Data de Nascimento",
            value=date(1985, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        
        idade = calcular_idade(data_nascimento)
        st.markdown(f"**Idade calculada:** {idade} anos")
        
        st.markdown("### 🏢 **Seguradoras para Comparar**")
        
        todas_seguradoras = list(seguradoras.keys())
        selecionadas = st.multiselect(
            "Selecione as seguradoras",
            todas_seguradoras,
            default=["Tokyo Marine", "Porto Seguro", "Prudential", "Metlife"],
            max_selections=7
        )
        
        if len(selecionadas) < 2:
            st.warning("Selecione pelo menos 2 seguradoras para comparar")
            st.stop()
        
        st.markdown("### 📊 **Prazo para Whole Life (meses)**")
        periodos_meses = {}
        
        for seguradora in selecionadas:
            periodos_meses[seguradora] = st.number_input(
                f"Meses para {seguradora[:15]}...",
                min_value=1,
                max_value=600,
                value=seguradoras[seguradora]["prazo_pagamento"],
                key=f"periodo_meses_{seguradora}"
            )
        
        st.markdown("### 📈 **Parâmetros Financeiros**")
        taxa_ipca = st.number_input(
            "Taxa IPCA (% a.a.)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            format="%.1f"
        )
        
        if st.button("🔄 **ATUALIZAR ANÁLISE**", use_container_width=True):
            st.rerun()
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 VISÃO GERAL", 
        "🛡️ COBERTURAS", 
        "💰 FINANCEIRO", 
        "⭐ ANÁLISE",
        "📄 RELATÓRIO"
    ])
    
    # Tab 1: Visão Geral
    with tab1:
        st.markdown("<div class='animate-fade-in-up'>", unsafe_allow_html=True)
        st.markdown("## 📊 **VISÃO GERAL COMPARATIVA**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='resumo-card'>
                <h4>👤 Cliente</h4>
                <h2 style='color: #667eea;'>{nome_cliente.split()[0]}</h2>
                <p>{idade} anos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='resumo-card'>
                <h4>🏢 Seguradoras</h4>
                <h2 style='color: #764ba2;'>{len(selecionadas)}</h2>
                <p>comparadas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='resumo-card'>
                <h4>📈 IPCA</h4>
                <h2 style='color: #10b981;'>{taxa_ipca}%</h2>
                <p>ao ano</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 2: Coberturas
    with tab2:
        st.markdown("## 🛡️ **EDITAR CAPITAL SEGURADO**")
        st.markdown("**Digite os valores com ponto para milhares e vírgula para decimais:**")
        st.markdown("*Exemplo: 1.000.000,00 ou 1000,50*")
        
        # Criar tabs para cada seguradora
        seguradora_tabs = st.tabs([f"✏️ {s}" for s in selecionadas])
        
        # Dicionário para armazenar os checklists por seguradora
        checklist_seguro_viagem = {}
        checklist_assistencia_domiciliar = {}
        
        for idx, seguradora in enumerate(selecionadas):
            with seguradora_tabs[idx]:
                dados = seguradoras[seguradora]
                
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {dados["cor"]}20, {dados["cor"]}10); 
                            padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;'>
                    <h3 style='color: {dados["cor"]}; margin: 0 0 1rem 0;'>
                        {dados['icone']} Editando coberturas: {seguradora}
                    </h3>
                    <p style='margin: 0;'>{dados['descricao']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Checklist para Assistência Domiciliar
                st.markdown("### 🏠 **Assistência Domiciliar**")
                checklist_assistencia_domiciliar[seguradora] = st.checkbox(
                    "Incluir Assistência Domiciliar",
                    value=False,
                    key=f"assistencia_{seguradora}"
                )
                
                # Checklist para Seguro Viagem
                st.markdown("### ✈️ **Seguro Viagem**")
                checklist_seguro_viagem[seguradora] = st.checkbox(
                    "Incluir Seguro Viagem",
                    value=False,
                    key=f"viagem_{seguradora}"
                )
                
                st.markdown("---")
                st.markdown("### 📋 **Coberturas Principais**")
                
                # Criar formulário para cada produto
                for produto in produtos_comuns:
                    with st.expander(f"**{produto}**", expanded=False):
                        col1, col2, col3 = st.columns([2, 2, 4])
                        
                        with col1:
                            # Capital Segurado (em branco para digitar)
                            if produto in seguradoras[seguradora]["produtos"]:
                                capital_atual = seguradoras[seguradora]["produtos"][produto]["capital"]
                            else:
                                capital_atual = ""
                            
                            novo_capital = criar_input_formatado(
                                "Capital Segurado",
                                key=f"capital_{seguradora}_{produto}",
                                placeholder="Ex: 1.000.000,00"
                            )
                        
                        with col2:
                            # Observação (pré-preenchida)
                            if produto in seguradoras[seguradora]["produtos"]:
                                obs_atual = seguradoras[seguradora]["produtos"][produto]["observacao"]
                            else:
                                obs_atual = ""
                            
                            nova_obs = st.text_input(
                                "Observação",
                                value=obs_atual,
                                key=f"obs_{seguradora}_{produto}"
                            )
                        
                        with col3:
                            # Informações sobre prazo
                            if obs_atual:
                                prazo = extrair_prazo_observacao(obs_atual)
                                if prazo == "vitalicio":
                                    st.info("📅 **Vitalício** - Paga enquanto o seguro estiver ativo")
                                elif prazo:
                                    st.info(f"📅 **Prazo:** {prazo} meses ({prazo//12} anos)")
                                else:
                                    st.info("ℹ️ Prazo não especificado")
                        
                        # Atualizar dados
                        if produto not in seguradoras[seguradora]["produtos"]:
                            seguradoras[seguradora]["produtos"][produto] = {
                                "capital": "",
                                "mensalidade": 0,
                                "observacao": ""
                            }
                        
                        # Atualizar capital
                        seguradoras[seguradora]["produtos"][produto]["capital"] = novo_capital
                        
                        # Atualizar observação
                        seguradoras[seguradora]["produtos"][produto]["observacao"] = nova_obs
                
                # Calcular e mostrar resumo financeiro
                st.markdown("---")
                st.markdown("#### 📊 **RESUMO FINANCEIRO**")
                
                # Calcular resultados
                resultados_seguradora = calcular_resumo_financeiro(
                    seguradora,
                    dados,
                    periodos_meses[seguradora],
                    taxa_ipca,
                    checklist_assistencia_domiciliar.get(seguradora, False),
                    checklist_seguro_viagem.get(seguradora, False)
                )
                
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                
                with col_res1:
                    st.metric("Capital Total", formatar_moeda(resultados_seguradora["total_capital"]))
                
                with col_res2:
                    st.metric("Mensalidade Total", formatar_moeda(resultados_seguradora["total_mensalidade"]))
                
                with col_res3:
                    st.metric("Prazo Principal", f"{resultados_seguradora['prazo_meses']} meses")
                
                with col_res4:
                    st.metric("Total Investido", formatar_moeda(resultados_seguradora["total_investimento_sem_ipca"]))
    
    # Tab 3: Análise Financeira
    with tab3:
        st.markdown("## 💰 **ANÁLISE FINANCEIRA DETALHADA**")
        
        # Calcular resultados para todas as seguradoras
        resultados_completos = {}
        
        for seguradora in selecionadas:
            dados = seguradoras[seguradora]
            resultados_completos[seguradora] = calcular_resumo_financeiro(
                seguradora,
                dados,
                periodos_meses[seguradora],
                taxa_ipca,
                checklist_assistencia_domiciliar.get(seguradora, False),
                checklist_seguro_viagem.get(seguradora, False)
            )
        
        # Gráfico de comparação
        st.markdown("### 📈 **COMPARAÇÃO DE INVESTIMENTO TOTAL (COM IPCA)**")
        
        if resultados_completos:
            max_val = max([r["total_investimento_com_ipca"] for r in resultados_completos.values()])
            
            for seguradora, dados in resultados_completos.items():
                cor = seguradoras[seguradora]["cor"]
                porcentagem = (dados["total_investimento_com_ipca"] / max_val) * 100 if max_val > 0 else 0
                
                st.markdown(f"""
                <div style='margin: 1rem 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='width: 12px; height: 12px; background: {cor}; border-radius: 50%; margin-right: 0.5rem;'></div>
                            <span style='font-weight: 600;'>{seguradora}</span>
                        </div>
                        <span style='font-weight: bold; color: {cor};'>{formatar_moeda(dados['total_investimento_com_ipca'])}</span>
                    </div>
                    <div class='progress-container'>
                        <div class='progress-bar' style='width: {porcentagem}%; background: {cor};'></div>
                    </div>
                    <div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #666; margin-top: 0.25rem;'>
                        <span>{dados['prazo_meses']} meses</span>
                        <span>Mensal WL: {formatar_moeda(dados['mensal_whole_life'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Tabela comparativa detalhada
        st.markdown("---")
        st.markdown("### 📋 **TABELA COMPARATIVA DETALHADA**")
        
        if resultados_completos:
            dados_tabela = []
            for seguradora, dados in resultados_completos.items():
                dados_tabela.append({
                    "Seguradora": seguradora,
                    "Mensalidade WL (R$)": formatar_moeda(dados['mensal_whole_life']),
                    "Prazo (meses)": dados['prazo_meses'],
                    "Prazo (anos)": f"{dados['prazo_anos']:.1f}",
                    "Invest. sem IPCA (R$)": formatar_moeda(dados['total_investimento_sem_ipca']),
                    "Invest. com IPCA (R$)": formatar_moeda(dados['total_investimento_com_ipca']),
                    "Capital Total (R$)": formatar_moeda(dados['total_capital']),
                    "Mensalidade Total (R$)": formatar_moeda(dados['total_mensalidade'])
                })
            
            df_comparativo = pd.DataFrame(dados_tabela)
            st.dataframe(df_comparativo, use_container_width=True)
            
            # Encontrar melhor custo-benefício
            seguradora_melhor_custo = min(
                resultados_completos.items(), 
                key=lambda x: x[1]["total_investimento_com_ipca"] / (x[1]["total_capital"] + 1)
            )[0]
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #10b98120, #10b98110); 
                        border-radius: 15px; padding: 1.5rem; margin-top: 2rem;'>
                <h4 style='color: #10b981; margin: 0 0 0.5rem 0;'>🏆 Melhor Custo-Benefício</h4>
                <h3 style='color: #10b981; margin: 0;'>{seguradora_melhor_custo}</h3>
                <p style='margin: 0.5rem 0 0 0; color: #666;'>
                    Menor investimento por capital segurado
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Tab 4: Análise Detalhada
    with tab4:
        st.markdown("## ⭐ **ANÁLISE DETALHADA POR SEGURADORA**")
        
        # Calcular resultados se ainda não calculados
        if 'resultados_completos' not in locals():
            resultados_completos = {}
            for seguradora in selecionadas:
                dados = seguradoras[seguradora]
                resultados_completos[seguradora] = calcular_resumo_financeiro(
                    seguradora,
                    dados,
                    periodos_meses[seguradora],
                    taxa_ipca,
                    checklist_assistencia_domiciliar.get(seguradora, False),
                    checklist_seguro_viagem.get(seguradora, False)
                )
        
        for seguradora in selecionadas:
            dados = seguradoras[seguradora]
            resultado = resultados_completos[seguradora]
            
            st.markdown(f"""
            <div class='modern-card'>
                <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem;'>
                    <div style='display: flex; align-items: center;'>
                        <span style='font-size: 2rem; margin-right: 1rem;'>{dados['icone']}</span>
                        <div>
                            <h2 style='color: {dados["cor"]}; margin: 0;'>{seguradora}</h2>
                            <p style='color: #666; margin: 0;'>{dados['descricao']}</p>
                        </div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 1.5rem; font-weight: bold; color: {dados["cor"]};'>
                            {formatar_moeda(dados['mensalidade_base'])}
                        </div>
                        <div style='font-size: 0.9rem; color: #666;'>mensal Whole Life</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ✅ **Pontos Fortes**")
                if "pontos_fortes" in dados:
                    for ponto in dados["pontos_fortes"]:
                        st.markdown(f"""
                        <div style='display: flex; align-items: start; margin-bottom: 0.5rem;'>
                            <span style='color: #10b981; margin-right: 0.5rem;'>✓</span>
                            <span>{ponto}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("#### 🎁 **Benefícios**")
                if "beneficios_adicionais" in dados and dados["beneficios_adicionais"]:
                    for beneficio in dados["beneficios_adicionais"]:
                        st.markdown(f"""
                        <div style='display: inline-block; background: {dados["cor"]}20; color: {dados["cor"]}; 
                                    padding: 0.25rem 0.75rem; border-radius: 50px; margin: 0.25rem; 
                                    font-size: 0.85rem;'>
                            {beneficio}
                        </div>
                        """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📊 **Resumo Financeiro**")
                
                st.markdown(f"""
                <div style='background: {dados["cor"]}10; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span>Capital Total:</span>
                        <span style='font-weight: bold;'>{formatar_moeda(resultado['total_capital'])}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span>Mensalidade Total:</span>
                        <span style='font-weight: bold;'>{formatar_moeda(resultado['total_mensalidade'])}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span>Investimento Total:</span>
                        <span style='font-weight: bold;'>{formatar_moeda(resultado['total_investimento_com_ipca'])}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between;'>
                        <span>Prazo:</span>
                        <span style='font-weight: bold;'>{resultado['prazo_meses']} meses</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Checklist status
                st.markdown("#### 📋 **Coberturas Adicionais**")
                if checklist_assistencia_domiciliar.get(seguradora, False):
                    st.markdown("✓ **Assistência Domiciliar incluída**")
                if checklist_seguro_viagem.get(seguradora, False):
                    st.markdown("✓ **Seguro Viagem incluído**")
            
            st.markdown("</div>")
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Tab 5: Relatório
    with tab5:
        st.markdown("## 📄 **RELATÓRIO COMPLETO**")
        
        # Calcular recomendação baseada no menor custo por capital segurado
        if 'resultados_completos' in locals() and resultados_completos:
            melhor_ratio = float('inf')
            recomendacao = ""
            
            for seguradora, dados in resultados_completos.items():
                if dados['total_capital'] > 0:
                    ratio = dados['total_investimento_com_ipca'] / dados['total_capital']
                    if ratio < melhor_ratio:
                        melhor_ratio = ratio
                        recomendacao = seguradora
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 **Visualizar Relatório**")
            
            if st.button("👁️ **GERAR RELATÓRIO**", use_container_width=True):
                if 'resultados_completos' in locals() and resultados_completos:
                    texto_relatorio = gerar_txt(
                        nome_cliente, 
                        idade, 
                        selecionadas, 
                        resultados_completos, 
                        recomendacao if 'recomendacao' in locals() else "", 
                        seguradoras, 
                        periodos_meses, 
                        taxa_ipca
                    )
                    
                    st.markdown("### 📋 **RELATÓRIO COMPLETO**")
                    st.text_area("Conteúdo do Relatório", texto_relatorio, height=400)
                else:
                    st.warning("Execute primeiro a análise nas abas anteriores")
        
        with col2:
            st.markdown("### 📥 **Exportar Relatório**")
            
            if st.button("💾 **BAIXAR RELATÓRIO TXT**", use_container_width=True):
                if 'resultados_completos' in locals() and resultados_completos:
                    texto_relatorio = gerar_txt(
                        nome_cliente, 
                        idade, 
                        selecionadas, 
                        resultados_completos, 
                        recomendacao if 'recomendacao' in locals() else "", 
                        seguradoras, 
                        periodos_meses, 
                        taxa_ipca
                    )
                    
                    st.download_button(
                        label="⬇️ CLIQUE PARA BAIXAR",
                        data=texto_relatorio,
                        file_name=f"Relatorio_Seguros_{nome_cliente.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                else:
                    st.warning("Execute primeiro a análise nas abas anteriores")

if __name__ == "__main__":
    main()


