import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import tempfile
import shutil
from comparacoes_criativas_interativas import adicionar_comparacoes_ao_painel
from analises_avancadas import (
    criar_heatmap_dia_semana_hora,
    criar_paleta_horarios,
    criar_comparativo_anos,
    criar_graficos_evolucao,
    gerar_recomendacoes,
    visualizar_recomendacoes
)

# Configuração da página
st.set_page_config(
    page_title="Spotify Analytics Avançado",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🎧"
)

# Aplicar tema personalizado
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #1DB954;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #1DB95420;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1DB954;
        color: white;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 1rem;
    }
    div.stButton > button:first-child {
        background-color: #1DB954;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #169c46;
        color: white;
    }
    .search-container {
        background-color: #1DB95410;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .result-container {
        background-color: #1DB95410;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .upload-container {
        background-color: rgba(29, 185, 84, 0.05);
        border: 1px dashed #1DB954;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        margin-bottom: 30px;
    }
    .spotify-logo {
        max-width: 180px;
        margin-bottom: 20px;
    }
    .welcome-text {
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    .instruction-text {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    .success-message {
        background-color: rgba(29, 185, 84, 0.1);
        border-left: 4px solid #1DB954;
        padding: 15px;
        border-radius: 4px;
        margin: 20px 0;
    }
    .error-message {
        background-color: rgba(255, 99, 71, 0.1);
        border-left: 4px solid tomato;
        padding: 15px;
        border-radius: 4px;
        margin: 20px 0;
    }
    .flow-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 20px;
    }
    .flow-item {
        background-color: rgba(29, 185, 84, 0.05);
        border-radius: 8px;
        padding: 10px 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .flow-number {
        background-color: #1DB954;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Função para validar arquivo JSON do Spotify
def validar_arquivo_spotify(conteudo):
    """
    Valida se o arquivo JSON contém dados do Spotify no formato esperado
    
    Args:
        conteudo: Conteúdo do arquivo JSON
        
    Returns:
        (bool, str): Tupla com status de validação e mensagem
    """
    try:
        # Verificar se é uma lista
        if not isinstance(conteudo, list):
            return False, "O arquivo deve conter uma lista de reproduções"
        
        # Verificar se há pelo menos um item
        if len(conteudo) == 0:
            return False, "O arquivo não contém dados de reprodução"
        
        # Verificar campos obrigatórios no primeiro item
        campos_obrigatorios = ['ts', 'ms_played', 'master_metadata_track_name', 
                              'master_metadata_album_artist_name', 'master_metadata_album_album_name']
        
        for campo in campos_obrigatorios:
            if campo not in conteudo[0]:
                return False, f"Campo obrigatório '{campo}' não encontrado nos dados"
        
        return True, "Arquivo válido"
    
    except Exception as e:
        return False, f"Erro ao validar arquivo: {str(e)}"

# Função para processar arquivos enviados
def processar_arquivos_enviados(arquivos_enviados):
    """
    Processa os arquivos JSON enviados pelo usuário
    
    Args:
        arquivos_enviados: Lista de arquivos enviados
        
    Returns:
        (bool, str, str): Tupla com status, mensagem e caminho da pasta temporária
    """
    try:
        # Criar pasta temporária para armazenar os arquivos
        pasta_temp = tempfile.mkdtemp()
        pasta_data = os.path.join(pasta_temp, 'data')
        os.makedirs(pasta_data, exist_ok=True)
        
        # Contador de arquivos válidos
        arquivos_validos = 0
        
        # Processar cada arquivo
        for arquivo in arquivos_enviados:
            try:
                # Ler conteúdo do arquivo
                conteudo = json.loads(arquivo.getvalue().decode('utf-8'))
                
                # Validar conteúdo
                valido, mensagem = validar_arquivo_spotify(conteudo)
                
                if valido:
                    # Salvar arquivo na pasta temporária
                    caminho_arquivo = os.path.join(pasta_data, f"spotify_{arquivos_validos}.json")
                    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                        json.dump(conteudo, f)
                    
                    arquivos_validos += 1
                else:
                    return False, f"Erro no arquivo {arquivo.name}: {mensagem}", ""
            
            except Exception as e:
                return False, f"Erro ao processar arquivo {arquivo.name}: {str(e)}", ""
        
        if arquivos_validos == 0:
            return False, "Nenhum arquivo válido foi enviado", ""
        
        return True, f"{arquivos_validos} arquivos processados com sucesso", pasta_temp
    
    except Exception as e:
        return False, f"Erro ao processar arquivos: {str(e)}", ""

# Função para carregar dados
@st.cache_data
def carregar_dados(pasta_dados):
    """
    Carrega dados dos arquivos JSON
    
    Args:
        pasta_dados: Caminho da pasta com os arquivos JSON
        
    Returns:
        DataFrame com os dados processados
    """
    caminho_pasta = os.path.join(pasta_dados, 'data')
    todos_dados = []

    for arquivo in os.listdir(caminho_pasta):
        if arquivo.endswith('.json'):
            with open(os.path.join(caminho_pasta, arquivo), 'r', encoding='utf-8') as f:
                dados = json.load(f)
                todos_dados.extend(dados)

    df = pd.DataFrame(todos_dados)

    df['ts'] = pd.to_datetime(df['ts'])
    df['ano'] = df['ts'].dt.year
    df['mes'] = df['ts'].dt.month
    df['dia'] = df['ts'].dt.day
    df['hora'] = df['ts'].dt.hour
    df['diaSemana'] = df['ts'].dt.day_name()

    df['segundos'] = df['ms_played'] / 1000
    df['minutos'] = df['segundos'] / 60
    df['horas'] = df['minutos'] / 60

    df['foi_pulado'] = df['skipped'] == True

    df['track'] = df['master_metadata_track_name']
    df['artist'] = df['master_metadata_album_artist_name']
    df['album'] = df['master_metadata_album_album_name']

    return df

# Função para encontrar músicas tocadas antes/depois
def encontrar_musicas_sequencia(df, musica_selecionada, direcao='depois', top_n=10):
    """
    Encontra as músicas mais tocadas antes ou depois de uma música específica
    
    Args:
        df: DataFrame com os dados
        musica_selecionada: Nome da música selecionada
        direcao: 'antes' ou 'depois'
        top_n: Número de músicas a retornar
        
    Returns:
        DataFrame com as músicas mais frequentes na sequência
    """
    # Ordenar por timestamp
    df_ordenado = df.sort_values('ts')
    
    # Encontrar índices da música selecionada
    indices_musica = df_ordenado[df_ordenado['track'] == musica_selecionada].index
    
    musicas_sequencia = []
    
    for idx in indices_musica:
        # Encontrar índice da próxima ou anterior música
        if direcao == 'depois':
            # Próxima música (índice + 1)
            if idx + 1 < len(df_ordenado):
                proxima_musica = df_ordenado.iloc[idx + 1]
                if not pd.isna(proxima_musica['track']):
                    musicas_sequencia.append({
                        'track': proxima_musica['track'],
                        'artist': proxima_musica['artist'],
                        'ts': proxima_musica['ts']
                    })
        else:
            # Música anterior (índice - 1)
            if idx - 1 >= 0:
                anterior_musica = df_ordenado.iloc[idx - 1]
                if not pd.isna(anterior_musica['track']):
                    musicas_sequencia.append({
                        'track': anterior_musica['track'],
                        'artist': anterior_musica['artist'],
                        'ts': anterior_musica['ts']
                    })
    
    # Converter para DataFrame
    if musicas_sequencia:
        df_sequencia = pd.DataFrame(musicas_sequencia)
        
        # Contar frequência
        contagem = df_sequencia.groupby(['track', 'artist']).size().reset_index(name='contagem')
        
        # Ordenar por contagem e retornar top N
        return contagem.sort_values('contagem', ascending=False).head(top_n)
    else:
        return pd.DataFrame(columns=['track', 'artist', 'contagem'])

# Função para buscar músicas por artista
def buscar_musicas_por_artista(df, artista):
    """
    Busca músicas de um artista específico
    
    Args:
        df: DataFrame com os dados
        artista: Nome do artista
        
    Returns:
        DataFrame com as músicas do artista ordenadas por tempo de escuta
    """
    # Filtrar por artista
    df_artista = df[df['artist'] == artista]
    
    # Agrupar por música e somar minutos
    musicas_artista = df_artista.groupby(['track', 'artist'])['minutos'].sum().reset_index()
    
    # Ordenar por tempo de escuta
    return musicas_artista.sort_values('minutos', ascending=False)

# Início do app
st.title("🎧 Spotify Analytics Avançado")

# Verificar se os dados já foram carregados
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
    st.session_state.pasta_temp = None

# Tela inicial para upload de dados
if not st.session_state.dados_carregados:
    st.markdown("### Bem-vindo ao Analisador Avançado de Dados do Spotify")
    
    # Container de upload estilizado
    st.markdown("""
    <div class="upload-container">
        <img src="https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png" class="spotify-logo" />
        <p class="welcome-text">Descubra insights detalhados sobre seus hábitos de escuta no Spotify com visualizações modernas e análises personalizadas.</p>
        <p class="instruction-text">Para começar, faça o upload dos seus arquivos JSON de histórico de reprodução do Spotify.<br>Você pode baixar seus dados em <a href="https://www.spotify.com/account/privacy/" target="_blank">spotify.com/account/privacy</a> → Solicitar dados → Histórico de reprodução.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Upload de arquivos
    arquivos_enviados = st.file_uploader(
        "Selecione seus arquivos JSON do Spotify",
        type=["json"],
        accept_multiple_files=True,
        help="Você pode selecionar múltiplos arquivos JSON do seu histórico de reprodução do Spotify."
    )
    
    # Botão para processar arquivos
    if arquivos_enviados:
        if st.button("Analisar meus dados", key="analisar_dados"):
            with st.spinner("Processando seus dados..."):
                # Processar arquivos
                sucesso, mensagem, pasta_temp = processar_arquivos_enviados(arquivos_enviados)
                
                if sucesso:
                    # Armazenar caminho da pasta temporária
                    st.session_state.pasta_temp = pasta_temp
                    st.session_state.dados_carregados = True
                    
                    # Exibir mensagem de sucesso
                    st.markdown(f"""
                    <div class="success-message">
                        <h3>✅ Dados carregados com sucesso!</h3>
                        <p>{mensagem}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Recarregar a página para mostrar as análises
                    st.rerun()
                else:
                    # Exibir mensagem de erro
                    st.markdown(f"""
                    <div class="error-message">
                        <h3>❌ Erro ao processar arquivos</h3>
                        <p>{mensagem}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Exibir instruções detalhadas
    with st.expander("Como obter seus dados do Spotify?"):
        st.markdown("""
        ### Como obter seus dados do Spotify
        
        1. Acesse [spotify.com/account/privacy](https://www.spotify.com/account/privacy/)
        2. Faça login na sua conta
        3. Role até a seção "Solicitar seus dados"
        4. Clique em "Solicitar"
        5. Selecione "Histórico de reprodução" e confirme
        6. Você receberá um e-mail quando seus dados estiverem prontos (geralmente em até 30 dias)
        7. Baixe o arquivo ZIP e extraia os arquivos JSON
        8. Faça upload dos arquivos JSON nesta página
        
        **Nota:** Os arquivos JSON do Spotify contêm seu histórico de reprodução detalhado, incluindo músicas, artistas, álbuns, timestamps e outros metadados.
        """)
    
    # Exibir exemplo com dados de demonstração
    with st.expander("Não tem seus dados? Use nosso exemplo de demonstração"):
        if st.button("Carregar dados de demonstração", key="carregar_demo"):
            # Criar pasta temporária para os dados de demonstração
            pasta_temp = tempfile.mkdtemp()
            pasta_data = os.path.join(pasta_temp, 'data')
            os.makedirs(pasta_data, exist_ok=True)
            
            # Criar arquivo de demonstração
            dados_demo = [
                {
                    "ts": "2024-01-01T12:30:45Z",
                    "ms_played": 18000000,
                    "master_metadata_track_name": "Exemplo de Música",
                    "master_metadata_album_artist_name": "Artista Exemplo",
                    "master_metadata_album_album_name": "Álbum Exemplo",
                    "reason_start": "trackdone",
                    "reason_end": "trackdone",
                    "skipped": False,
                    "offline": False,
                    "platform": "android"
                },
                {
                    "ts": "2024-01-01T12:34:45Z",
                    "ms_played": 24000000,
                    "master_metadata_track_name": "Outra Música",
                    "master_metadata_album_artist_name": "Outro Artista",
                    "master_metadata_album_album_name": "Outro Álbum",
                    "reason_start": "clickrow",
                    "reason_end": "fwdbtn",
                    "skipped": True,
                    "offline": True,
                    "platform": "ios"
                },
                {
                    "ts": "2024-01-02T18:30:45Z",
                    "ms_played": 30000000,
                    "master_metadata_track_name": "Música Popular",
                    "master_metadata_album_artist_name": "Artista Famoso",
                    "master_metadata_album_album_name": "Álbum Famoso",
                    "reason_start": "playbtn",
                    "reason_end": "trackdone",
                    "skipped": False,
                    "offline": False,
                    "platform": "desktop"
                },
                {
                    "ts": "2023-01-01T12:30:45Z",
                    "ms_played": 18000000,
                    "master_metadata_track_name": "Música Antiga",
                    "master_metadata_album_artist_name": "Artista Antigo",
                    "master_metadata_album_album_name": "Álbum Antigo",
                    "reason_start": "trackdone",
                    "reason_end": "trackdone",
                    "skipped": False,
                    "offline": False,
                    "platform": "android"
                },
                {
                    "ts": "2024-01-01T12:38:45Z",
                    "ms_played": 24000000,
                    "master_metadata_track_name": "Música Sequencial",
                    "master_metadata_album_artist_name": "Artista Exemplo",
                    "master_metadata_album_album_name": "Álbum Exemplo",
                    "reason_start": "trackdone",
                    "reason_end": "trackdone",
                    "skipped": False,
                    "offline": False,
                    "platform": "android"
                }
            ]
            
            # Multiplicar dados para ter mais exemplos
            dados_expandidos = []
            for i in range(20):
                for item in dados_demo:
                    novo_item = item.copy()
                    if i > 0:
                        # Modificar alguns campos para criar variação
                        novo_item["ts"] = f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T{i % 24:02d}:30:45Z"
                        if i % 3 == 0:
                            novo_item["master_metadata_track_name"] += f" {i}"
                            novo_item["master_metadata_album_artist_name"] += f" {i % 5}"
                    dados_expandidos.append(novo_item)
            
            # Salvar arquivo de demonstração
            with open(os.path.join(pasta_data, "spotify_demo.json"), 'w', encoding='utf-8') as f:
                json.dump(dados_expandidos, f)
            
            # Atualizar estado da sessão
            st.session_state.pasta_temp = pasta_temp
            st.session_state.dados_carregados = True
            
            # Exibir mensagem de sucesso
            st.markdown("""
            <div class="success-message">
                <h3>✅ Dados de demonstração carregados!</h3>
                <p>Os dados de demonstração foram carregados com sucesso. Clique em "Recarregar" para ver as análises.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para recarregar
            if st.button("Recarregar"):
                st.rerun()

# Painel principal com análises
else:
    # Carregar dados
    df = carregar_dados(st.session_state.pasta_temp)
    
    # Criar abas para organizar o conteúdo
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Visão Geral", 
        "🔍 Busca por Artista",
        "🔄 Fluxo Musical",
        "🎭 Estatísticas Divertidas", 
        "⏰ Análise de Horários", 
        "📈 Evolução e Comparativos"
    ])
    
    with tab1:
        st.header("📊 Visão Geral")
        
        # Botão para carregar novos dados
        if st.button("Carregar novos dados", key="novos_dados"):
            # Limpar pasta temporária
            if st.session_state.pasta_temp and os.path.exists(st.session_state.pasta_temp):
                shutil.rmtree(st.session_state.pasta_temp)
            
            # Resetar estado
            st.session_state.dados_carregados = False
            st.session_state.pasta_temp = None
            
            # Recarregar página
            st.rerun()
        
        # Cartões principais
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total de minutos", f"{df['minutos'].sum():,.0f}")
        col2.metric("Total de horas", f"{df['horas'].sum():,.0f}")
        col3.metric("Total de dias", f"{df['horas'].sum() / 24:,.1f}")
        col4.metric("Músicas ouvidas", f"{len(df):,}")
        
        # Top artistas
        st.subheader("👨‍🎤 Artistas mais ouvidos")
        top_artistas = df.groupby('artist')['minutos'].sum().sort_values(ascending=False).head(10)
        fig1 = px.bar(top_artistas, x=top_artistas.values, y=top_artistas.index, orientation='h', 
                     labels={'x':'Minutos', 'y':'Artista'}, 
                     color=top_artistas.values, color_continuous_scale='viridis',
                     template="plotly_dark")
        fig1.update_layout(height=500)
        st.plotly_chart(fig1, use_container_width=True)

        # Top músicas e álbuns em colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎶 Músicas mais ouvidas")
            top_musicas = df.groupby('track')['minutos'].sum().sort_values(ascending=False).head(10)
            fig2 = px.bar(top_musicas, x=top_musicas.values, y=top_musicas.index, orientation='h', 
                         labels={'x':'Minutos', 'y':'Música'}, 
                         color=top_musicas.values, color_continuous_scale='plasma',
                         template="plotly_dark")
            fig2.update_layout(height=500)
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            st.subheader("💿 Álbuns mais ouvidos")
            top_albuns = df.groupby('album')['minutos'].sum().sort_values(ascending=False).head(10)
            fig3 = px.bar(top_albuns, x=top_albuns.values, y=top_albuns.index, orientation='h', 
                         labels={'x':'Minutos', 'y':'Álbum'}, 
                         color=top_albuns.values, color_continuous_scale='inferno',
                         template="plotly_dark")
            fig3.update_layout(height=500)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Puladas vs completas e dispositivos em colunas
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("⏭️ Puladas vs Completas")
            qtd_puladas = df['foi_pulado'].sum()
            qtd_completas = len(df) - qtd_puladas
            fig6 = px.pie(values=[qtd_completas, qtd_puladas],
                          names=['Completas', 'Puladas'],
                          title='Proporção de faixas puladas',
                          color_discrete_sequence=px.colors.qualitative.Set2,
                          template="plotly_dark",
                          hole=0.4)
            fig6.update_layout(height=400)
            st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            st.subheader("📱 Dispositivos mais utilizados")
            dispositivos = df['platform'].value_counts().head(10)
            fig14 = px.bar(dispositivos, x=dispositivos.index, y=dispositivos.values,
                           labels={'x': 'Dispositivo', 'y': 'Execuções'},
                           color=dispositivos.values, color_continuous_scale='Viridis',
                           template="plotly_dark")
            fig14.update_layout(height=400)
            st.plotly_chart(fig14, use_container_width=True)
    
    with tab2:
        st.header("🔍 Busca por Artista")
        
        # Container de busca estilizado
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Obter lista de artistas para autocompletar
        todos_artistas = df['artist'].dropna().unique().tolist()
        
        # Criar lista de sugestões baseada no top 10
        top10_artistas = df.groupby('artist')['minutos'].sum().sort_values(ascending=False).head(10).index.tolist()
        
        # Exibir sugestões de top artistas
        st.markdown("### Sugestões de artistas populares")
        cols_sugestoes = st.columns(5)
        for i, artista in enumerate(top10_artistas[:5]):
            with cols_sugestoes[i]:
                if st.button(artista, key=f"sugestao_{i}"):
                    st.session_state.artista_selecionado = artista
        
        cols_sugestoes2 = st.columns(5)
        for i, artista in enumerate(top10_artistas[5:10]):
            with cols_sugestoes2[i]:
                if st.button(artista, key=f"sugestao2_{i}"):
                    st.session_state.artista_selecionado = artista
        
        # Campo de busca com autocompletar
        if 'artista_selecionado' not in st.session_state:
            st.session_state.artista_selecionado = ""
            
        artista_busca = st.text_input(
            "Buscar artista",
            value=st.session_state.artista_selecionado,
            placeholder="Digite o nome do artista...",
            key="busca_artista"
        )
        
        # Lista de sugestões baseada no input
        if artista_busca:
            sugestoes = [a for a in todos_artistas if artista_busca.lower() in a.lower()][:10]
            
            if sugestoes:
                st.markdown("### Sugestões de artistas")
                cols_auto = st.columns(5)
                for i, sugestao in enumerate(sugestoes[:5]):
                    with cols_auto[i]:
                        if st.button(sugestao, key=f"auto_{i}"):
                            st.session_state.artista_selecionado = sugestao
                            artista_busca = sugestao
                
                if len(sugestoes) > 5:
                    cols_auto2 = st.columns(5)
                    for i, sugestao in enumerate(sugestoes[5:10]):
                        with cols_auto2[i]:
                            if st.button(sugestao, key=f"auto2_{i}"):
                                st.session_state.artista_selecionado = sugestao
                                artista_busca = sugestao
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Exibir resultados da busca
        if artista_busca and artista_busca in todos_artistas:
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # Buscar músicas do artista
            musicas_artista = buscar_musicas_por_artista(df, artista_busca)
            
            # Calcular estatísticas do artista
            total_minutos = musicas_artista['minutos'].sum()
            total_musicas = len(musicas_artista)
            
            # Exibir estatísticas
            st.subheader(f"Estatísticas de {artista_busca}")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total de minutos", f"{total_minutos:,.0f}")
            col2.metric("Total de músicas", f"{total_musicas}")
            col3.metric("Média por música", f"{total_minutos/total_musicas if total_musicas > 0 else 0:,.1f}")
            
            # Exibir top músicas
            st.subheader(f"Top músicas de {artista_busca}")
            
            if not musicas_artista.empty:
                fig = px.bar(
                    musicas_artista.head(10),
                    x='minutos',
                    y='track',
                    orientation='h',
                    labels={'minutos': 'Minutos', 'track': 'Música'},
                    color='minutos',
                    color_continuous_scale='Viridis',
                    template="plotly_dark"
                )
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                # Exibir tabela com todas as músicas
                st.subheader("Todas as músicas")
                st.dataframe(
                    musicas_artista[['track', 'minutos']].reset_index(drop=True),
                    column_config={
                        "track": "Música",
                        "minutos": st.column_config.NumberColumn("Minutos", format="%.1f")
                    },
                    hide_index=True
                )
            else:
                st.info(f"Nenhuma música encontrada para {artista_busca}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.header("🔄 Fluxo Musical")
        
        # Container de busca estilizado
        st.markdown('<div class="search-container">', unsafe_allow_html=True)
        
        # Obter lista de músicas para autocompletar
        todas_musicas = df['track'].dropna().unique().tolist()
        
        # Criar lista de sugestões baseada no top 10
        top10_musicas = df.groupby('track')['minutos'].sum().sort_values(ascending=False).head(10).index.tolist()
        
        # Exibir sugestões de top músicas
        st.markdown("### Sugestões de músicas populares")
        cols_sugestoes = st.columns(5)
        for i, musica in enumerate(top10_musicas[:5]):
            with cols_sugestoes[i]:
                if st.button(musica, key=f"sugestao_musica_{i}"):
                    st.session_state.musica_selecionada = musica
        
        cols_sugestoes2 = st.columns(5)
        for i, musica in enumerate(top10_musicas[5:10]):
            with cols_sugestoes2[i]:
                if st.button(musica, key=f"sugestao_musica2_{i}"):
                    st.session_state.musica_selecionada = musica
        
        # Campo de busca com autocompletar
        if 'musica_selecionada' not in st.session_state:
            st.session_state.musica_selecionada = ""
            
        musica_busca = st.text_input(
            "Buscar música",
            value=st.session_state.musica_selecionada,
            placeholder="Digite o nome da música...",
            key="busca_musica"
        )
        
        # Lista de sugestões baseada no input
        if musica_busca:
            sugestoes = [m for m in todas_musicas if musica_busca.lower() in m.lower()][:10]
            
            if sugestoes:
                st.markdown("### Sugestões de músicas")
                cols_auto = st.columns(5)
                for i, sugestao in enumerate(sugestoes[:5]):
                    with cols_auto[i]:
                        if st.button(sugestao, key=f"auto_musica_{i}"):
                            st.session_state.musica_selecionada = sugestao
                            musica_busca = sugestao
                
                if len(sugestoes) > 5:
                    cols_auto2 = st.columns(5)
                    for i, sugestao in enumerate(sugestoes[5:10]):
                        with cols_auto2[i]:
                            if st.button(sugestao, key=f"auto_musica2_{i}"):
                                st.session_state.musica_selecionada = sugestao
                                musica_busca = sugestao
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Exibir resultados da busca
        if musica_busca and musica_busca in todas_musicas:
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # Encontrar músicas tocadas antes e depois
            musicas_depois = encontrar_musicas_sequencia(df, musica_busca, 'depois')
            musicas_antes = encontrar_musicas_sequencia(df, musica_busca, 'antes')
            
            # Exibir informações da música
            info_musica = df[df['track'] == musica_busca].iloc[0]
            artista = info_musica['artist']
            
            st.subheader(f"Fluxo musical para: {musica_busca}")
            st.markdown(f"**Artista:** {artista}")
            
            # Exibir fluxo musical em colunas
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔙 Top 10 músicas tocadas ANTES")
                
                if not musicas_antes.empty:
                    # Criar gráfico
                    fig_antes = px.bar(
                        musicas_antes,
                        x='contagem',
                        y='track',
                        orientation='h',
                        labels={'contagem': 'Frequência', 'track': 'Música', 'artist': 'Artista'},
                        color='contagem',
                        color_continuous_scale='Blues',
                        template="plotly_dark",
                        hover_data=['artist']
                    )
                    fig_antes.update_layout(height=500)
                    st.plotly_chart(fig_antes, use_container_width=True)
                    
                    # Exibir lista detalhada
                    st.markdown("### Lista detalhada")
                    for i, (_, row) in enumerate(musicas_antes.iterrows()):
                        st.markdown(f"""
                        <div class="flow-item">
                            <div class="flow-number">{i+1}</div>
                            <div>
                                <strong>{row['track']}</strong><br>
                                <small>{row['artist']} • {row['contagem']} vezes</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhuma música encontrada tocada antes desta música")
            
            with col2:
                st.subheader("🔜 Top 10 músicas tocadas DEPOIS")
                
                if not musicas_depois.empty:
                    # Criar gráfico
                    fig_depois = px.bar(
                        musicas_depois,
                        x='contagem',
                        y='track',
                        orientation='h',
                        labels={'contagem': 'Frequência', 'track': 'Música', 'artist': 'Artista'},
                        color='contagem',
                        color_continuous_scale='Greens',
                        template="plotly_dark",
                        hover_data=['artist']
                    )
                    fig_depois.update_layout(height=500)
                    st.plotly_chart(fig_depois, use_container_width=True)
                    
                    # Exibir lista detalhada
                    st.markdown("### Lista detalhada")
                    for i, (_, row) in enumerate(musicas_depois.iterrows()):
                        st.markdown(f"""
                        <div class="flow-item">
                            <div class="flow-number">{i+1}</div>
                            <div>
                                <strong>{row['track']}</strong><br>
                                <small>{row['artist']} • {row['contagem']} vezes</small>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nenhuma música encontrada tocada depois desta música")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.header("🎭 Estatísticas Divertidas")
        
        # Adicionar estatísticas divertidas e criativas interativas
        adicionar_comparacoes_ao_painel(df)
    
    with tab5:
        st.header("⏰ Análise de Horários")
        
        # Paleta de horários moderna
        st.subheader("🕒 Paleta de Horários")
        fig_paleta = criar_paleta_horarios(df)
        st.plotly_chart(fig_paleta, use_container_width=True)
        
        # Heatmap dia da semana vs hora
        st.subheader("📅 Heatmap: Dia da Semana x Hora")
        fig_heatmap = criar_heatmap_dia_semana_hora(df)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Filtros para análise de horários
        st.subheader("🔍 Análise Personalizada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            periodo_selecionado = st.selectbox(
                "Selecione um período do dia:",
                ["Todos", "Madrugada (0h-6h)", "Manhã (6h-12h)", "Tarde (12h-18h)", "Noite (18h-24h)"]
            )
        
        with col2:
            dia_selecionado = st.selectbox(
                "Selecione um dia da semana:",
                ["Todos", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            )
        
        # Filtrar dados conforme seleção
        df_filtrado = df.copy()
        
        # Mapear dias da semana para português
        mapa_dias = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        df_filtrado['dia_pt'] = df_filtrado['diaSemana'].map(mapa_dias)
        
        # Aplicar filtro de período
        if periodo_selecionado != "Todos":
            if periodo_selecionado == "Madrugada (0h-6h)":
                df_filtrado = df_filtrado[(df_filtrado['hora'] >= 0) & (df_filtrado['hora'] < 6)]
            elif periodo_selecionado == "Manhã (6h-12h)":
                df_filtrado = df_filtrado[(df_filtrado['hora'] >= 6) & (df_filtrado['hora'] < 12)]
            elif periodo_selecionado == "Tarde (12h-18h)":
                df_filtrado = df_filtrado[(df_filtrado['hora'] >= 12) & (df_filtrado['hora'] < 18)]
            elif periodo_selecionado == "Noite (18h-24h)":
                df_filtrado = df_filtrado[(df_filtrado['hora'] >= 18) & (df_filtrado['hora'] < 24)]
        
        # Aplicar filtro de dia
        if dia_selecionado != "Todos":
            df_filtrado = df_filtrado[df_filtrado['dia_pt'] == dia_selecionado]
        
        # Exibir resultados da análise personalizada
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Artistas no Período Selecionado")
            top_artistas_filtrado = df_filtrado.groupby('artist')['minutos'].sum().sort_values(ascending=False).head(5)
            
            if not top_artistas_filtrado.empty:
                fig_artistas_filtrado = px.bar(
                    top_artistas_filtrado, 
                    x=top_artistas_filtrado.values, 
                    y=top_artistas_filtrado.index, 
                    orientation='h',
                    labels={'x':'Minutos', 'y':'Artista'},
                    color=top_artistas_filtrado.values,
                    color_continuous_scale='Viridis',
                    template="plotly_dark"
                )
                fig_artistas_filtrado.update_layout(height=400)
                st.plotly_chart(fig_artistas_filtrado, use_container_width=True)
            else:
                st.info("Não há dados suficientes para o período selecionado.")
        
        with col2:
            st.subheader("Top Músicas no Período Selecionado")
            top_musicas_filtrado = df_filtrado.groupby('track')['minutos'].sum().sort_values(ascending=False).head(5)
            
            if not top_musicas_filtrado.empty:
                fig_musicas_filtrado = px.bar(
                    top_musicas_filtrado, 
                    x=top_musicas_filtrado.values, 
                    y=top_musicas_filtrado.index, 
                    orientation='h',
                    labels={'x':'Minutos', 'y':'Música'},
                    color=top_musicas_filtrado.values,
                    color_continuous_scale='Plasma',
                    template="plotly_dark"
                )
                fig_musicas_filtrado.update_layout(height=400)
                st.plotly_chart(fig_musicas_filtrado, use_container_width=True)
            else:
                st.info("Não há dados suficientes para o período selecionado.")
    
    with tab6:
        st.header("📈 Evolução e Comparativos")
        
        # Comparativo entre anos
        st.subheader("🗓️ Comparativo entre Anos")
        fig_comparativo = criar_comparativo_anos(df)
        
        if fig_comparativo:
            st.plotly_chart(fig_comparativo, use_container_width=True)
        else:
            st.info("Não há dados suficientes para comparar diferentes anos. É necessário ter dados de pelo menos dois anos.")
        
        # Gráficos de evolução
        st.subheader("📊 Evolução ao Longo do Tempo")
        fig_evolucao = criar_graficos_evolucao(df)
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        # Filtros para análise de evolução
        st.subheader("🔍 Análise de Evolução Personalizada")
        
        # Selecionar período para análise
        col1, col2 = st.columns(2)
        
        with col1:
            anos_disponiveis = sorted(df['ano'].dropna().unique())
            anos_selecionados = st.multiselect(
                "Selecione os anos para análise:",
                anos_disponiveis,
                default=anos_disponiveis[-2:] if len(anos_disponiveis) >= 2 else anos_disponiveis
            )
        
        with col2:
            metrica_selecionada = st.selectbox(
                "Selecione a métrica para análise:",
                ["Minutos ouvidos", "Quantidade de músicas", "Proporção de músicas puladas"]
            )
        
        # Filtrar dados conforme seleção
        if anos_selecionados:
            df_anos = df[df['ano'].isin(anos_selecionados)]
            
            # Agrupar por mês e ano
            df_evolucao = df_anos.groupby([df_anos['ts'].dt.year, df_anos['ts'].dt.month]).agg({
                'minutos': 'sum',
                'track': 'count',
                'foi_pulado': 'mean'
            }).rename_axis(['ano', 'mes']).reset_index()
            
            df_evolucao.columns = ['ano', 'mes', 'minutos', 'quantidade', 'proporcao_puladas']
            df_evolucao['data'] = pd.to_datetime({
                'year': df_evolucao['ano'],
                'month': df_evolucao['mes'],
                'day': 1  # Define o dia como 1 (ou outro valor fixo)
            })
            
            # Selecionar métrica para visualização
            if metrica_selecionada == "Minutos ouvidos":
                y_col = 'minutos'
                y_label = 'Minutos'
            elif metrica_selecionada == "Quantidade de músicas":
                y_col = 'quantidade'
                y_label = 'Quantidade'
            else:
                y_col = 'proporcao_puladas'
                y_label = 'Proporção de puladas'
                df_evolucao[y_col] = df_evolucao[y_col] * 100  # Converter para percentual
            
            # Criar gráfico de evolução personalizado
            fig_evolucao_personalizada = px.line(
                df_evolucao,
                x='data',
                y=y_col,
                color='ano',
                markers=True,
                labels={'data': 'Data', y_col: y_label},
                title=f'Evolução de {metrica_selecionada} por mês',
                template="plotly_dark"
            )
            
            fig_evolucao_personalizada.update_layout(height=500)
            st.plotly_chart(fig_evolucao_personalizada, use_container_width=True)
        else:
            st.info("Selecione pelo menos um ano para visualizar a evolução.")

# Rodapé
st.markdown("---")
st.caption("Feito com ❤️ usando Python, Streamlit e Plotly | Análise avançada de dados do Spotify")
