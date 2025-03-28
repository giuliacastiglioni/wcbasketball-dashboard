import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("🏀 Statistiche Basket Femminile College 2021-2025")

# Caricamento dei file CSV
uploaded_teams = st.file_uploader("Carica il file CSV delle squadre", type=["csv"], key="teams")
uploaded_rosters = st.file_uploader("Carica i file CSV dei roster", type=["csv"], accept_multiple_files=True, key="rosters")
uploaded_stats = st.file_uploader("Carica il file Excel delle statistiche", type=["xlsx"], key="stats")

if uploaded_teams and uploaded_rosters and uploaded_stats:
    teams_df = pd.read_csv(uploaded_teams)
    roster_dfs = [pd.read_csv(f) for f in uploaded_rosters]
    roster_df = pd.concat(roster_dfs)
    stats_df = pd.read_excel(uploaded_stats)
    
    # Normalizzazione nomi colonne
    teams_df.columns = teams_df.columns.str.strip().str.lower()
    roster_df.columns = roster_df.columns.str.strip().str.lower()
    stats_df.columns = stats_df.columns.str.strip().str.lower()

    st.write("Anteprima delle squadre:")
    st.dataframe(teams_df.head())

    st.write("Anteprima del roster:")
    st.dataframe(roster_df.head())

    st.write("Anteprima delle statistiche:")
    st.dataframe(stats_df.head())

    # Analisi 1️⃣: Distribuzione delle altezze delle giocatrici per stagione
    #if 'season' in roster_df.columns and 'height_clean' in roster_df.columns:
    #    fig_height = px.box(roster_df, x='season', y='height_clean', color='season',
    #                         title="Distribuzione delle Altezze per Stagione")
    #    st.plotly_chart(fig_height)
    
    # Analisi 2️⃣: Numero di nuove giocatrici per squadra ogni anno
    if 'team' in roster_df.columns and 'player_id' in roster_df.columns:
        roster_df['new_player'] = ~roster_df.duplicated(subset=['player_id'], keep='first')
        new_players_by_team = roster_df.groupby(['season', 'team'])['new_player'].sum().reset_index()
        fig_new_players = px.line(new_players_by_team, x='season', y='new_player', color='team',
                                   title="Numero di Nuove Giocatrici per Squadra")
        st.plotly_chart(fig_new_players)

    # Analisi 3️⃣: Turnover delle giocatrici per squadra
    if 'team' in roster_df.columns and 'player_id' in roster_df.columns:
        turnover_data = roster_df.groupby(['season', 'team'])['player_id'].nunique().reset_index()
        fig_turnover = px.bar(turnover_data, x='season', y='player_id', color='team',
                               title="Turnover delle Giocatrici per Squadra")
        st.plotly_chart(fig_turnover)
    
    # Analisi 4️⃣: Distribuzione geografica delle giocatrici per anno
    if 'season' in roster_df.columns and 'state_clean' in roster_df.columns:
        fig_geo = px.choropleth(roster_df, locations='state_clean', locationmode="USA-states",
                                color='season', title="Distribuzione Geografica delle Giocatrici")
        st.plotly_chart(fig_geo)

else:
    st.write("Carica tutti i file richiesti per iniziare!")

# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
