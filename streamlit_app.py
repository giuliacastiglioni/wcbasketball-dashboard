import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("🏀 Analisi Roster nel Tempo")

# Caricamento dei file CSV
df_rosters = []

uploaded_files = st.file_uploader("Carica i file CSV dei roster (2021-2025)", type=["csv"], accept_multiple_files=True)
if uploaded_files:
    for file in uploaded_files:
        df = pd.read_csv(file)
        df["season"] = file.name.split("_")[-1].replace(".csv", "")  # Estrai la stagione dal nome file
        df_rosters.append(df)
    
    roster_df = pd.concat(df_rosters)
    
    # Pulizia e filtraggio dei dati
    roster_df.columns = roster_df.columns.str.strip().str.lower()
    valid_seasons = ["2021-22", "2022-23", "2023-24", "2024-25"]
    roster_df = roster_df[roster_df["season"].isin(valid_seasons)]
    
    # 📊 Distribuzione delle altezze per stagione (box plot)
    fig_height = px.box(roster_df, x="season", y="total_inches", title="Distribuzione delle Altezze per Stagione")
    st.plotly_chart(fig_height)
    
    # 📈 Numero di nuove giocatrici per squadra ogni anno
    roster_df["new_player"] = ~roster_df.duplicated(subset=["player_id"], keep="first")
    new_players_per_team = roster_df.groupby(["season", "team"])["new_player"].sum().reset_index()
    fig_new_players = px.bar(new_players_per_team, x="season", y="new_player", color="team", 
                             title="Nuove Giocatrici per Squadra", barmode="stack")
    st.plotly_chart(fig_new_players)
    
    # 🔄 Turnover delle giocatrici per squadra
    player_counts = roster_df.groupby(["season", "team"])["player_id"].count().reset_index()
    fig_turnover = px.bar(player_counts, x="season", y="player_id", color="team", 
                          title="Turnover delle Giocatrici per Squadra", barmode="stack")
    st.plotly_chart(fig_turnover)
    
    # 🌍 Distribuzione geografica delle giocatrici per anno
    if "hometown" in roster_df.columns and "state_clean" in roster_df.columns:
        fig_geo = px.scatter_geo(roster_df, locations="state_clean", locationmode="USA-states", 
                                 hover_name="hometown", title="Distribuzione Geografica delle Giocatrici")
        st.plotly_chart(fig_geo)
    
else:
    st.write("Carica i file dei roster per iniziare l'analisi!")
# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
