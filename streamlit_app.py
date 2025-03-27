import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("🏀 Statistiche Basket Femminile College 2021-2025")

# Caricamento dei dati
uploaded_teams = st.file_uploader("Carica il file CSV delle squadre", type=["csv"], key="teams")
uploaded_rosters = st.file_uploader("Carica i file CSV dei roster (2021-2025)", type=["csv"], accept_multiple_files=True, key="rosters")

if uploaded_teams and uploaded_rosters and uploaded_stats:
    teams_df = pd.read_csv(uploaded_teams)
    roster_dfs = [pd.read_csv(f) for f in uploaded_rosters]
    roster_df = pd.concat(roster_dfs)
    stats_df = pd.read_csv(uploaded_stats)
    
    # Normalizzazione nomi colonne
    teams_df.columns = teams_df.columns.str.strip().str.upper()
    roster_df.columns = roster_df.columns.str.strip().str.upper()
    stats_df.columns = stats_df.columns.str.strip().str.upper()
    
    st.write("Anteprima delle squadre:")
    st.dataframe(teams_df.head())
    
    st.write("Anteprima del roster:")
    st.dataframe(roster_df.head())
    
    st.write("Anteprima delle statistiche:")
    st.dataframe(stats_df.head())
    
    # Selezione della squadra
    if 'TEAM_NAME' in roster_df.columns:
        team_selected = st.selectbox("Seleziona una squadra", roster_df['TEAM_NAME'].unique())
        df_team = roster_df[roster_df['TEAM_NAME'] == team_selected]
    
        # Mostra informazioni sulla squadra selezionata
        team_info = teams_df[teams_df['TEAM'] == team_selected]
        if not team_info.empty:
            st.subheader(f"Informazioni sulla squadra: {team_selected}")
            st.write(f"**Twitter:** {team_info['TWITTER'].values[0]}")
            st.write(f"**NCAA ID:** {team_info['NCAA_ID'].values[0]}")
            st.write(f"**Conference:** {team_info['CONFERENCE'].values[0]}")
            st.write(f"**Division:** {team_info['DIVISION'].values[0]}")
    
        # Selezione della giocatrice
        if 'PLAYER_NAME' in df_team.columns:
            player_selected = st.selectbox("Seleziona una giocatrice", df_team['PLAYER_NAME'].unique())
            df_player = stats_df[stats_df['PLAYER_NAME'] == player_selected]
            
            # Statistiche complete della giocatrice
            st.subheader(f"Statistiche di {player_selected}")
            st.dataframe(df_player)
            
            # Grafico radar delle abilità
            st.subheader(f"Profilo Abilità - {player_selected}")
            skill_cols = ['POINTS', 'TOTAL_REBOUNDS', 'ASSISTS', 'STEALS', 'BLOCKS']
            if all(col in df_player.columns for col in skill_cols):
                skills = df_player[skill_cols].mean()
                fig_radar = px.line_polar(r=skills.values, theta=skill_cols, line_close=True, title=f"Radar Abilità - {player_selected}")
                st.plotly_chart(fig_radar)
            
            # Grafico 3D a bolle
            st.subheader("Prestazioni della giocatrice in 3D")
            if all(col in df_player.columns for col in ['MINUTES_PLAYED', 'POINTS', 'TOTAL_REBOUNDS']):
                fig_3d = px.scatter_3d(df_player, x='MINUTES_PLAYED', y='POINTS', z='TOTAL_REBOUNDS', color='GAMES',
                                       size='POINTS', title=f"Performance 3D di {player_selected}")
                st.plotly_chart(fig_3d)
            
            # Istogrammi 3D
            st.subheader("Distribuzione Statistiche in 3D")
            if all(col in df_player.columns for col in ['GAMES', 'FIELD_GOALS_MADE', 'THREE_POINTS_MADE']):
                fig_hist3d = go.Figure(data=[go.Bar3d(
                    x=df_player['GAMES'],
                    y=['Field Goals', '3PT Made'],
                    z=[df_player['FIELD_GOALS_MADE'].sum(), df_player['THREE_POINTS_MADE'].sum()],
                    opacity=0.8
                )])
                fig_hist3d.update_layout(title=f"Distribuzione dei Tiri di {player_selected}")
                st.plotly_chart(fig_hist3d)
        else:
            st.write("Colonna PLAYER_NAME non trovata nel roster.")
    else:
        st.write("Colonna TEAM_NAME non trovata nel roster.")
else:
    st.write("Carica tutti i file CSV per iniziare!")

# Footer
st.write("App creata con ❤️ usando Streamlit e Plotly")
