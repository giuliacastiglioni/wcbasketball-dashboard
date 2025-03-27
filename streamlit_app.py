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

            # Evoluzione delle presenze in campo per stagione
            st.subheader("Evoluzione Presenze in Campo")
            if 'season' in df_player.columns and 'year_clean' in df_player.columns:
                fig_games = px.line(df_player, x='season', y='year_clean', title=f"Presenze in Campo di {player_selected} nel Tempo")
                st.plotly_chart(fig_games)

            # Distribuzione delle posizioni nel tempo
            st.subheader("Distribuzione delle Posizioni nel Tempo")
            if 'season' in df_player.columns and 'position_clean' in df_player.columns:
                fig_bar_positions = px.histogram(df_player, x='season', color='position_clean', barmode='group', title=f"Posizioni giocate da {player_selected}")
                st.plotly_chart(fig_bar_positions)

            # Grafico della provenienza geografica
            st.subheader("Mappa della Provenienza")
            if 'hometown_clean' in df_player.columns and 'state_clean' in df_player.columns:
                fig_map = px.scatter_geo(df_player, locations='state_clean', locationmode='USA-states', hover_name='hometown_clean', title=f"Provenienza di {player_selected}")
                st.plotly_chart(fig_map)

            # Statistiche della giocatrice
            st.subheader("Statistiche della Giocatrice")
            df_stats_player = stats_df[stats_df['player_name'] == player_selected]
            if not df_stats_player.empty:
                st.dataframe(df_stats_player)

                # Grafico a barre per i punti per partita
                st.subheader("Punti per Partita")
                fig_points = px.bar(df_stats_player, x='games', y='points', title=f"Punti per Partita di {player_selected}")
                st.plotly_chart(fig_points)

                # Grafico 3D del rendimento in campo
                st.subheader("Rendimento in Campo 3D")
                fig_3d_performance = px.scatter_3d(df_stats_player, x='minutes_played', y='field_goals_made', z='three_points_made', color='games', size='points', title=f"Performance 3D di {player_selected}")
                st.plotly_chart(fig_3d_performance)

        else:
            st.write("Colonna name non trovata nel roster.")
    else:
        st.write("Colonna team non trovata nel roster.")
else:
    st.write("Carica tutti i file CSV per iniziare!")

# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
