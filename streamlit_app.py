import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("🏀 Statistiche Basket Femminile College 2021-2025")

# URL dei file su GitHub
GITHUB_BASE_URL = "https://raw.githubusercontent.com/tuo-repo/tuo-progetto/main/"
TEAMS_CSV_URL = GITHUB_BASE_URL + "teams.csv"
ROSTERS_CSV_URL = GITHUB_BASE_URL + "rosters.csv"
STATS_FILE_URL = GITHUB_BASE_URL + "stats.xlsx"

# Caricamento dei dati direttamente da GitHub
teams_df = pd.read_csv(TEAMS_CSV_URL)
roster_df = pd.read_csv(ROSTERS_CSV_URL)
stats_df = pd.read_excel(STATS_FILE_URL)

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

# Selezione della squadra
if 'team_name' in roster_df.columns:
    team_selected = st.selectbox("Seleziona una squadra", roster_df['team_name'].unique())
    df_team = roster_df[roster_df['team_name'] == team_selected]

    # Mostra informazioni sulla squadra selezionata
    team_info = teams_df[teams_df['team'] == team_selected]
    if not team_info.empty:
        st.subheader(f"Informazioni sulla squadra: {team_selected}")
        st.write(f"**Twitter:** {team_info['twitter'].values[0]}")
        st.write(f"**NCAA ID:** {team_info['ncaa_id'].values[0]}")
        st.write(f"**Conference:** {team_info['conference'].values[0]}")
        st.write(f"**Division:** {team_info['division'].values[0]}")

    # Selezione della giocatrice
    if 'player_name' in df_team.columns:
        player_selected = st.selectbox("Seleziona una giocatrice", df_team['player_name'].unique())
        st.subheader(f"Dettagli della giocatrice: {player_selected}")
        df_player = df_team[df_team['player_name'] == player_selected]
        st.dataframe(df_player)

        # Statistiche della giocatrice
        st.subheader("Statistiche della Giocatrice")
        df_stats_player = stats_df[stats_df['player_name'] == player_selected]
        if not df_stats_player.empty:
            st.dataframe(df_stats_player)

            # Grafico a linee per punti per partita
            st.subheader("Andamento Punti per Partita")
            fig_points = px.line(df_stats_player, x='games', y='points', title=f"Andamento Punti per Partita di {player_selected}", markers=True)
            st.plotly_chart(fig_points)

            # Confronto tra media giocatrice e media squadra
            st.subheader("Profilo Abilità e Confronto con Media Squadra")
            skill_cols = ['points', 'total_rebounds', 'assists', 'steals', 'blocks']
            if all(col in df_stats_player.columns for col in skill_cols):
                skills_player = df_stats_player[skill_cols].mean()
                skills_team = stats_df[stats_df['team_name'] == team_selected][skill_cols].mean()
                radar_data = pd.DataFrame({'Skill': skill_cols, 'Player': skills_player, 'Team Avg': skills_team})
                fig_radar = px.line_polar(radar_data, r='Player', theta='Skill', line_close=True, markers=True)
                st.plotly_chart(fig_radar)

            # Nuova visualizzazione 3D dei tiri con distribuzione
            st.subheader("Distribuzione Tiri in 3D")
            if all(col in df_stats_player.columns for col in ['field_goal_attempts', 'three_point_attempts', 'free_throw_attempts']):
                fig_shot_chart = px.scatter_3d(df_stats_player, x='field_goal_attempts', y='three_point_attempts', z='free_throw_attempts', 
                                               color='points', title=f"Distribuzione dei Tiri di {player_selected}", opacity=0.7)
                st.plotly_chart(fig_shot_chart)

            # Grafico 3D delle prestazioni migliorato
            st.subheader("Prestazioni Generali della Giocatrice in 3D")
            fig_performance_3d = px.scatter_3d(df_stats_player, x='points', y='total_rebounds', z='assists', 
                                               color='games', title=f"Prestazioni 3D di {player_selected}", opacity=0.8, size_max=10)
            st.plotly_chart(fig_performance_3d)

            # Confronto storico tra stagioni
            st.subheader("Andamento Storico delle Statistiche della Giocatrice")
            if 'season' in df_stats_player.columns:
                fig_history = px.line(df_stats_player, x='season', y=['points', 'assists', 'total_rebounds'], 
                                      title=f"Andamento Storico delle Statistiche di {player_selected}", markers=True)
                st.plotly_chart(fig_history)

    else:
        st.write("Colonna player_name non trovata nel roster.")
else:
    st.write("Colonna team_name non trovata nel roster.")

# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
