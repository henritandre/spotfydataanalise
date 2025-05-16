import pandas as pd
import streamlit as st
import random
import math
import pycountry
import json
import os

# Dicionário de cidades por país/região
def carregar_cidades_por_regiao():
    """
    Carrega um dicionário de cidades por país/região.
    Retorna um dicionário onde as chaves são os países e os valores são listas de tuplas (cidade, distância em km)
    """
    cidades = {
        "Brasil": [
            ("São Paulo", 960),
            ("Rio de Janeiro", 1260),
            ("Brasília", 140),
            ("Salvador", 1800),
            ("Fortaleza", 2100),
            ("Belo Horizonte", 800),
            ("Manaus", 2500),
            ("Curitiba", 1200),
            ("Recife", 2300),
            ("Porto Alegre", 2000),
            ("Belém", 2200),
            ("Goiânia", 70),
            ("Florianópolis", 1600),
            ("Natal", 2500),
            ("Vitória", 1400)
        ],
        "Estados Unidos": [
            ("Nova York", 8500),
            ("Los Angeles", 9800),
            ("Chicago", 8900),
            ("Houston", 8200),
            ("Phoenix", 9000),
            ("Filadélfia", 8600),
            ("San Antonio", 8300),
            ("San Diego", 9700),
            ("Dallas", 8100),
            ("San Jose", 9900),
            ("Austin", 8200),
            ("Jacksonville", 8000),
            ("Fort Worth", 8100),
            ("Columbus", 8700),
            ("Charlotte", 8400)
        ],
        "Europa": [
            ("Londres", 9300),
            ("Paris", 9500),
            ("Madri", 8800),
            ("Roma", 9700),
            ("Berlim", 10200),
            ("Atenas", 10500),
            ("Amsterdã", 9800),
            ("Viena", 10100),
            ("Bruxelas", 9700),
            ("Lisboa", 8500),
            ("Estocolmo", 10800),
            ("Praga", 10300),
            ("Budapeste", 10400),
            ("Varsóvia", 10600),
            ("Dublin", 9200)
        ],
        "Ásia": [
            ("Tóquio", 18000),
            ("Pequim", 17500),
            ("Seul", 17800),
            ("Mumbai", 14500),
            ("Xangai", 17300),
            ("Delhi", 14300),
            ("Singapura", 16800),
            ("Bangkok", 16500),
            ("Hong Kong", 17000),
            ("Dubai", 12500),
            ("Kuala Lumpur", 16700),
            ("Taipei", 17500),
            ("Jakarta", 16900),
            ("Manila", 17200),
            ("Osaka", 18100)
        ]
    }
    return cidades

# Pool de curiosidades diversas
def obter_pool_curiosidades():
    """
    Retorna uma lista de funções que geram curiosidades baseadas no tempo total de escuta
    """
    curiosidades = [
        # Maratona de filmes
        lambda horas: f"Com o tempo que você passou ouvindo músicas ({horas:.1f} horas), poderia assistir à saga completa de O Senhor dos Anéis e O Hobbit {math.floor(horas / 17.2)} vezes completas.",
        
        # Livros lidos
        lambda horas: f"No tempo que você passou ouvindo músicas ({horas:.1f} horas), poderia ter lido aproximadamente {math.floor(horas / 5)} livros.",
        
        # Tempo de sono
        lambda horas: f"O tempo que você passou ouvindo músicas ({horas:.1f} horas) equivale a {(horas / 8):.1f} noites de sono (de 8 horas cada).",
        
        # Maratonas de corrida
        lambda horas: f"Você poderia ter completado {math.floor(horas / 4.5)} maratonas de corrida no tempo que passou ouvindo músicas ({horas:.1f} horas).",
        
        # Episódios de série
        lambda horas: f"Você poderia ter assistido a {math.floor(horas / 0.75)} episódios de série de 45 minutos cada durante o tempo que passou ouvindo músicas ({horas:.1f} horas).",
        
        # Volta ao mundo (circunferência da Terra ~40.000 km)
        lambda horas: f"Se você dirigisse sem parar a 80 km/h durante o tempo que passou ouvindo músicas ({horas:.1f} horas), poderia percorrer {(horas * 80):.0f} km, o que equivale a {(horas * 80 / 40000):.2f} voltas ao redor da Terra.",
        
        # Distância até a Lua (~384.400 km)
        lambda horas: f"A distância que você poderia percorrer no tempo que passou ouvindo músicas ({horas:.1f} horas) equivale a {((horas * 80 / 384400) * 100):.1f}% do caminho até a Lua.",
        
        # Aulas na faculdade/escola
        lambda horas: f"Você poderia ter assistido a {math.floor(horas)} aulas de 1 hora durante o tempo que passou ouvindo músicas ({horas:.1f} horas).",
        
        # Partidas de futebol
        lambda horas: f"O tempo que você passou ouvindo músicas ({horas:.1f} horas) equivale a {math.floor(horas / 1.5)} partidas de futebol completas.",
        
        # Filmes da Marvel
        lambda horas: f"Com o tempo que você passou ouvindo músicas ({horas:.1f} horas), poderia assistir a {math.floor(horas / 2.5)} filmes do Universo Cinematográfico Marvel.",
        
        # Viagem de avião
        lambda horas: f"O tempo que você passou ouvindo músicas ({horas:.1f} horas) equivale a uma viagem de avião de São Paulo até {['Tóquio', 'Nova York', 'Londres', 'Paris', 'Sydney'][random.randint(0, 4)]}.",
        
        # Crescimento de cabelo
        lambda horas: f"Durante o tempo que você passou ouvindo músicas ({horas:.1f} horas), seu cabelo cresceu aproximadamente {(horas * 0.017):.1f} mm (considerando que o cabelo cresce cerca de 1 cm por mês).",
        
        # Batimentos cardíacos
        lambda horas: f"Durante o tempo que você passou ouvindo músicas ({horas:.1f} horas), seu coração bateu aproximadamente {int(horas * 60 * 70):,} vezes (considerando 70 batimentos por minuto).",
        
        # Respirações
        lambda horas: f"Durante o tempo que você passou ouvindo músicas ({horas:.1f} horas), você respirou aproximadamente {int(horas * 60 * 16):,} vezes (considerando 16 respirações por minuto).",
        
        # Calorias queimadas em repouso
        lambda horas: f"Durante o tempo que você passou ouvindo músicas ({horas:.1f} horas), seu corpo queimou aproximadamente {int(horas * 70):,} calorias em repouso."
    ]
    return curiosidades

# Função para identificar a região com base na cidade informada
def identificar_regiao(cidade):
    """
    Identifica a região/país com base na cidade informada pelo usuário.
    Retorna a região identificada ou "Brasil" como padrão.
    """
    # Lista de cidades brasileiras conhecidas
    cidades_brasil = ["são paulo", "rio de janeiro", "brasília", "brasilia", "salvador", 
                      "fortaleza", "belo horizonte", "manaus", "curitiba", "recife", 
                      "porto alegre", "belém", "belem", "goiânia", "goiania", "anápolis", 
                      "anapolis", "florianópolis", "florianopolis", "natal", "vitória", "vitoria"]
    
    # Lista de cidades americanas conhecidas
    cidades_eua = ["new york", "nova york", "los angeles", "chicago", "houston", "phoenix", 
                   "philadelphia", "filadélfia", "filadelfia", "san antonio", "san diego", 
                   "dallas", "san jose", "austin", "jacksonville", "fort worth", "columbus", 
                   "charlotte", "denver", "seattle", "boston", "las vegas", "miami"]
    
    # Lista de cidades europeias conhecidas
    cidades_europa = ["london", "londres", "paris", "madrid", "madri", "rome", "roma", 
                      "berlin", "berlim", "athens", "atenas", "amsterdam", "amsterdã", 
                      "vienna", "viena", "brussels", "bruxelas", "lisbon", "lisboa", 
                      "stockholm", "estocolmo", "prague", "praga", "budapest", "budapeste", 
                      "warsaw", "varsóvia", "varsovia", "dublin"]
    
    # Lista de cidades asiáticas conhecidas
    cidades_asia = ["tokyo", "tóquio", "toquio", "beijing", "pequim", "seoul", "seul", 
                    "mumbai", "shanghai", "xangai", "delhi", "singapore", "singapura", 
                    "bangkok", "hong kong", "dubai", "kuala lumpur", "taipei", "jakarta", 
                    "manila", "osaka"]
    
    # Normaliza a cidade (remove acentos, converte para minúsculas)
    cidade_norm = cidade.lower()
    
    # Verifica em qual lista a cidade se encontra
    if cidade_norm in cidades_brasil:
        return "Brasil"
    elif cidade_norm in cidades_eua:
        return "Estados Unidos"
    elif cidade_norm in cidades_europa:
        return "Europa"
    elif cidade_norm in cidades_asia:
        return "Ásia"
    else:
        # Se não encontrar, tenta fazer uma correspondência parcial
        for c in cidades_brasil:
            if c in cidade_norm or cidade_norm in c:
                return "Brasil"
        for c in cidades_eua:
            if c in cidade_norm or cidade_norm in c:
                return "Estados Unidos"
        for c in cidades_europa:
            if c in cidade_norm or cidade_norm in c:
                return "Europa"
        for c in cidades_asia:
            if c in cidade_norm or cidade_norm in c:
                return "Ásia"
        
        # Se ainda não encontrar, retorna Brasil como padrão
        return "Brasil"

# Função para selecionar cidades aleatórias de uma região
def selecionar_cidades_aleatorias(regiao, num_cidades=3):
    """
    Seleciona um número específico de cidades aleatórias de uma região.
    
    Args:
        regiao: A região/país para selecionar cidades
        num_cidades: Número de cidades a selecionar
        
    Returns:
        Lista de tuplas (cidade, distância)
    """
    cidades_por_regiao = carregar_cidades_por_regiao()
    
    if regiao in cidades_por_regiao:
        # Seleciona cidades aleatórias da região
        cidades_disponiveis = cidades_por_regiao[regiao]
        if len(cidades_disponiveis) <= num_cidades:
            return cidades_disponiveis
        else:
            return random.sample(cidades_disponiveis, num_cidades)
    else:
        # Se a região não for reconhecida, usa Brasil como padrão
        cidades_disponiveis = cidades_por_regiao["Brasil"]
        return random.sample(cidades_disponiveis, num_cidades)

# Função para calcular comparações de viagem
def calcular_comparacao_viagem(horas_totais, cidade_origem, cidade_destino, distancia):
    """
    Calcula uma comparação de viagem baseada no tempo total de escuta.
    
    Args:
        horas_totais: Tempo total de escuta em horas
        cidade_origem: Cidade de origem do usuário
        cidade_destino: Cidade de destino para comparação
        distancia: Distância em km entre as cidades
        
    Returns:
        Texto da comparação
    """
    # Velocidade média em rodovias (km/h)
    velocidade_media = 80  # Considerando paradas e tráfego
    
    # Distância total possível com o tempo de escuta
    distancia_total_possivel = horas_totais * velocidade_media
    
    # Calcula quantas viagens completas (ida e volta) são possíveis
    viagens_ida_volta = distancia_total_possivel / (distancia * 2)
    
    # Calcula quantas viagens de ida são possíveis
    viagens_ida = distancia_total_possivel / distancia
    
    # Tempo necessário para uma viagem de ida
    tempo_ida = distancia / velocidade_media
    
    # Formata o texto da comparação
    if viagens_ida_volta >= 1:
        # Se for possível fazer pelo menos uma viagem completa (ida e volta)
        return f"Com o tempo que você passou ouvindo músicas ({horas_totais:.1f} horas), poderia ir de {cidade_origem} até {cidade_destino} e voltar {math.floor(viagens_ida_volta)} vezes completas."
    elif viagens_ida >= 1:
        # Se for possível fazer pelo menos uma viagem de ida
        return f"Com o tempo que você passou ouvindo músicas ({horas_totais:.1f} horas), poderia ir de {cidade_origem} até {cidade_destino} {math.floor(viagens_ida)} vezes."
    else:
        # Se não for possível completar uma viagem de ida
        percentual = (distancia_total_possivel / distancia) * 100
        return f"O tempo que você passou ouvindo músicas ({horas_totais:.1f} horas) equivale a {percentual:.1f}% do tempo necessário para ir de {cidade_origem} até {cidade_destino}."

# Função para selecionar curiosidades aleatórias
def selecionar_curiosidades_aleatorias(horas_totais, num_curiosidades=2):
    """
    Seleciona um número específico de curiosidades aleatórias.
    
    Args:
        horas_totais: Tempo total de escuta em horas
        num_curiosidades: Número de curiosidades a selecionar
        
    Returns:
        Lista de textos de curiosidades
    """
    pool_curiosidades = obter_pool_curiosidades()
    
    # Seleciona curiosidades aleatórias
    curiosidades_selecionadas = random.sample(pool_curiosidades, min(num_curiosidades, len(pool_curiosidades)))
    
    # Gera os textos das curiosidades
    return [curiosidade(horas_totais) for curiosidade in curiosidades_selecionadas]

# Função para adicionar as comparações ao painel do Streamlit
def adicionar_comparacoes_ao_painel(df):
    """
    Adiciona as comparações criativas ao painel do Streamlit
    
    Args:
        df: DataFrame com os dados do Spotify
    """
    # Calcular o tempo total em horas
    horas_totais = df['horas'].sum()
    
    # Adicionar seção de estatísticas divertidas ao painel
    st.subheader("🎭 Estatísticas Divertidas")
    st.write(f"Você passou um total de **{horas_totais:.1f} horas** ouvindo músicas. Vamos ver o que você poderia fazer com esse tempo!")
    
    # Criar um formulário para a localização
    with st.form(key='localizacao_form'):
        col1, col2 = st.columns([3, 1])
        with col1:
            cidade_origem = st.text_input("Qual é a sua cidade atual?", placeholder="Ex: Rio de Janeiro, Nova York, Londres...")
        with col2:
            submit_button = st.form_submit_button(label='Confirmar')
            
    # Checkbox para mostrar apenas curiosidades (sem comparações de viagem)
    mostrar_apenas_curiosidades = st.checkbox("Mostrar apenas curiosidades (sem comparações de viagem)", value=False)
    
    # Inicializa a chave de sessão para controlar os refreshes
    if 'refresh_count' not in st.session_state:
        st.session_state.refresh_count = 0
    
    # Se o usuário informou a cidade e não quer apenas curiosidades
    if cidade_origem and not mostrar_apenas_curiosidades:
        # Identifica a região com base na cidade informada
        regiao = identificar_regiao(cidade_origem)
        
        # Seleciona cidades aleatórias da região
        cidades_aleatorias = selecionar_cidades_aleatorias(regiao, 2)
        
        # Cria comparações de viagem
        comparacoes_viagem = []
        for cidade, distancia in cidades_aleatorias:
            comparacao = calcular_comparacao_viagem(horas_totais, cidade_origem, cidade, distancia)
            comparacoes_viagem.append(comparacao)
        
        # Seleciona curiosidades aleatórias
        curiosidades = selecionar_curiosidades_aleatorias(horas_totais, 2)
        
        # Exibe as comparações de viagem
        st.subheader("🚗 Comparações de Viagem")
        for i, comparacao in enumerate(comparacoes_viagem):
            st.info(comparacao)
            
        # Botão para atualizar as comparações de viagem
        if st.button("🔄 Mostrar outras cidades", key=f"refresh_viagens_{st.session_state.refresh_count}"):
            st.session_state.refresh_count += 1
            st.rerun()
        
        # Exibe as curiosidades
        st.subheader("🎮 Outras Curiosidades")
        for curiosidade in curiosidades:
            st.success(curiosidade)
            
        # Botão para atualizar as curiosidades
        if st.button("🔄 Mostrar outras curiosidades", key=f"refresh_curiosidades_{st.session_state.refresh_count}"):
            st.session_state.refresh_count += 1
            st.rerun()
            
    else:
        # Se o usuário não informou a cidade ou quer apenas curiosidades
        # Seleciona mais curiosidades aleatórias
        curiosidades = selecionar_curiosidades_aleatorias(horas_totais, 2)
        
        # Exibe as curiosidades
        st.subheader("🎮 Curiosidades")
        for curiosidade in curiosidades:
            st.success(curiosidade)
            
        # Botão para atualizar as curiosidades
        if st.button("🔄 Mostrar outras curiosidades", key=f"refresh_curiosidades_{st.session_state.refresh_count}"):
            st.session_state.refresh_count += 1
            st.rerun()
