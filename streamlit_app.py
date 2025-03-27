import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import Court

# Titolo dell'app
st.title("🏀 Statistiche Basket Femminile College 2024-2025")

# Caricamento dei dati
uploaded_teams = st.file_uploader("Carica il file CSV delle squadre", type=["csv"], key="teams")
uploaded_roster = st.file_uploader("Carica il file CSV del roster 2024-2025", type=["csv"], key="roster")

if uploaded_teams and uploaded_roster:
    teams_df = pd.read_csv(uploaded_teams)
    roster_df = pd.read_csv(uploaded_roster)
    
    st.write("Anteprima delle squadre:")
    st.dataframe(teams_df.head())
    
    st.write("Anteprima del roster:")
    st.dataframe(roster_df.head())
    
    # Selezione della squadra
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
    player_selected = st.selectbox("Seleziona una giocatrice", df_team['name'].unique())
    df_player = df_team[df_team['name'] == player_selected]
    
    # Statistiche della giocatrice
    st.subheader(f"Statistiche di {player_selected}")
    st.write(df_player[['year_clean', 'position_clean', 'height_ft', 'height_in', 'total_inches', 'hometown_clean', 'state_clean']])
    
    # Visualizzazione 3D (altezza delle giocatrici rispetto al ruolo)
    fig_3d = px.scatter_3d(df_team, x='total_inches', y='primary_position', z='year_clean', color='total_inches',
                           hover_name='name', title=f"Distribuzione Altezza/Ruolo - {team_selected}")
    st.plotly_chart(fig_3d)
    
    # Visualizzazione 3D specifica per la giocatrice selezionata
    st.subheader(f"Visualizzazione 3D - {player_selected}")
    fig_player_3d = px.scatter_3d(df_player, x='total_inches', y='primary_position', z='year_clean',
                                  color='total_inches', hover_name='name',
                                  title=f"Profilo Altezza/Ruolo - {player_selected}")
    st.plotly_chart(fig_player_3d)
    
    # Grafico dei tiri su un campo da basket
    st.subheader(f"Tiri di {player_selected}")
    if 'shot_x' in df_player.columns and 'shot_y' in df_player.columns:
        fig, ax = plt.subplots(figsize=(6, 5))
        court = Court()
        court.draw(ax=ax)
        ax.scatter(df_player['shot_x'], df_player['shot_y'], c='red', label='Tiri')
        ax.legend()
        st.pyplot(fig)
    else:
        st.write("Dati sui tiri non disponibili.")
    
    # Trend di crescita della giocatrice
    st.subheader(f"Evoluzione della carriera di {player_selected}")
    if 'season' in df_player.columns and 'total_inches' in df_player.columns:
        fig_growth = px.line(df_player, x='season', y='total_inches', title=f"Evoluzione Altezza - {player_selected}", markers=True)
        st.plotly_chart(fig_growth)
    else:
        st.write("Dati di crescita non disponibili.")
    
    # Grafico radar delle abilità
    st.subheader(f"Profilo Abilità - {player_selected}")
    skill_cols = ['points', 'rebounds', 'assists', 'steals', 'blocks']
    if all(col in df_player.columns for col in skill_cols):
        skills = df_player[skill_cols].mean()
        fig_radar = px.line_polar(r=skills.values, theta=skill_cols, line_close=True, title=f"Radar Abilità - {player_selected}")
        st.plotly_chart(fig_radar)
    else:
        st.write("Dati sulle abilità non disponibili.")
    
else:
    st.write("Carica entrambi i file CSV per iniziare!")

# Footer
st.write("App creata con ❤️ usando Streamlit, Matplotlib e Plotly")
