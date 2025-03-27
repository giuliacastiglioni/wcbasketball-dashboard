import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("🏀 Statistiche Basket Femminile College 2021-2025")

# Caricamento dei dati
uploaded_teams = st.file_uploader("Carica il file CSV delle squadre", type=["csv"], key="teams")
uploaded_rosters = st.file_uploader("Carica i file CSV dei roster (2021-2025)", type=["csv"], accept_multiple_files=True, key="rosters")
uploaded_stats = st.file_uploader("Carica il file delle statistiche 2023-2024", type=["csv", "xlsx"], key="stats")

if uploaded_teams and uploaded_rosters and uploaded_stats:
    teams_df = pd.read_csv(uploaded_teams)
    roster_dfs = [pd.read_csv(f) for f in uploaded_rosters]
    roster_df = pd.concat(roster_dfs)
    
    if uploaded_stats.name.endswith(".csv"):
        stats_df = pd.read_csv(uploaded_stats)
    else:
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
    
    # Selezione della squadra
    if 'team' in roster_df.columns:
        team_selected = st.selectbox("Seleziona una squadra", roster_df['team'].unique())
        df_team = roster_df[roster_df['team'] == team_selected]
    
        # Mostra informazioni sulla squadra selezionata
        team_info = teams_df[teams_df['team'] == team_selected]
        if not team_info.empty:
            st.subheader(f"Informazioni sulla squadra: {team_selected}")
            st.write(f"**Twitter:** {team_info['twitter'].values[0]}")
            st.write(f"**NCAA ID:** {team_info['ncaa_id'].values[0]}")
            st.write(f"**Conference:** {team_info['conference'].values[0]}")
            st.write(f"**Division:** {team_info['division'].values[0]}")
    
        # Selezione della giocatrice
        if 'name' in df_team.columns:
            player_selected = st.selectbox("Seleziona una giocatrice", df_team['name'].unique())
            st.subheader(f"Dettagli della giocatrice: {player_selected}")
            df_player = df_team[df_team['name'] == player_selected]
            st.dataframe(df_player)

            # Statistiche della giocatrice
            st.subheader("Statistiche della Giocatrice")
            df_stats_player = stats_df[stats_df['player_name'] == player_selected]
            if not df_stats_player.empty:
                st.dataframe(df_stats_player)

                # Grafico a barre per i punti per partita
                st.subheader("Punti per Partita")
                fig_points = px.line(df_stats_player, x='games', y='points', title=f"Andamento Punti per Partita di {player_selected}", markers=True)
                st.plotly_chart(fig_points)

                # Grafico radar confronto con media della squadra
                st.subheader("Profilo Abilità e Confronto con Media Squadra")
                skill_cols = ['points', 'total_rebounds', 'assists', 'steals', 'blocks']
                if all(col in df_stats_player.columns for col in skill_cols):
                    skills_player = df_stats_player[skill_cols].mean()
                    skills_team = stats_df[stats_df['team_name'] == team_selected][skill_cols].mean()
                    radar_data = pd.DataFrame({'Skill': skill_cols, 'Player': skills_player.values, 'Team Avg': skills_team.values})
                    fig_radar = px.line_polar(radar_data, r=['Player', 'Team Avg'], theta='Skill', line_close=True, markers=True)
                    st.plotly_chart(fig_radar)

                # Campo 3D per distribuzione tiri
                st.subheader("Mappa di Tiro in 3D")
                if all(col in df_stats_player.columns for col in ['field_goal_attempts', 'three_point_attempts', 'free_throw_attempts']):
                    fig_shot_chart = px.scatter_3d(df_stats_player, x='field_goal_attempts', y='three_point_attempts', z='free_throw_attempts', 
                                                   color='points', title=f"Distribuzione dei Tiri di {player_selected}", opacity=0.8, size_max=10)
                    st.plotly_chart(fig_shot_chart)

                # Confronto storico tra stagioni della giocatrice
                st.subheader("Andamento Storico delle Statistiche della Giocatrice")
                if 'season' in df_stats_player.columns:
                    fig_history = px.line(df_stats_player, x='season', y=['points', 'assists', 'total_rebounds'], 
                                          title=f"Andamento Storico delle Statistiche di {player_selected}", markers=True)
                    st.plotly_chart(fig_history)
        
        else:
            st.write("Colonna name non trovata nel roster.")
    else:
        st.write("Colonna team non trovata nel roster.")
else:
    st.write("Carica tutti i file CSV per iniziare!")

# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
