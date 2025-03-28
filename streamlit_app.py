import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Titolo dell'app
st.title("**🏀 College Baskeball Analysis: just for fun!**")

# 📂 **Caricamento dei file**
roster_files = st.file_uploader("Carica i file CSV dei roster (2021-2025)", type=["csv"], accept_multiple_files=True)
stats_file = st.file_uploader("Carica il file Excel con le statistiche dei giocatori", type=["xlsx"])
teams_file = st.file_uploader("Carica il file CSV con i dati delle squadre", type=["csv"])

# 📌 **Punto 1: Analisi sui roster nel tempo**
if roster_files:
    df_rosters = []
    for file in roster_files:
        df = pd.read_csv(file)
        df["season"] = file.name.split("_")[-1].replace(".csv", "")  # Estrai la stagione dal nome file
        df_rosters.append(df)
    
    roster_df = pd.concat(df_rosters)
    roster_df.columns = roster_df.columns.str.strip().str.lower()
    
    # ✅ **Distribuzione delle altezze (box plot)**
    fig_height = px.box(roster_df, x="season", y="total_inches", title="Distribuzione delle Altezze per Stagione")
    st.plotly_chart(fig_height)
    
    # ✅ **Numero di nuove giocatrici per squadra (bar chart)**
    roster_df["new_player"] = ~roster_df.duplicated(subset=["player_id"], keep="first")
    new_players_per_team = roster_df.groupby(["season", "team"])["new_player"].sum().reset_index()
    fig_new_players = px.bar(new_players_per_team, x="season", y="new_player", color="team", 
                             title="Nuove Giocatrici per Squadra", barmode="stack")
    st.plotly_chart(fig_new_players)

    # ✅ **Turnover delle giocatrici per squadra (stacked bar chart)**
    player_counts = roster_df.groupby(["season", "team"])["player_id"].count().reset_index()
    fig_turnover = px.bar(player_counts, x="season", y="player_id", color="team", 
                          title="Turnover delle Giocatrici per Squadra", barmode="stack")
    st.plotly_chart(fig_turnover)

    # ✅ **Distribuzione geografica delle giocatrici per anno (mappa interattiva)**
    if "hometown" in roster_df.columns and "state_clean" in roster_df.columns:
        fig_geo = px.scatter_geo(roster_df, locations="state_clean", locationmode="USA-states", 
                                 hover_name="hometown", title="Distribuzione Geografica delle Giocatrici")
        st.plotly_chart(fig_geo)

#st.write("📊 **Analisi sui roster completata!**")

# 📌 **Punto 2: Analisi individuale delle giocatrici**
if stats_file:
    stats_df = pd.read_excel(stats_file)
    stats_df.columns = stats_df.columns.str.strip().str.lower()  # Convertiamo le colonne in minuscolo

    st.header("📊 Analisi delle Statistiche Giocatrici")

    # Selezione della giocatrice
    players = stats_df["player_name"].unique()
    selected_player = st.selectbox("Seleziona una giocatrice:", players)

    # 📊 **Andamento delle statistiche nel tempo**
    player_stats = stats_df[stats_df["player_name"] == selected_player]
    fig_stats = px.line(player_stats, x="games", y=["points", "assists", "total_rebounds"],
                         title=f"Andamento delle Statistiche di {selected_player}", markers=True)
    st.plotly_chart(fig_stats)

    # 🎯 **Mappa di tiro migliorata**
    if "shot_zone" in stats_df.columns and "field_goal_percentage" in stats_df.columns:
        fig_shot_map = px.scatter(stats_df[stats_df["player_name"] == selected_player],
                                  x="shot_zone", y="field_goal_percentage", size="field_goal_attempts", 
                                  color="field_goal_percentage",
                                  title=f"Mappa di tiro di {selected_player}")
        st.plotly_chart(fig_shot_map)

    # 🆚 **Confronto giocatrice vs squadra**
    if "team_name" in stats_df.columns:
        team_avg = stats_df.groupby("team_name")[["points", "assists", "total_rebounds"]].mean().reset_index()
        player_team = stats_df[stats_df["player_name"] == selected_player]["team_name"].iloc[0]
        player_avg = stats_df[stats_df["player_name"] == selected_player][["points", "assists", "total_rebounds"]].mean()
        
        team_vs_player = pd.DataFrame({
            "Statistica": ["Punti", "Assist", "Rimbalzi"],
            "Giocatrice": player_avg.values,
            "Media Squadra": team_avg[team_avg["team_name"] == player_team].iloc[:, 1:].values.flatten()
        })

        fig_team_comp = px.bar(team_vs_player, x="Statistica", y=["Giocatrice", "Media Squadra"],
                               title=f"Confronto {selected_player} vs Media Squadra", barmode="group")
        st.plotly_chart(fig_team_comp)

#st.write("📊 **Analisi individuale delle giocatrici completata!**")

# 📌 **Punto 4: Analisi avanzate con grafici 3D**
if stats_file:
    stats_df = pd.read_excel(stats_file)
    stats_df.columns = stats_df.columns.str.strip().str.lower()

    st.header("📊 Analisi Avanzate con Grafici 3D")

    # 🏟️ **Heatmap 3D delle zone di tiro**
    if "shot_x" in stats_df.columns and "shot_y" in stats_df.columns and "fg_pct" in stats_df.columns:
        fig_shot_3d = go.Figure(data=[go.Scatter3d(
            x=stats_df["shot_x"],
            y=stats_df["shot_y"],
            z=stats_df["fg_pct"],
            mode="markers",
            marker=dict(size=5, color=stats_df["fg_pct"], colorscale="Viridis", opacity=0.8)
        )])
        fig_shot_3d.update_layout(title="Heatmap 3D delle Zone di Tiro", scene=dict(
            xaxis_title="Posizione X", yaxis_title="Posizione Y", zaxis_title="Percentuale FG"
        ))
        st.plotly_chart(fig_shot_3d)

    # 🎭 **Grafico 3D con prestazioni su più metriche**
    if all(col in stats_df.columns for col in ["points", "assists", "rebounds"]):
        fig_perf_3d = go.Figure(data=[go.Scatter3d(
            x=stats_df["points"],
            y=stats_df["assists"],
            z=stats_df["rebounds"],
            mode="markers",
            marker=dict(size=6, color=stats_df["points"], colorscale="Plasma", opacity=0.8)
        )])
        fig_perf_3d.update_layout(title="Prestazioni 3D (Punti, Assist, Rimbalzi)", scene=dict(
            xaxis_title="Punti", yaxis_title="Assist", zaxis_title="Rimbalzi"
        ))
        st.plotly_chart(fig_perf_3d)

    # 🔮 **Modelli predittivi per stimare l'impatto di una giocatrice sulla squadra**
    st.subheader("🔮 Modelli Predittivi: Valutazione Impatto Giocatrice")

    if all(col in stats_df.columns for col in ["player_efficiency_rating", "win_shares", "usage_rate"]):
        fig_pred = px.scatter_3d(stats_df, x="player_efficiency_rating", y="win_shares", z="usage_rate",
                                 color="player_efficiency_rating", title="Impatto della Giocatrice sulla Squadra")
        st.plotly_chart(fig_pred)

st.write("📊 **Carica i dati per iniziare!**")

# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
