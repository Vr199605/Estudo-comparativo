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
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        animation: float 20s linear infinite;
        opacity: 0.3;
    }
    
    @keyframes float {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(-50px, -50px) rotate(360deg); }
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
    
    .badge-danger {
        background: linear-gradient(135deg, #ef4444, #f87171);
        color: white;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #3b82f6, #60a5fa);
        color: white;
    }
    
    /* Métricas */
    .metric-container {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 1px solid #e2e8f0;
        transition: all 0.3s;
    }
    
    .metric-container:hover {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
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
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
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
    
    /* Seção de apresentação */
    .presentation-section {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem 0;
        border: 2px solid #bae6fd;
    }
    
    /* Indicadores visuais */
    .indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        .modern-card {
            padding: 1.5rem;
        }
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
</style>
""", unsafe_allow_html=True)

# Função para calcular idade
def calcular_idade(data_nascimento):
    hoje = date.today()
    idade = relativedelta(hoje, data_nascimento).years
    return idade

# Função para formatar número brasileiro
def formatar_numero_brasileiro(valor):
    if pd.isna(valor) or valor is None or valor == "" or valor == 0:
        return ""
    
    try:
        # Se for string, limpar
        if isinstance(valor, str):
            valor = valor.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
        
        # Converter para float
        valor_float = float(valor)
        
        if valor_float == 0:
            return ""
        
        # Formatar com separadores brasileiros
        if valor_float.is_integer():
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
        # Converter para float se necessário
        if isinstance(valor, str):
            valor_float = converter_string_para_float(valor)
        else:
            valor_float = float(valor)
        
        if valor_float == 0:
            return "R$ 0,00"
        
        # Formatar como moeda brasileira
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
def criar_input_formatado(label, valor, key, placeholder="0,00"):
    # Converter valor para formato brasileiro
    valor_formatado = formatar_numero_brasileiro(valor) if valor not in [None, "", 0] else ""
    
    # Criar input com formatação
    input_valor = st.text_input(
        label,
        value=valor_formatado,
        key=key,
        placeholder=placeholder
    )
    
    # Retornar o valor convertido para float
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
    if 'vitalício' in obs_lower or 'vitalicia' in obs_lower or 'vitalicio' in obs_lower or 'global' in obs_lower:
        return 'vitalicio'
    
    # Verificar se é mensal
    if 'mensal' in obs_lower:
        return 1  # Mensal
    
    # Verificar se é diária
    if 'diária' in obs_lower or 'diario' in obs_lower or 'diaria' in obs_lower:
        return 1  # Considerar como 1 mês para cálculo
    
    # Verificar se é por evento/ocorrência
    if 'evento' in obs_lower or 'ocorrência' in obs_lower or 'ocorrencia' in obs_lower:
        return None  # Não tem prazo fixo
    
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "Vitalício Global"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício Plus"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "20 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "30 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar"}
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "MetLife"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "20 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "35 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar"}
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "Porto Vida"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "15 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "28 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar"}
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "Mag Seguros"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "15 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "27 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar"}
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "Prudential Life"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "20 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "32 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar"}
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "Omint Premium"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício Premium"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "15 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "45 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar Premium"}
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
                "Whole Life": {"capital": "", "mensalidade": "", "observacao": "Icatu Vida"},
                "Morte com Reenquadramento Etário": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Morte Temporária": {"capital": "", "mensalidade": "", "observacao": "18 anos"},
                "Morte Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "DIT (Afastamento do Trabalho)": {"capital": "", "mensalidade": "", "observacao": "Mensal"},
                "DIH (Internação Hospitalar)": {"capital": "", "mensalidade": "", "observacao": "Diária"},
                "Doenças Graves": {"capital": "", "mensalidade": "", "observacao": "30 doenças"},
                "Invalidez Acidental": {"capital": "", "mensalidade": "", "observacao": "Vitalício"},
                "Invalidez por Doença": {"capital": "", "mensalidade": "", "observacao": "Temporária"},
                "Cirurgia": {"capital": "", "mensalidade": "", "observacao": "Por evento"},
                "Quebra de Ossos": {"capital": "", "mensalidade": "", "observacao": "Por ocorrência"},
                "SAF (Seguro Acidente Familiar)": {"capital": "", "mensalidade": "", "observacao": "Familiar"}
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
    
    # Obter mensalidade do Whole Life
    mensal_whole_life = 0
    if "Whole Life" in dados["produtos"]:
        mensal_whole_life = dados["produtos"]["Whole Life"].get("mensalidade", 0)
        if isinstance(mensal_whole_life, str):
            mensal_whole_life = converter_string_para_float(mensal_whole_life)
    
    resultados = {
        "mensal_whole_life": mensal_whole_life,
        "prazo_meses": periodo_meses,
        "prazo_anos": periodo_meses / 12,
        "coberturas": {},
        "total_mensalidade": 0,
        "total_capital": 0,
        "total_investimento_sem_ipca": 0,
        "total_investimento_com_ipca": 0
    }
    
    # Calcular Whole Life (sempre vitalício)
    if mensal_whole_life > 0:
        total_investimento_sem_ipca_whole_life = mensal_whole_life * resultados["prazo_meses"]
        
        if taxa_ipca > 0:
            fator_correcao = (1 + taxa_ipca/100) ** resultados["prazo_anos"]
            total_investimento_com_ipca_whole_life = total_investimento_sem_ipca_whole_life * fator_correcao
        else:
            total_investimento_com_ipca_whole_life = total_investimento_sem_ipca_whole_life
        
        resultados["total_investimento_sem_ipca"] += total_investimento_sem_ipca_whole_life
        resultados["total_investimento_com_ipca"] += total_investimento_com_ipca_whole_life
        
        # Adicionar capital do Whole Life se existir
        if "Whole Life" in dados["produtos"]:
            capital_whole_life = dados["produtos"]["Whole Life"].get("capital", 0)
            if isinstance(capital_whole_life, str):
                capital_whole_life = converter_string_para_float(capital_whole_life)
            resultados["total_capital"] += capital_whole_life
            resultados["total_mensalidade"] += mensal_whole_life
    
    # Calcular outras coberturas
    for produto, valores in dados["produtos"].items():
        if produto == "Whole Life":
            continue
            
        capital = valores.get("capital", 0)
        mensalidade = valores.get("mensalidade", 0)
        observacao = valores.get("observacao", "")
        
        # Converter strings para float se necessário
        if isinstance(capital, str):
            capital = converter_string_para_float(capital)
        if isinstance(mensalidade, str):
            mensalidade = converter_string_para_float(mensalidade)
        
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

# Função para criar tabela de cenários
def criar_tabela_cenarios(seguradoras_dict, seguradoras_selecionadas, produtos_comuns):
    """Cria tabela editável para cenários personalizados"""
    
    dados_cenarios = []
    
    for produto in produtos_comuns:
        linha = {"Produto": produto}
        for seguradora in seguradoras_selecionadas:
            if produto in seguradoras_dict[seguradora]["produtos"]:
                capital = seguradoras_dict[seguradora]["produtos"][produto]["capital"]
                linha[seguradora] = float(capital) if isinstance(capital, (int, float)) else 0.0
            else:
                linha[seguradora] = 0.0
        dados_cenarios.append(linha)
    
    return pd.DataFrame(dados_cenarios)

# Função para gerar TXT
def gerar_txt(nome_cliente, idade, seguradoras_selecionadas, resultados, recomendacao, seguradoras, periodos_meses, taxa_ipca):
    """Gera relatório em formato TXT"""
    
    texto = "=" * 60 + "\n"
    texto += "ANÁLISE COMPLETA DE SEGUROS\n"
    texto += "=" * 60 + "\n\n"
    
    texto += f"Data: {datetime.now().strftime('%d/%m/%Y')}\n"
    texto += f"Cliente: {nome_cliente}\n"
    texto += f"Idade: {idade} anos\n"
    texto += f"Taxa IPCA considerada: {taxa_ipca}% a.a.\n\n"
    
    texto += "🎯 ANÁLISE ESTRATÉGICA DE PROTEÇÃO\n"
    texto += "-" * 40 + "\n"
    texto += "Esta análise foi desenvolvida para fornecer uma visão completa e comparativa das melhores opções de seguros disponíveis no mercado.\n\n"
    
    texto += "📊 METODOLOGIA DA ANÁLISE\n"
    texto += "-" * 40 + "\n"
    texto += "• Comparação de múltiplas seguradoras líderes\n"
    texto += "• Análise de diversas coberturas\n"
    texto += "• Critérios: custo-benefício, coberturas, prazo\n"
    texto += "• Sistema de pontuação multicritério\n"
    texto += "• Cálculos com projeção de inflação\n\n"
    
    texto += "🏢 SEGURADORAS ANALISADAS\n"
    texto += "-" * 40 + "\n"
    for seguradora in seguradoras_selecionadas:
        texto += f"• {seguradora}: {seguradoras[seguradora]['descricao']}\n"
    texto += "\n"
    
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
    
    if 'recomendacao' in locals() and recomendacao:
        texto += "\n🏆 RECOMENDAÇÃO FINAL\n"
        texto += "-" * 40 + "\n"
        texto += f"SEGURADORA RECOMENDADA: {recomendacao}\n\n"
        texto += f"Descrição: {seguradoras[recomendacao]['descricao']}\n\n"
        
        texto += "📈 PONTOS FORTES:\n"
        for ponto in seguradoras[recomendacao]['pontos_fortes']:
            texto += f"• {ponto}\n"
        
        texto += "\n🎁 BENEFÍCIOS INCLUÍDOS:\n"
        for beneficio in seguradoras[recomendacao]['beneficios_adicionais']:
            texto += f"✓ {beneficio}\n"
        
        texto += f"\n💵 Mensalidade Whole Life: {formatar_moeda(resultados[recomendacao]['mensal_whole_life'])}\n"
        texto += f"📅 Prazo: {periodos_meses.get(recomendacao, seguradoras[recomendacao]['prazo_pagamento'])} meses\n"
        
        if recomendacao in resultados:
            texto += f"🛡️ Capital Segurado Total: {formatar_moeda(resultados[recomendacao]['total_capital'])}\n"
    
    texto += "\n🎯 CONSIDERAÇÕES FINAIS\n"
    texto += "-" * 40 + "\n"
    texto += "Esta análise foi realizada com rigor técnico para garantir a melhor proteção disponível.\n"
    texto += "Recomendamos agendar uma conversa para discutir os detalhes da contratação.\n\n"
    
    texto += "=" * 60 + "\n"
    texto += "Relatório gerado automaticamente pelo Sistema de Análise de Seguros\n"
    texto += "Dados válidos para a data de emissão\n"
    texto += "=" * 60 + "\n"
    
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
            <span class='badge badge-info'>12 Coberturas</span>
            <span class='badge badge-warning'>Análise Personalizada</span>
            <span class='badge badge-danger'>Resumo Financeiro</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar com configurações
    with st.sidebar:
        st.markdown("## ⚙️ **CONFIGURAÇÕES**")
        
        # Nome do cliente
        st.markdown("### 👤 **Dados do Cliente**")
        nome_cliente = st.text_input("Nome do Cliente", value="Cliente Exemplo")
        
        # Data de nascimento
        data_nascimento = st.date_input(
            "Data de Nascimento",
            value=date(1985, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        
        idade = calcular_idade(data_nascimento)
        st.markdown(f"**Idade calculada:** {idade} anos")
        
        # Seleção de seguradoras
        st.markdown("### 🏢 **Seguradoras para Comparar**")
        
        todas_seguradoras = list(seguradoras.keys())
        selecionadas = st.multiselect(
            "Selecione as seguradoras (máx 7 para melhor visualização)",
            todas_seguradoras,
            default=["Tokyo Marine", "Porto Seguro", "Prudential", "Metlife", "Mag Seguros", "Omint", "Icatu"],
            max_selections=7,
            format_func=lambda x: f"{seguradoras[x]['icone']} {x}"
        )
        
        if len(selecionadas) < 2:
            st.warning("Selecione pelo menos 2 seguradoras para comparar")
            st.stop()
        
        # Período de análise em MESES para cada seguradora
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
        
        # Taxa IPCA
        st.markdown("### 📈 **Parâmetros Financeiros**")
        taxa_ipca = st.number_input(
            "Taxa IPCA (% a.a.)",
            min_value=0.0,
            max_value=20.0,
            value=5.0,
            step=0.1,
            format="%.1f"
        )
        
        # Botão de atualização
        if st.button("🔄 **ATUALIZAR ANÁLISE**", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"""
        <div style='text-align: center; color: #666; font-size: 0.9rem;'>
            <p>⚡ Análise em tempo real</p>
            <p>🔒 Dados protegidos</p>
            <p>📅 Atualizado: {datetime.now().strftime("%d/%m/%Y")}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Abas principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 VISÃO GERAL", 
        "🛡️ COBERTURAS", 
        "💰 FINANCEIRO", 
        "⭐ ANÁLISE", 
        "📋 CENÁRIOS",
        "🏆 RECOMENDAÇÃO",
        "🎯 APRESENTAÇÃO",
        "📄 RELATÓRIO"
    ])
    
    # Dicionário para armazenar os checklists por seguradora
    if 'checklist_assistencia_domiciliar' not in st.session_state:
        st.session_state.checklist_assistencia_domiciliar = {}
    if 'checklist_seguro_viagem' not in st.session_state:
        st.session_state.checklist_seguro_viagem = {}
    
    # Tab 1: Visão Geral
    with tab1:
        st.markdown("<div class='animate-fade-in-up'>", unsafe_allow_html=True)
        st.markdown("## 📊 **VISÃO GERAL COMPARATIVA**")
        
        # Métricas rápidas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class='metric-container'>
                <h4>👤 Cliente</h4>
                <h2 style='color: #667eea;'>{nome_cliente.split()[0]}</h2>
                <p>{idade} anos</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-container'>
                <h4>🏢 Seguradoras</h4>
                <h2 style='color: #764ba2;'>{len(selecionadas)}</h2>
                <p>comparadas</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-container'>
                <h4>📈 IPCA</h4>
                <h2 style='color: #10b981;'>{taxa_ipca}%</h2>
                <p>ao ano</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Tab 2: Coberturas (Editável) com Capital Segurado e Mensalidades
    with tab2:
        st.markdown("## 🛡️ **EDITAR CAPITAL SEGURADO E MENSALIDADES**")
        
        # Checklist para escolher entre mensal ou anual
        st.markdown("### 📅 **Escolha o período das mensalidades:**")
        col_check1, col_check2, col_check3 = st.columns([1, 1, 2])
        
        with col_check1:
            mostrar_mensal = st.checkbox("Mensal", value=True, key="check_mensal")
        
        with col_check2:
            mostrar_anual = st.checkbox("Anual", value=False, key="check_anual")
        
        with col_check3:
            if mostrar_mensal and mostrar_anual:
                st.success("✅ Mostrando valores mensais e anuais")
            elif mostrar_mensal:
                st.info("📅 Mostrando apenas valores mensais")
            elif mostrar_anual:
                st.info("📊 Mostrando apenas valores anuais")
            else:
                st.warning("⚠️ Selecione pelo menos uma opção")
        
        st.markdown("**Digite os valores com ponto para milhares e vírgula para decimais:**")
        st.markdown("*Exemplo: 1.000.000,00 ou 1000,50*")
        
        # Criar tabs para cada seguradora
        seguradora_tabs = st.tabs([f"✏️ {s}" for s in selecionadas])
        
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
                st.session_state.checklist_assistencia_domiciliar[seguradora] = st.checkbox(
                    "Incluir Assistência Domiciliar",
                    value=st.session_state.checklist_assistencia_domiciliar.get(seguradora, False),
                    key=f"assistencia_{seguradora}"
                )
                
                # Checklist para Seguro Viagem
                st.markdown("### ✈️ **Seguro Viagem**")
                st.session_state.checklist_seguro_viagem[seguradora] = st.checkbox(
                    "Incluir Seguro Viagem",
                    value=st.session_state.checklist_seguro_viagem.get(seguradora, False),
                    key=f"viagem_{seguradora}"
                )
                
                st.markdown("---")
                st.markdown("### 📋 **Coberturas Principais**")
                
                # Criar formulário para cada produto
                for produto in produtos_comuns:
                    with st.expander(f"**{produto}**", expanded=False):
                        col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                        
                        with col1:
                            # Capital Segurado (em branco para digitar)
                            if produto in seguradoras[seguradora]["produtos"]:
                                capital_atual = seguradoras[seguradora]["produtos"][produto]["capital"]
                            else:
                                capital_atual = ""
                            
                            novo_capital = criar_input_formatado(
                                "Capital Segurado",
                                capital_atual,
                                key=f"capital_{seguradora}_{produto}",
                                placeholder="Ex: 1.000.000,00"
                            )
                        
                        with col2:
                            # Mensalidade (se selecionado)
                            if mostrar_mensal:
                                if produto in seguradoras[seguradora]["produtos"]:
                                    mensalidade_atual = seguradoras[seguradora]["produtos"][produto]["mensalidade"]
                                else:
                                    mensalidade_atual = ""
                                
                                nova_mensalidade = criar_input_formatado(
                                    "Mensalidade",
                                    mensalidade_atual,
                                    key=f"mensal_{seguradora}_{produto}",
                                    placeholder="Ex: 320,00"
                                )
                        
                        with col3:
                            # Anualidade (se selecionado)
                            if mostrar_anual:
                                if produto in seguradoras[seguradora]["produtos"]:
                                    mensalidade_atual = seguradoras[seguradora]["produtos"][produto]["mensalidade"]
                                    if isinstance(mensalidade_atual, str):
                                        mensalidade_float = converter_string_para_float(mensalidade_atual)
                                    else:
                                        mensalidade_float = mensalidade_atual
                                    anualidade_atual = mensalidade_float * 12
                                else:
                                    anualidade_atual = ""
                                
                                nova_anualidade = criar_input_formatado(
                                    "Anualidade",
                                    anualidade_atual,
                                    key=f"anual_{seguradora}_{produto}",
                                    placeholder="Ex: 3840,00"
                                )
                                
                                # Se foi editado, calcular mensalidade
                                if nova_anualidade != anualidade_atual and nova_anualidade > 0:
                                    nova_mensalidade = nova_anualidade / 12
                        
                        with col4:
                            # Observação
                            if produto in seguradoras[seguradora]["produtos"]:
                                obs_atual = seguradoras[seguradora]["produtos"][produto]["observacao"]
                            else:
                                obs_atual = ""
                            
                            nova_obs = st.text_input(
                                "Observação",
                                value=obs_atual,
                                key=f"obs_{seguradora}_{produto}"
                            )
                        
                        # Atualizar dados
                        if produto not in seguradoras[seguradora]["produtos"]:
                            seguradoras[seguradora]["produtos"][produto] = {
                                "capital": "",
                                "mensalidade": "",
                                "observacao": ""
                            }
                        
                        # Atualizar capital
                        seguradoras[seguradora]["produtos"][produto]["capital"] = novo_capital
                        
                        # Atualizar mensalidade
                        if mostrar_mensal:
                            seguradoras[seguradora]["produtos"][produto]["mensalidade"] = nova_mensalidade if 'nova_mensalidade' in locals() else mensalidade_atual
                        elif mostrar_anual and 'nova_anualidade' in locals():
                            # Se apenas anual estiver selecionado, calcular mensalidade
                            seguradoras[seguradora]["produtos"][produto]["mensalidade"] = nova_anualidade / 12 if nova_anualidade > 0 else ""
                        
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
                    st.session_state.checklist_assistencia_domiciliar.get(seguradora, False),
                    st.session_state.checklist_seguro_viagem.get(seguradora, False)
                )
                
                col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                
                with col_res1:
                    st.metric("Capital Total", formatar_moeda(resultados_seguradora["total_capital"]))
                
                with col_res2:
                    if mostrar_mensal:
                        st.metric("Mensalidade Total", formatar_moeda(resultados_seguradora["total_mensalidade"]))
                    elif mostrar_anual:
                        st.metric("Anualidade Total", formatar_moeda(resultados_seguradora["total_mensalidade"] * 12))
                
                with col_res3:
                    st.metric("Prazo Principal", f"{resultados_seguradora['prazo_meses']} meses")
                
                with col_res4:
                    st.metric("Total Investido", formatar_moeda(resultados_seguradora["total_investimento_sem_ipca"]))
        
        # Resumo visual das coberturas principais
        st.markdown("---")
        st.markdown("## 📊 **RESUMO DO CAPITAL SEGURADO**")
        
        # Selecionar coberturas para visualização
        coberturas_visuais = st.multiselect(
            "Selecione coberturas para visualização do capital segurado",
            produtos_comuns,
            default=["Whole Life", "Doenças Graves", "Invalidez Acidental"],
            max_selections=4
        )
        
        if coberturas_visuais:
            num_viz_cols = min(2, len(coberturas_visuais))
            viz_cols = st.columns(num_viz_cols)
            
            for idx, cobertura in enumerate(coberturas_visuais):
                with viz_cols[idx % num_viz_cols]:
                    st.markdown(f"**{cobertura}**")
                    
                    # Coletar valores para esta cobertura
                    valores = []
                    cores = []
                    for seguradora in selecionadas:
                        if cobertura in seguradoras[seguradora]["produtos"]:
                            valor = seguradoras[seguradora]["produtos"][cobertura]["capital"]
                            if isinstance(valor, (int, float)):
                                valores.append(valor)
                                cores.append(seguradoras[seguradora]["cor"])
                            else:
                                # Tentar converter string para float
                                valor_float = converter_string_para_float(valor)
                                valores.append(valor_float)
                                cores.append(seguradoras[seguradora]["cor"])
                        else:
                            valores.append(0)
                            cores.append("#cccccc")
                    
                    if any(v > 0 for v in valores):
                        max_val = max(valores) if max(valores) > 0 else 1
                        
                        for i, (seguradora, valor, cor) in enumerate(zip(selecionadas, valores, cores)):
                            porcentagem = (valor / max_val) * 100 if max_val > 0 else 0
                            
                            st.markdown(f"""
                            <div style='margin: 0.5rem 0;'>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                                    <span style='font-size: 0.9rem; display: flex; align-items: center;'>
                                        <span class='indicator' style='background: {cor};'></span>
                                        {seguradora[:12]}{'...' if len(seguradora) > 12 else ''}
                                    </span>
                                    <span style='font-weight: bold;'>{formatar_moeda(valor)}</span>
                                </div>
                                <div class='progress-container'>
                                    <div class='progress-bar' style='width: {porcentagem}%; background: {cor};'></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Nenhum capital segurado configurado para esta cobertura")
    
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
                st.session_state.checklist_assistencia_domiciliar.get(seguradora, False),
                st.session_state.checklist_seguro_viagem.get(seguradora, False)
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
                    st.session_state.checklist_assistencia_domiciliar.get(seguradora, False),
                    st.session_state.checklist_seguro_viagem.get(seguradora, False)
                )
        
        for seguradora in selecionadas:
            dados = seguradoras[seguradora]
            resultado = resultados_completos.get(seguradora, {})
            
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
                            {formatar_moeda(resultado.get('mensal_whole_life', 0))}
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
                else:
                    st.info("Não possui benefícios adicionais")
            
            with col2:
                st.markdown("#### 📊 **Resumo Financeiro**")
                
                st.markdown(f"""
                <div style='background: {dados["cor"]}10; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span>Capital Total:</span>
                        <span style='font-weight: bold;'>{formatar_moeda(resultado.get('total_capital', 0))}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span>Mensalidade Total:</span>
                        <span style='font-weight: bold;'>{formatar_moeda(resultado.get('total_mensalidade', 0))}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span>Investimento Total:</span>
                        <span style='font-weight: bold;'>{formatar_moeda(resultado.get('total_investimento_com_ipca', 0))}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between;'>
                        <span>Prazo:</span>
                        <span style='font-weight: bold;'>{resultado.get('prazo_meses', 0)} meses</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Checklist status
                st.markdown("#### 📋 **Coberturas Adicionais**")
                if st.session_state.checklist_assistencia_domiciliar.get(seguradora, False):
                    st.markdown("✓ **Assistência Domiciliar incluída**")
                if st.session_state.checklist_seguro_viagem.get(seguradora, False):
                    st.markdown("✓ **Seguro Viagem incluído**")
            
            st.markdown("</div>")
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Tab 5: Cenários Personalizados
    with tab5:
        st.markdown("## 📋 **CENÁRIOS PERSONALIZADOS**")
        st.markdown("""
        **Compare diferentes cenários editando o capital segurado das coberturas.**
        *Ideal para quando um cliente traz uma apólice de banco e quer comparar com outras seguradoras.*
        """)
        
        # Criar tabela editável para todas as seguradoras selecionadas
        st.markdown("### ✏️ **Tabela de Comparação Completa (Capital Segurado)**")
        
        # Inicializar dataframe
        df_cenarios = criar_tabela_cenarios(seguradoras, selecionadas, produtos_comuns)
        
        # Configurar editor de dados
        column_config = {
            "Produto": st.column_config.TextColumn("Produto", width="medium")
        }
        
        for seguradora in selecionadas:
            column_config[seguradora] = st.column_config.NumberColumn(
                seguradora,
                min_value=0,
                max_value=10000000,
                step=1000,
                format="R$ %d"
            )
        
        # Editor de dados
        df_editado = st.data_editor(
            df_cenarios,
            column_config=column_config,
            use_container_width=True,
            num_rows="fixed",
            key="cenarios_editor"
        )
        
        # Análise dos cenários
        st.markdown("---")
        st.markdown("### 📊 **ANÁLISE DOS CENÁRIOS**")
        
        # Calcular totais por seguradora
        totais = {}
        for seguradora in selecionadas:
            if seguradora in df_editado.columns:
                totais[seguradora] = df_editado[seguradora].sum()
        
        if totais:
            # Encontrar seguradora com maior capital total
            seguradora_maior_capital = max(totais.items(), key=lambda x: x[1])[0]
            maior_valor = totais[seguradora_maior_capital]
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea20, #764ba210); 
                        padding: 1.5rem; border-radius: 15px; margin: 1rem 0;'>
                <h4 style='color: #667eea; margin: 0 0 0.5rem 0;'>🏆 Maior Capital Segurado Total</h4>
                <div style='display: flex; align-items: center; justify-content: space-between;'>
                    <h3 style='color: #667eea; margin: 0;'>{seguradora_maior_capital}</h3>
                    <h3 style='color: #667eea; margin: 0;'>{formatar_moeda(maior_valor)}</h3>
                </div>
                <p style='margin: 0.5rem 0 0 0; color: #666; font-size: 0.9rem;'>
                    Soma de todo o capital segurado configurado
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico de comparação
            st.markdown("#### 📈 Comparação Visual do Capital Segurado Total")
            
            max_total = max(totais.values())
            
            for seguradora, total in totais.items():
                cor = seguradoras[seguradora]["cor"]
                porcentagem = (total / max_total) * 100 if max_total > 0 else 0
                
                st.markdown(f"""
                <div style='margin: 1rem 0;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='width: 12px; height: 12px; background: {cor}; border-radius: 50%; margin-right: 0.5rem;'></div>
                            <span style='font-weight: 600;'>{seguradora}</span>
                        </div>
                        <span style='font-weight: bold; color: {cor};'>{formatar_moeda(total)}</span>
                    </div>
                    <div class='progress-container'>
                        <div class='progress-bar' style='width: {porcentagem}%; background: {cor};'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 6: Recomendação
    with tab6:
        st.markdown("## 🏆 **RECOMENDAÇÃO PERSONALIZADA**")
        
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
                    st.session_state.checklist_assistencia_domiciliar.get(seguradora, False),
                    st.session_state.checklist_seguro_viagem.get(seguradora, False)
                )
        
        # Sistema de pontuação
        pontuacoes = {}
        
        for seguradora in selecionadas:
            dados = seguradoras[seguradora]
            resultados_fin = resultados_completos.get(seguradora, {"total_investimento_com_ipca": 0, "prazo_meses": 0, "total_capital": 0})
            
            pontuacao = 0
            
            # Critério 1: Custo do Whole Life (30%)
            if resultados_completos:
                custos = [r["total_investimento_com_ipca"] for r in resultados_completos.values()]
                if custos:
                    max_custo = max(custos)
                    if max_custo > 0:
                        custo_normalizado = 1 - (resultados_fin["total_investimento_com_ipca"] / max_custo)
                        pontuacao += custo_normalizado * 30
            
            # Critério 2: Prazo (20%)
            if periodos_meses:
                prazos = [periodos_meses[s] for s in selecionadas]
                if prazos:
                    max_prazo = max(prazos)
                    if max_prazo > 0:
                        prazo_normalizado = 1 - (periodos_meses.get(seguradora, 0) / max_prazo)
                        pontuacao += prazo_normalizado * 20
            
            # Critério 3: Capital Segurado (30%)
            if resultados_completos:
                capitais = [r["total_capital"] for r in resultados_completos.values()]
                if capitais:
                    max_capital = max(capitais)
                    if max_capital > 0:
                        capital_normalizado = resultados_fin["total_capital"] / max_capital
                        pontuacao += capital_normalizado * 30
            
            # Critério 4: Benefícios (20%)
            beneficios = len(dados.get("beneficios_adicionais", []))
            max_beneficios = max([len(seguradoras[s].get("beneficios_adicionais", [])) for s in selecionadas])
            if max_beneficios > 0:
                pontuacao += (beneficios / max_beneficios) * 20
            
            pontuacoes[seguradora] = pontuacao
        
        # Determinar recomendação
        if pontuacoes:
            recomendacao = max(pontuacoes.items(), key=lambda x: x[1])[0]
            pontuacao_max = max(pontuacoes.values())
            cor_recomendacao = seguradoras[recomendacao]["cor"]
            
            # Exibir recomendação
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, {cor_recomendacao}20, {cor_recomendacao}10); 
                        border: 3px solid {cor_recomendacao}; 
                        border-radius: 25px; padding: 3rem; text-align: center; margin: 2rem 0;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>🏆</div>
                <h1 style='color: {cor_recomendacao}; font-size: 3.5rem; margin: 0 0 1rem 0;'>{recomendacao}</h1>
                <p style='font-size: 1.5rem; color: #666; margin: 0 0 2rem 0;'>
                    Recomendação baseada em análise multicritério
                </p>
                <div style='display: inline-block; background: {cor_recomendacao}; color: white; 
                            padding: 0.75rem 2rem; border-radius: 50px; font-size: 1.1rem; font-weight: bold;'>
                    Pontuação: {pontuacao_max:.1f}/100
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Tabela de pontuação
            st.markdown("### 📋 **DETALHAMENTO DA PONTUAÇÃO**")
            
            dados_pontuacao = []
            for seguradora, pontuacao in pontuacoes.items():
                dados_pontuacao.append({
                    "Seguradora": seguradora,
                    "Pontuação Total": f"{pontuacao:.1f}",
                    "Classificação": "🏆 RECOMENDADA" if seguradora == recomendacao else "⭐ ALTERNATIVA"
                })
            
            df_pontuacao = pd.DataFrame(dados_pontuacao)
            
            # Estilizar a tabela
            def colorizar_classificacao(val):
                if val == "🏆 RECOMENDADA":
                    return 'background-color: #10b98120; color: #10b981; font-weight: bold;'
                return ''
            
            st.dataframe(
                df_pontuacao.style.applymap(colorizar_classificacao, subset=['Classificação']),
                use_container_width=True
            )
        
        # Explicação dos critérios
        st.markdown("---")
        st.markdown("### 📊 **CRITÉRIOS DE ANÁLISE**")
        
        crit_cols = st.columns(4)
        
        criterios = [
            ("💰", "Custo Whole Life", "30%", "#667eea"),
            ("📅", "Prazo Pagamento", "20%", "#764ba2"),
            ("🛡️", "Capital Segurado", "30%", "#10b981"),
            ("🎁", "Benefícios Extras", "20%", "#f59e0b")
        ]
        
        for idx, (icone, nome, peso, cor) in enumerate(criterios):
            with crit_cols[idx]:
                st.markdown(f"""
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {cor};'>{icone}</div>
                    <h4>{nome}</h4>
                    <p style='font-size: 0.9rem; color: #666;'>{peso} do peso</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 7: Apresentação para Cliente
    with tab7:
        st.markdown(f"""
        <div class='presentation-section'>
            <div style='text-align: center; margin-bottom: 3rem;'>
                <h1 style='color: #667eea; font-size: 3.5rem; margin-bottom: 1rem;'>🎯 APRESENTAÇÃO FINAL</h1>
                <h3 style='color: #666; font-weight: 300;'>Análise completa para {nome_cliente}</h3>
                <p style='color: #888;'>Data: {datetime.now().strftime('%d/%m/%Y')} | Idade: {idade} anos</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Resumo executivo
        st.markdown("### 📋 **RESUMO EXECUTIVO**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class='modern-card'>
                <h3 style='color: #667eea;'>👤 Perfil do Cliente</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;'>
                    <div>
                        <p style='margin: 0; color: #666; font-size: 0.9rem;'>Nome</p>
                        <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>{nome_cliente}</p>
                    </div>
                    <div>
                        <p style='margin: 0; color: #666; font-size: 0.9rem;'>Idade</p>
                        <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>{idade} anos</p>
                    </div>
                    <div>
                        <p style='margin: 0; color: #666; font-size: 0.9rem;'>Seguradoras</p>
                        <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>{len(selecionadas)}</p>
                    </div>
                    <div>
                        <p style='margin: 0; color: #666; font-size: 0.9rem;'>IPCA</p>
                        <p style='margin: 0; font-weight: bold; font-size: 1.2rem;'>{taxa_ipca}% a.a.</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if 'recomendacao' in locals() and recomendacao in seguradoras:
                st.markdown(f"""
                <div class='modern-card'>
                    <h3 style='color: #10b981;'>🏆 Recomendação Principal</h3>
                    <div style='display: flex; align-items: center; margin-top: 1rem;'>
                        <div style='font-size: 3rem; margin-right: 1rem; color: {seguradoras[recomendacao]["cor"]};'>
                            {seguradoras[recomendacao]["icone"]}
                        </div>
                        <div>
                            <h2 style='color: {seguradoras[recomendacao]["cor"]}; margin: 0;'>{recomendacao}</h2>
                            <p style='margin: 0; color: #666;'>{seguradoras[recomendacao]['descricao']}</p>
                        </div>
                    </div>
                    <div style='margin-top: 1rem;'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span>Mensalidade Whole Life:</span>
                            <span style='font-weight: bold;'>{formatar_moeda(resultados_completos.get(recomendacao, {}).get('mensal_whole_life', 0))}</span>
                        </div>
                        <div style='display: flex; justify-content: space-between;'>
                            <span>Prazo:</span>
                            <span style='font-weight: bold;'>{periodos_meses.get(recomendacao, 0)} meses</span>
                        </div>
                        <div style='display: flex; justify-content: space-between;'>
                            <span>Capital Segurado Total:</span>
                            <span style='font-weight: bold;'>{formatar_moeda(resultados_completos.get(recomendacao, {}).get('total_capital', 0))}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='modern-card'>
                    <h3 style='color: #10b981;'>🏆 Recomendação Principal</h3>
                    <p>Execute a análise na aba "Recomendação" para obter a recomendação personalizada.</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Tab 8: Relatório
    with tab8:
        st.markdown("## 📄 **GERAR RELATÓRIO COMPLETO**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 **Visualizar Análise**")
            st.markdown("""
            **Relatório inclui:**
            - Dados do cliente e contexto
            - Metodologia da análise
            - Comparação detalhada das seguradoras
            - Análise de coberturas principais
            - Recomendação final justificada
            - Storytelling profissional
            """)
            
            if st.button("👁️ **VISUALIZAR RELATÓRIO**", use_container_width=True):
                if 'recomendacao' in locals() and recomendacao:
                    # Gerar texto do relatório
                    texto_relatorio = gerar_txt(nome_cliente, idade, selecionadas, resultados_completos, recomendacao, seguradoras, periodos_meses, taxa_ipca)
                    
                    # Exibir relatório
                    st.markdown("### 📋 **RELATÓRIO COMPLETO**")
                    st.text_area("Conteúdo do Relatório", texto_relatorio, height=400)
                else:
                    st.warning("Execute primeiro a análise na aba 'Recomendação'")
        
        with col2:
            st.markdown("### 📥 **Exportar Relatório**")
            st.markdown("""
            **Formato disponível:**
            - **TXT**: Formato simples para compartilhamento e impressão
            """)
            
            # Botão para exportar TXT
            if st.button("📝 **GERAR E BAIXAR TXT**", use_container_width=True):
                if 'recomendacao' in locals() and recomendacao:
                    # Gerar TXT
                    texto_relatorio = gerar_txt(nome_cliente, idade, selecionadas, resultados_completos, recomendacao, seguradoras, periodos_meses, taxa_ipca)
                    
                    # Criar botão de download
                    st.download_button(
                        label="⬇️ BAIXAR ARQUIVO TXT",
                        data=texto_relatorio,
                        file_name=f"Relatorio_Seguros_{nome_cliente}_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    st.success("TXT gerado com sucesso! Clique no botão acima para baixar.")
                else:
                    st.warning("Execute primeiro a análise na aba 'Recomendação'")
        
        # Instruções
        st.markdown("---")
        st.markdown("### 📋 **INSTRUÇÕES**")
        st.markdown("""
        1. **Complete todas as abas de análise** (especialmente a de Recomendação)
        2. **Personalize os dados** conforme necessário
        3. **Clique em 'Visualizar Relatório'** para pré-visualizar
        4. **Clique em 'Gerar e Baixar TXT'** para exportar
        5. **Baixe e compartilhe** com seu cliente
        """)

# Executar aplicativo
if __name__ == "__main__":
    main()





