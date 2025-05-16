import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import random
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from collections import Counter

# Função para criar heatmap de dia da semana vs hora
def criar_heatmap_dia_semana_hora(df):
    """
    Cria um heatmap que mostra a intensidade de escuta por dia da semana e hora do dia
    
    Args:
        df: DataFrame com os dados do Spotify
        
    Returns:
        Figura do Plotly com o heatmap
    """
    # Mapear dias da semana para ordem correta (começando segunda)
    mapa_dias = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Criar DataFrame para o heatmap
    df['dia_pt'] = df['diaSemana'].map(mapa_dias)
    heatmap_data = df.groupby(['dia_pt', 'hora'])['minutos'].sum().reset_index()
    
    # Criar matriz para o heatmap
    heatmap_matrix = pd.pivot_table(
        heatmap_data, 
        values='minutos', 
        index='dia_pt',
        columns='hora',
        fill_value=0
    )
    
    # Reordenar os dias da semana
    heatmap_matrix = heatmap_matrix.reindex(ordem_dias)
    
    # Criar heatmap com Plotly
    fig = px.imshow(
        heatmap_matrix,
        labels=dict(x="Hora do dia", y="Dia da semana", color="Minutos"),
        x=list(range(24)),
        y=ordem_dias,
        color_continuous_scale='viridis',
        aspect="auto"
    )
    
    fig.update_layout(
        title="Heatmap: Quando você mais ouve música?",
        xaxis_title="Hora do dia",
        yaxis_title="Dia da semana",
        coloraxis_colorbar=dict(title="Minutos"),
        height=500
    )
    
    # Adicionar anotações para destacar os períodos de maior atividade
    max_valor = heatmap_matrix.max().max()
    for i, dia in enumerate(ordem_dias):
        for j in range(24):
            valor = heatmap_matrix.loc[dia, j]
            if valor > 0.7 * max_valor:
                fig.add_annotation(
                    x=j, y=dia,
                    text="🔥",
                    showarrow=False,
                    font=dict(size=16)
                )
    
    return fig

# Função para criar paleta de horários moderna
def criar_paleta_horarios(df):
    """
    Cria uma visualização moderna da distribuição de escuta por hora do dia
    
    Args:
        df: DataFrame com os dados do Spotify
        
    Returns:
        Figura do Plotly com a paleta de horários
    """
    # Agrupar por hora
    df_horas = df.groupby('hora')['minutos'].sum().reset_index()
    
    # Definir períodos do dia
    df_horas['periodo'] = pd.cut(
        df_horas['hora'],
        bins=[0, 6, 12, 18, 24],
        labels=['Madrugada (0h-6h)', 'Manhã (6h-12h)', 'Tarde (12h-18h)', 'Noite (18h-24h)'],
        include_lowest=True
    )
    
    # Criar figura com subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Distribuição por hora do dia", "Distribuição por período do dia"),
        vertical_spacing=0.3,
        row_heights=[0.7, 0.3],
        specs = [
            [{"type": "bar"}],  # Gráfico de barras
            [{"type": "pie"}]  # Gráfico de pizza
        ]
    )
    
    # Adicionar gráfico de barras por hora
    colors = px.colors.sequential.Viridis
    bar_colors = [colors[int(i/24 * len(colors))] for i in df_horas['hora']]
    
    fig.add_trace(
        go.Bar(
            x=df_horas['hora'],
            y=df_horas['minutos'],
            marker=dict(color=bar_colors),
            hovertemplate='Hora: %{x}h<br>Minutos: %{y:.1f}<extra></extra>',
            name='Minutos por hora'
        ),
        row=1, col=1
    )
    
    # Adicionar linha de tendência suavizada
    fig.add_trace(
        go.Scatter(
            x=df_horas['hora'],
            y=df_horas['minutos'].rolling(window=3, center=True, min_periods=1).mean(),
            mode='lines',
            line=dict(color='rgba(255, 255, 255, 0.5)', width=3),
            hoverinfo='skip',
            name='Tendência'
        ),
        row=1, col=1
    )
    
    # Adicionar gráfico de pizza por período
    periodo_data = df_horas.groupby('periodo')['minutos'].sum().reset_index()
    
    # Cores para os períodos
    periodo_colors = ['#2E294E', '#541388', '#F1E9DA', '#FFD400']
    
    fig = make_subplots(
        rows=2, cols=1,
        specs=[
            [{"type": "xy"}],  # Primeira linha - gráfico XY (linha, barra, etc)
            [{"type": "domain"}]  # Segunda linha - gráfico de pizza ou donut (que usam "domain")
        ]
    )
    fig.add_trace(
        go.Pie(
            labels=periodo_data['periodo'],
            values=periodo_data['minutos'],
            textinfo='percent+label',
            marker=dict(colors=periodo_colors),
            hole=0.4,
            hovertemplate='%{label}<br>Minutos: %{value:.1f}<br>Porcentagem: %{percent}<extra></extra>',
            name='Períodos do dia'
        ),
        row=2, col=1
    )
    
    # Atualizar layout
    fig.update_layout(
        title="Paleta de Horários: Quando você mais ouve música?",
        showlegend=False,
        height=800,
        template="plotly_dark"
    )
    
    # Atualizar eixos
    fig.update_xaxes(title_text="Hora do dia", row=1, col=1)
    fig.update_yaxes(title_text="Minutos", row=1, col=1)
    
    # Adicionar anotações para destacar os horários de pico
    hora_pico = df_horas.loc[df_horas['minutos'].idxmax()]
    fig.add_annotation(
        x=hora_pico['hora'],
        y=hora_pico['minutos'],
        text=f"Pico às {int(hora_pico['hora'])}h",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40,
        font=dict(size=12, color="white"),
        bgcolor="rgba(0,0,0,0.7)",
        bordercolor="white",
        borderwidth=1,
        borderpad=4,
        row=1, col=1
    )
    
    return fig

# Função para criar comparativo entre anos
def criar_comparativo_anos(df):
    """
    Cria visualizações comparativas entre diferentes anos
    
    Args:
        df: DataFrame com os dados do Spotify
        
    Returns:
        Figura do Plotly com o comparativo entre anos
    """
    # Verificar se há mais de um ano nos dados
    anos = sorted(df['ano'].dropna().unique())
    if len(anos) <= 1:
        return None
    
    # Criar figura com subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Minutos ouvidos por ano",
            "Top 5 artistas por ano",
            "Distribuição por hora do dia",
            "Proporção de músicas puladas"
        ),
        specs=[
            [{"type": "bar"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "pie"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Minutos ouvidos por ano
    minutos_por_ano = df.groupby('ano')['minutos'].sum().reset_index()
    
    fig.add_trace(
        go.Bar(
            x=minutos_por_ano['ano'],
            y=minutos_por_ano['minutos'],
            marker=dict(color=px.colors.qualitative.Plotly),
            hovertemplate='Ano: %{x}<br>Minutos: %{y:.1f}<extra></extra>',
            name='Minutos por ano'
        ),
        row=1, col=1
    )
    
    # 2. Top 5 artistas por ano (último ano vs. penúltimo ano)
    if len(anos) >= 2:
        ultimo_ano = anos[-1]
        penultimo_ano = anos[-2]
        
        # Top 5 artistas do último ano
        top_artistas_ultimo = df[df['ano'] == ultimo_ano].groupby('artist')['minutos'].sum().nlargest(5).reset_index()
        top_artistas_ultimo['ano'] = ultimo_ano
        
        # Top 5 artistas do penúltimo ano
        top_artistas_penultimo = df[df['ano'] == penultimo_ano].groupby('artist')['minutos'].sum().nlargest(5).reset_index()
        top_artistas_penultimo['ano'] = penultimo_ano
        
        # Combinar os dados
        top_artistas_combinado = pd.concat([top_artistas_ultimo, top_artistas_penultimo])
        
        fig.add_trace(
            go.Bar(
                x=top_artistas_combinado['artist'],
                y=top_artistas_combinado['minutos'],
                marker=dict(color=top_artistas_combinado['ano'], colorscale='Viridis'),
                hovertemplate='Artista: %{x}<br>Minutos: %{y:.1f}<br>Ano: %{marker.color}<extra></extra>',
                name='Top artistas'
            ),
            row=1, col=2
        )
    
    # 3. Distribuição por hora do dia (comparativo entre anos)
    for ano in anos[-2:]:  # Últimos dois anos
        df_ano = df[df['ano'] == ano]
        horas_ano = df_ano.groupby('hora')['minutos'].sum().reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=horas_ano['hora'],
                y=horas_ano['minutos'],
                mode='lines+markers',
                name=f'Ano {int(ano)}',
                hovertemplate='Hora: %{x}h<br>Minutos: %{y:.1f}<br>Ano: {int(ano)}<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 4. Proporção de músicas puladas (comparativo entre anos)
    dados_pie = []
    
    for ano in anos[-2:]:  # Últimos dois anos
        df_ano = df[df['ano'] == ano]
        puladas = df_ano['foi_pulado'].sum()
        completas = len(df_ano) - puladas
        
        dados_pie.append({
            'ano': int(ano),
            'status': 'Puladas',
            'quantidade': puladas
        })
        
        dados_pie.append({
            'ano': int(ano),
            'status': 'Completas',
            'quantidade': completas
        })
    
    df_pie = pd.DataFrame(dados_pie)
    
    fig.add_trace(
        go.Pie(
            labels=df_pie['status'] + ' (' + df_pie['ano'].astype(str) + ')',
            values=df_pie['quantidade'],
            textinfo='percent+label',
            hole=0.4,
            hovertemplate='%{label}<br>Quantidade: %{value}<br>Porcentagem: %{percent}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        title="Comparativo entre anos",
        height=800,
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    # Atualizar eixos
    fig.update_xaxes(title_text="Ano", row=1, col=1)
    fig.update_yaxes(title_text="Minutos", row=1, col=1)
    
    fig.update_xaxes(title_text="Artista", row=1, col=2)
    fig.update_yaxes(title_text="Minutos", row=1, col=2)
    
    fig.update_xaxes(title_text="Hora do dia", row=2, col=1)
    fig.update_yaxes(title_text="Minutos", row=2, col=1)
    
    return fig

# Função para criar gráficos de evolução comparativos
def criar_graficos_evolucao(df):
    """
    Cria gráficos de evolução comparativos ao longo do tempo
    
    Args:
        df: DataFrame com os dados do Spotify
        
    Returns:
        Figura do Plotly com os gráficos de evolução
    """
    # Criar figura com subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Evolução mensal de escuta",
            "Evolução de artistas favoritos",
            "Evolução da proporção online/offline",
            "Evolução de músicas puladas vs. completas"
        ),
        specs=[
            [{"type": "scatter"}, {"type": "scatter"}],
            [{"type": "scatter"}, {"type": "scatter"}]
        ],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Evolução mensal de escuta
    df_mensal = df.groupby(df['ts'].dt.to_period('M')).agg({'minutos':'sum'}).reset_index()
    df_mensal['ts'] = df_mensal['ts'].dt.to_timestamp()
    
    # Adicionar média móvel de 3 meses
    df_mensal['media_movel'] = df_mensal['minutos'].rolling(window=3, min_periods=1).mean()
    
    fig.add_trace(
        go.Scatter(
            x=df_mensal['ts'],
            y=df_mensal['minutos'],
            mode='lines+markers',
            name='Minutos por mês',
            line=dict(color='rgba(0, 180, 216, 0.8)', width=1),
            marker=dict(size=6, color='rgba(0, 180, 216, 1)'),
            hovertemplate='Data: %{x|%b %Y}<br>Minutos: %{y:.1f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df_mensal['ts'],
            y=df_mensal['media_movel'],
            mode='lines',
            name='Média móvel (3 meses)',
            line=dict(color='rgba(255, 209, 102, 1)', width=3),
            hovertemplate='Data: %{x|%b %Y}<br>Média: %{y:.1f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # 2. Evolução de artistas favoritos
    # Identificar top 3 artistas de todos os tempos
    top_artistas = df.groupby('artist')['minutos'].sum().nlargest(3).index.tolist()
    
    # Agrupar por mês e artista
    df_artistas_mes = df[df['artist'].isin(top_artistas)].groupby([df['ts'].dt.to_period('M'), 'artist']).agg({'minutos':'sum'}).reset_index()
    df_artistas_mes['ts'] = df_artistas_mes['ts'].dt.to_timestamp()
    
    # Adicionar linhas para cada artista
    for artista in top_artistas:
        df_artista = df_artistas_mes[df_artistas_mes['artist'] == artista]
        
        fig.add_trace(
            go.Scatter(
                x=df_artista['ts'],
                y=df_artista['minutos'],
                mode='lines+markers',
                name=artista,
                hovertemplate='Data: %{x|%b %Y}<br>Artista: ' + artista + '<br>Minutos: %{y:.1f}<extra></extra>'
            ),
            row=1, col=2
        )
    
    # 3. Evolução da proporção online/offline
    df_online_mes = df.groupby([df['ts'].dt.to_period('M'), 'offline']).size().reset_index()
    df_online_mes['ts'] = df_online_mes['ts'].dt.to_timestamp()
    df_online_mes.columns = ['ts', 'offline', 'contagem']
    
    # Calcular proporção
    total_por_mes = df_online_mes.groupby('ts')['contagem'].sum().reset_index()
    df_online_mes = pd.merge(df_online_mes, total_por_mes, on='ts', suffixes=('', '_total'))
    df_online_mes['proporcao'] = df_online_mes['contagem'] / df_online_mes['contagem_total']
    
    # Filtrar apenas offline=True
    df_offline = df_online_mes[df_online_mes['offline'] == True]
    
    fig.add_trace(
        go.Scatter(
            x=df_offline['ts'],
            y=df_offline['proporcao'] * 100,
            mode='lines+markers',
            name='% Offline',
            line=dict(color='rgba(255, 99, 132, 0.8)', width=2),
            marker=dict(size=6, color='rgba(255, 99, 132, 1)'),
            hovertemplate='Data: %{x|%b %Y}<br>Offline: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Adicionar linha para online (complemento)
    df_online = df_online_mes[df_online_mes['offline'] == False]
    
    fig.add_trace(
        go.Scatter(
            x=df_online['ts'],
            y=df_online['proporcao'] * 100,
            mode='lines+markers',
            name='% Online',
            line=dict(color='rgba(54, 162, 235, 0.8)', width=2),
            marker=dict(size=6, color='rgba(54, 162, 235, 1)'),
            hovertemplate='Data: %{x|%b %Y}<br>Online: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Evolução de músicas puladas vs. completas
    df_puladas_mes = df.groupby([df['ts'].dt.to_period('M'), 'foi_pulado']).size().reset_index()
    df_puladas_mes['ts'] = df_puladas_mes['ts'].dt.to_timestamp()
    df_puladas_mes.columns = ['ts', 'foi_pulado', 'contagem']
    
    # Calcular proporção
    total_por_mes = df_puladas_mes.groupby('ts')['contagem'].sum().reset_index()
    df_puladas_mes = pd.merge(df_puladas_mes, total_por_mes, on='ts', suffixes=('', '_total'))
    df_puladas_mes['proporcao'] = df_puladas_mes['contagem'] / df_puladas_mes['contagem_total']
    
    # Filtrar apenas puladas=True
    df_puladas = df_puladas_mes[df_puladas_mes['foi_pulado'] == True]
    
    fig.add_trace(
        go.Scatter(
            x=df_puladas['ts'],
            y=df_puladas['proporcao'] * 100,
            mode='lines+markers',
            name='% Puladas',
            line=dict(color='rgba(255, 159, 64, 0.8)', width=2),
            marker=dict(size=6, color='rgba(255, 159, 64, 1)'),
            hovertemplate='Data: %{x|%b %Y}<br>Puladas: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Adicionar linha para completas (complemento)
    df_completas = df_puladas_mes[df_puladas_mes['foi_pulado'] == False]
    
    fig.add_trace(
        go.Scatter(
            x=df_completas['ts'],
            y=df_completas['proporcao'] * 100,
            mode='lines+markers',
            name='% Completas',
            line=dict(color='rgba(75, 192, 192, 0.8)', width=2),
            marker=dict(size=6, color='rgba(75, 192, 192, 1)'),
            hovertemplate='Data: %{x|%b %Y}<br>Completas: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Atualizar layout
    fig.update_layout(
        title="Evolução do seu perfil de escuta ao longo do tempo",
        height=900,
        template="plotly_dark",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        )
    )
    
    # Atualizar eixos
    fig.update_xaxes(title_text="Data", row=1, col=1)
    fig.update_yaxes(title_text="Minutos", row=1, col=1)
    
    fig.update_xaxes(title_text="Data", row=1, col=2)
    fig.update_yaxes(title_text="Minutos", row=1, col=2)
    
    fig.update_xaxes(title_text="Data", row=2, col=1)
    fig.update_yaxes(title_text="Porcentagem", row=2, col=1)
    
    fig.update_xaxes(title_text="Data", row=2, col=2)
    fig.update_yaxes(title_text="Porcentagem", row=2, col=2)
    
    return fig

# Função para gerar recomendações baseadas em padrões
def gerar_recomendacoes(df):
    """
    Gera recomendações de artistas e músicas baseadas em padrões de escuta
    
    Args:
        df: DataFrame com os dados do Spotify
        
    Returns:
        Dicionário com recomendações de artistas e músicas
    """
    recomendacoes = {}
    
    # 1. Artistas que você ouve pouco, mas gosta (alta taxa de conclusão)
    # Filtrar artistas com pelo menos 5 reproduções
    contagem_por_artista = df.groupby('artist').size()
    artistas_validos = contagem_por_artista[contagem_por_artista >= 5].index
    
    # Calcular taxa de conclusão por artista
    df_artistas = df[df['artist'].isin(artistas_validos)].copy()
    taxa_conclusao = df_artistas.groupby('artist')['foi_pulado'].apply(lambda x: 1 - x.mean()).reset_index()
    taxa_conclusao.columns = ['artist', 'taxa_conclusao']
    
    # Adicionar contagem de reproduções
    taxa_conclusao['reproducoes'] = df_artistas.groupby('artist').size().values
    
    # Ordenar por taxa de conclusão (decrescente) e reproduções (crescente)
    taxa_conclusao = taxa_conclusao.sort_values(['taxa_conclusao', 'reproducoes'], ascending=[False, True])
    
    # Selecionar top 5 artistas com alta taxa de conclusão e poucas reproduções
    artistas_recomendados = taxa_conclusao.head(5)['artist'].tolist()
    recomendacoes['artistas_pouco_ouvidos'] = artistas_recomendados
    
    # 2. Músicas que você sempre ouve até o fim
    # Filtrar músicas com pelo menos 3 reproduções
    contagem_por_musica = df.groupby('track').size()
    musicas_validas = contagem_por_musica[contagem_por_musica >= 3].index
    
    # Calcular taxa de conclusão por música
    df_musicas = df[df['track'].isin(musicas_validas)].copy()
    taxa_conclusao_musica = df_musicas.groupby('track')['foi_pulado'].apply(lambda x: 1 - x.mean()).reset_index()
    taxa_conclusao_musica.columns = ['track', 'taxa_conclusao']
    
    # Adicionar artista
    df_musicas_artistas = df_musicas.groupby('track')['artist'].first().reset_index()
    taxa_conclusao_musica = pd.merge(taxa_conclusao_musica, df_musicas_artistas, on='track')
    
    # Ordenar por taxa de conclusão (decrescente)
    taxa_conclusao_musica = taxa_conclusao_musica.sort_values('taxa_conclusao', ascending=False)
    
    # Selecionar top 5 músicas com alta taxa de conclusão
    musicas_recomendadas = taxa_conclusao_musica.head(5)[['track', 'artist']].values.tolist()
    recomendacoes['musicas_favoritas'] = musicas_recomendadas
    
    # 3. Artistas similares aos seus favoritos
    # Identificar top 3 artistas
    top_artistas = df.groupby('artist')['minutos'].sum().nlargest(3).index.tolist()
    
    # Simular recomendações de artistas similares (em um sistema real, usaríamos dados de similaridade)
    artistas_similares = {
        artista: [f"Artista similar a {artista} #{i}" for i in range(1, 4)]
        for artista in top_artistas
    }
    
    recomendacoes['artistas_similares'] = artistas_similares
    
    # 4. Recomendações baseadas em horário
    # Identificar horário favorito
    horario_favorito = df.groupby('hora')['minutos'].sum().idxmax()
    
    # Identificar artistas mais ouvidos nesse horário
    artistas_horario = df[df['hora'] == horario_favorito].groupby('artist')['minutos'].sum().nlargest(3).index.tolist()
    
    recomendacoes['artistas_horario_favorito'] = {
        'horario': int(horario_favorito),
        'artistas': artistas_horario
    }
    
    # 5. Recomendações baseadas em dia da semana
    # Identificar dia da semana favorito
    dia_favorito = df.groupby('diaSemana')['minutos'].sum().idxmax()
    
    # Identificar artistas mais ouvidos nesse dia
    artistas_dia = df[df['diaSemana'] == dia_favorito].groupby('artist')['minutos'].sum().nlargest(3).index.tolist()
    
    recomendacoes['artistas_dia_favorito'] = {
        'dia': dia_favorito,
        'artistas': artistas_dia
    }
    
    return recomendacoes

# Função para visualizar recomendações
def visualizar_recomendacoes(recomendacoes):
    """
    Cria uma visualização moderna para as recomendações
    
    Args:
        recomendacoes: Dicionário com recomendações geradas
        
    Returns:
        None (exibe diretamente no Streamlit)
    """
    st.subheader("🎯 Recomendações Personalizadas")
    
    # Criar abas para diferentes tipos de recomendações
    tab1, tab2, tab3 = st.tabs(["Artistas para você", "Músicas para você", "Baseado no seu horário"])
    
    with tab1:
        st.markdown("### 🌟 Artistas que você deveria ouvir mais")
        st.markdown("Você parece gostar destes artistas, mas os ouve pouco:")
        
        # Exibir artistas pouco ouvidos em cards
        cols = st.columns(len(recomendacoes['artistas_pouco_ouvidos']))
        for i, artista in enumerate(recomendacoes['artistas_pouco_ouvidos']):
            with cols[i]:
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 10px; background-color: rgba(0, 180, 216, 0.1); border: 1px solid rgba(0, 180, 216, 0.3); text-align: center;">
                    <h4 style="margin: 0;">{artista}</h4>
                    <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #888;">Você gosta, mas ouve pouco</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("### 👥 Artistas similares aos seus favoritos")
        
        # Exibir artistas similares
        for artista, similares in recomendacoes['artistas_similares'].items():
            st.markdown(f"#### Se você gosta de {artista}, talvez goste de:")
            
            cols = st.columns(len(similares))
            for i, similar in enumerate(similares):
                with cols[i]:
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 10px; background-color: rgba(255, 159, 64, 0.1); border: 1px solid rgba(255, 159, 64, 0.3); text-align: center;">
                        <h4 style="margin: 0;">{similar}</h4>
                        <p style="margin: 5px 0 0 0; font-size: 0.8em; color: #888;">Similar a {artista}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 🎵 Músicas que você sempre ouve até o fim")
        st.markdown("Estas músicas parecem ser suas favoritas, pois você raramente as pula:")
        
        # Exibir músicas favoritas em uma tabela estilizada
        for i, (musica, artista) in enumerate(recomendacoes['musicas_favoritas']):
            st.markdown(f"""
            <div style="padding: 10px; margin-bottom: 10px; border-radius: 10px; background-color: rgba(75, 192, 192, 0.1); border: 1px solid rgba(75, 192, 192, 0.3);">
                <div style="display: flex; align-items: center;">
                    <div style="background-color: rgba(75, 192, 192, 0.2); border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                        <span style="font-weight: bold;">{i+1}</span>
                    </div>
                    <div>
                        <h4 style="margin: 0;">{musica}</h4>
                        <p style="margin: 0; font-size: 0.9em; color: #888;">{artista}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### ⏰ Baseado no seu horário favorito")
        
        # Exibir recomendações baseadas em horário
        horario = recomendacoes['artistas_horario_favorito']['horario']
        artistas_horario = recomendacoes['artistas_horario_favorito']['artistas']
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; background-color: rgba(54, 162, 235, 0.1); border: 1px solid rgba(54, 162, 235, 0.3); margin-bottom: 20px;">
            <h4 style="margin: 0;">Seu horário favorito para ouvir música: {horario}h</h4>
            <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #888;">Artistas que combinam com este horário:</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(artistas_horario))
        for i, artista in enumerate(artistas_horario):
            with cols[i]:
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 10px; background-color: rgba(54, 162, 235, 0.1); border: 1px solid rgba(54, 162, 235, 0.3); text-align: center;">
                    <h4 style="margin: 0;">{artista}</h4>
                </div>
                """, unsafe_allow_html=True)
        
        # Exibir recomendações baseadas em dia da semana
        dia = recomendacoes['artistas_dia_favorito']['dia']
        artistas_dia = recomendacoes['artistas_dia_favorito']['artistas']
        
        st.markdown(f"""
        <div style="padding: 15px; border-radius: 10px; background-color: rgba(255, 99, 132, 0.1); border: 1px solid rgba(255, 99, 132, 0.3); margin-top: 20px; margin-bottom: 20px;">
            <h4 style="margin: 0;">Seu dia favorito para ouvir música: {dia}</h4>
            <p style="margin: 5px 0 0 0; font-size: 0.9em; color: #888;">Artistas que combinam com este dia:</p>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns(len(artistas_dia))
        for i, artista in enumerate(artistas_dia):
            with cols[i]:
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 10px; background-color: rgba(255, 99, 132, 0.1); border: 1px solid rgba(255, 99, 132, 0.3); text-align: center;">
                    <h4 style="margin: 0;">{artista}</h4>
                </div>
                """, unsafe_allow_html=True)
