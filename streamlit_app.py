import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("🏀 Statistiche Basket Femminile College 2021-2025")

# Caricamento dei dati
uploaded_teams = st.file_uploader("Carica il file CSV delle squadre", type=["csv"], key="teams")
uploaded_rosters = st.file_uploader("Carica i file CSV dei roster (2021-2025)", type=["csv"], accept_multiple_files=True, key="rosters")

if uploaded_teams and uploaded_rosters:
    teams_df = pd.read_csv(uploaded_teams)
    roster_dfs = [pd.read_csv(f) for f in uploaded_rosters]
    roster_df = pd.concat(roster_dfs)
    
    # Normalizzazione nomi colonne
    teams_df.columns = teams_df.columns.str.strip().str.lower()
    roster_df.columns = roster_df.columns.str.strip().str.lower()
    
    st.write("Anteprima delle squadre:")
    st.dataframe(teams_df.head())
    
    st.write("Anteprima del roster:")
    st.dataframe(roster_df.head())
    
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

            # Grafico di distribuzione altezza
            st.subheader("Distribuzione Altezza per Stagione")
            if 'season' in roster_df.columns and 'total_inches' in roster_df.columns:
                fig_height = px.box(roster_df, x='season', y='total_inches', title="Distribuzione Altezza per Stagione")
                st.plotly_chart(fig_height)

            # Grafico 3D altezza per stagione
            st.subheader("Evoluzione Altezza nel Tempo")
            if 'season' in roster_df.columns and 'height_ft' in roster_df.columns and 'height_in' in roster_df.columns:
                fig_3d_height = px.scatter_3d(roster_df, x='season', y='height_ft', z='height_in', color='team', title="Evoluzione Altezza 3D")
                st.plotly_chart(fig_3d_height)

            # Grafico a dispersione altezza vs posizione
            st.subheader("Relazione tra Altezza e Posizione")
            if 'position_clean' in roster_df.columns and 'total_inches' in roster_df.columns:
                fig_scatter = px.scatter(roster_df, x='position_clean', y='total_inches', color='season', title="Altezza vs Posizione")
                st.plotly_chart(fig_scatter)

            # Analisi della distribuzione delle posizioni nel tempo
            st.subheader("Distribuzione delle Posizioni nel Tempo")
            if 'season' in roster_df.columns and 'position_clean' in roster_df.columns:
                fig_bar_positions = px.histogram(roster_df, x='season', color='position_clean', barmode='group', title="Distribuzione Posizioni nel Tempo")
                st.plotly_chart(fig_bar_positions)
        else:
            st.write("Colonna name non trovata nel roster.")
    else:
        st.write("Colonna team non trovata nel roster.")
else:
    st.write("Carica tutti i file CSV per iniziare!")

# Footer
st.write("App creata con ❤️ usando Streamlit e Plotly")
