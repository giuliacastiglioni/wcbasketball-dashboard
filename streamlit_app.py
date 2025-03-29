import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Titolo dell'app
st.title("**🏀 College Baskeball Analysis: just for fun!**")

# 📂 **Caricamento dei file**
roster_files = st.file_uploader("Carica i file CSV dei roster (2021-2025)", type=["csv"], accept_multiple_files=True)
stats_file = st.file_uploader("Carica il file Excel con le statistiche dei giocatori", type=["xlsx"])
teams_file = st.file_uploader("Carica il file CSV con i dati delle squadre", type=["csv"])

st.write("📊 **Carica i dati per iniziare!**")

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
    # Carichiamo i dati dal file
    stats_df = pd.read_excel(stats_file, sheet_name="Sheet1")
    stats_df.columns = stats_df.columns.str.strip().str.upper()  # Convertiamo le colonne in maiuscolo per uniformità

    st.header("📊 Analisi delle Statistiche Giocatrici")

    # 🔍 **Selezione della giocatrice**
    players = stats_df["PLAYER_NAME"].unique()
    selected_player = st.selectbox("Seleziona una giocatrice:", players)

    # 📊 **Andamento delle statistiche nel tempo**
    player_stats = stats_df[stats_df["PLAYER_NAME"] == selected_player]
    if not player_stats.empty:
        fig_stats = px.line(player_stats, x="GAMES", y=["POINTS", "ASSISTS", "TOTAL_REBOUNDS"],
                            title=f"Andamento delle Statistiche di {selected_player}", markers=True)
        st.plotly_chart(fig_stats)

    # 🎯 **Mappa di tiro migliorata**
    if "FIELD_GOAL_PERCENTAGE" in stats_df.columns:
        fig_shot_map = px.scatter(player_stats, x="FIELD_GOAL_ATTEMPTS", y="FIELD_GOAL_PERCENTAGE",
                                  size="FIELD_GOALS_MADE", color="FIELD_GOAL_PERCENTAGE",
                                  title=f"Mappa di tiro di {selected_player}")
        st.plotly_chart(fig_shot_map)

    # 🆚 **Confronto giocatrice vs squadra**
    if "TEAM_NAME" in stats_df.columns:
        team_avg = stats_df.groupby("TEAM_NAME")[["POINTS", "ASSISTS", "TOTAL_REBOUNDS"]].mean().reset_index()
        player_team = player_stats["TEAM_NAME"].iloc[0]
        player_avg = player_stats[["POINTS", "ASSISTS", "TOTAL_REBOUNDS"]].mean()

        team_vs_player = pd.DataFrame({
            "Statistica": ["Punti", "Assist", "Rimbalzi"],
            "Giocatrice": player_avg.values,
            "Media Squadra": team_avg[team_avg["TEAM_NAME"] == player_team].iloc[:, 1:].values.flatten()
        })

        fig_team_comp = px.bar(team_vs_player, x="Statistica", y=["Giocatrice", "Media Squadra"],
                               title=f"Confronto {selected_player} vs Media Squadra", barmode="group")
        st.plotly_chart(fig_team_comp)

    # 🔥 **Hot Streak & Cold Streak**
    st.header("🔥 Hot & Cold Streak")
    if "POINTS" in stats_df.columns and "GAMES" in stats_df.columns:
        player_stats = player_stats.sort_values("GAMES")
        player_stats["HOT_STREAK"] = player_stats["POINTS"].rolling(3).mean() > 20
        player_stats["COLD_STREAK"] = player_stats["POINTS"].rolling(3).mean() < 5

        fig_streak = px.line(player_stats, x="GAMES", y="POINTS", markers=True,
                             title=f"Hot & Cold Streak di {selected_player}",
                             color=player_stats["HOT_STREAK"].map({True: "Hot", False: "Cold"}))
        st.plotly_chart(fig_streak)

    # ⏳ **Consistenza delle Prestazioni**
    st.header("⏳ Consistenza delle Prestazioni")
    if all(col in stats_df.columns for col in ["POINTS", "TOTAL_REBOUNDS", "ASSISTS"]):
        stats_std = stats_df.groupby("PLAYER_NAME")[["POINTS", "TOTAL_REBOUNDS", "ASSISTS"]].std().reset_index()
        stats_std = stats_std.melt(id_vars="PLAYER_NAME", var_name="Statistica", value_name="Deviazione Standard")

        fig_consistency = px.box(stats_std, x="Statistica", y="Deviazione Standard",
                                 title="Consistenza delle Prestazioni")
        st.plotly_chart(fig_consistency)

    # 🏀 **Giocatrici con Stile di Gioco Simile**
    st.header("🏀 Giocatrici con Stile di Gioco Simile")
    if all(col in stats_df.columns for col in ["POINTS", "TOTAL_REBOUNDS", "ASSISTS", "MINUTES_PLAYED"]):
        cluster_data = stats_df.groupby("PLAYER_NAME")[["POINTS", "TOTAL_REBOUNDS", "ASSISTS", "MINUTES_PLAYED"]].mean()
        scaler = StandardScaler()
        cluster_scaled = scaler.fit_transform(cluster_data)
        
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_data["CLUSTER"] = kmeans.fit_predict(cluster_scaled)

        fig_cluster = px.scatter(cluster_data, x="POINTS", y="ASSISTS", color=cluster_data["CLUSTER"].astype(str),
                                 hover_name=cluster_data.index, title="Clustering delle Giocatrici")
        st.plotly_chart(fig_cluster)
    
     # 📊 **Efficienza Avanzata**
    st.subheader("📈 Efficienza Avanzata")
    if all(col in stats_df.columns for col in ["POINTS", "FIELD_GOAL_ATTEMPTS", "FREE_THROW_ATTEMPTS", "TURNOVERS", "MINUTES_PLAYED"]):
        player_stats = stats_df[stats_df["PLAYER_NAME"] == selected_player].copy()

        # Calcolo True Shooting Percentage (TS%)
        player_stats["TS_PCT"] = player_stats["POINTS"] / (2 * (player_stats["FIELD_GOAL_ATTEMPTS"] + 0.44 * player_stats["FREE_THROW_ATTEMPTS"]))
        
        # Calcolo Usage Rate (USG%)
        player_stats["USG_PCT"] = 100 * (player_stats["FIELD_GOAL_ATTEMPTS"] + 0.44 * player_stats["FREE_THROW_ATTEMPTS"] + player_stats["TURNOVERS"]) / player_stats["MINUTES_PLAYED"]
        
        # Visualizzazione grafica
        fig_efficiency = px.line(player_stats, x="GAMES", y=["TS_PCT", "USG_PCT"], markers=True,
                                 title=f"Efficienza Avanzata di {selected_player}", labels={"value": "Percentuale", "variable": "Statistica"})
        st.plotly_chart(fig_efficiency)

    # 🔥 **Momentum e Clutch Performance**
    st.subheader("🔥 Momentum e Clutch Performance")
    if all(col in stats_df.columns for col in ["GAMES", "POINTS", "MINUTES_PLAYED"]):
        player_stats["MOMENTUM"] = player_stats["POINTS"].rolling(3, min_periods=1).mean()

        # Definiamo clutch performance come partite con punti superiori a 20 e giocate con più di 35 minuti
        clutch_games = player_stats[player_stats["MINUTES_PLAYED"] > 35]

        fig_momentum = px.line(player_stats, x="GAMES", y="MOMENTUM", markers=True,
                               title=f"Momentum e Clutch Performance di {selected_player}")
        st.plotly_chart(fig_momentum)

        if not clutch_games.empty:
            st.write(f"🎯 {selected_player} ha giocato {len(clutch_games)} partite clutch con più di 20 punti e oltre 35 minuti in campo.")

    # 🚀 **MVP Index e Valutazione Impatto**
    st.subheader("🚀 MVP Index e Valutazione Impatto")
    if all(col in stats_df.columns for col in ["POINTS", "TOTAL_REBOUNDS", "ASSISTS", "STEALS", "BLOCKS", "TURNOVERS", "MINUTES_PLAYED"]):
        stats_df["IMPACT_SCORE"] = (stats_df["POINTS"] + stats_df["TOTAL_REBOUNDS"] + stats_df["ASSISTS"] + stats_df["STEALS"] + stats_df["BLOCKS"]) - stats_df["TURNOVERS"]
        player_impact = stats_df.groupby("PLAYER_NAME")["IMPACT_SCORE"].mean().reset_index()
        top_impact = player_impact.sort_values("IMPACT_SCORE", ascending=False).head(10)

        fig_impact = px.bar(top_impact, x="PLAYER_NAME", y="IMPACT_SCORE", title="Top 10 Giocatrici per Impatto", color="IMPACT_SCORE")
        st.plotly_chart(fig_impact)

#st.write("📊 **Analisi individuale delle giocatrici completata!**")

if stats_file:
    stats_df = pd.read_excel(stats_file)
    stats_df.columns = stats_df.columns.str.strip().str.upper()  # 👈 Convertiamo in MAIUSCOLO

    st.header("📊 Analisi delle Statistiche Giocatrici")

    # Selezione delle due giocatrici
    players = stats_df["PLAYER_NAME"].unique()
    selected_player1 = st.selectbox("Seleziona la prima giocatrice:", players, index=0)
    selected_player2 = st.selectbox("Seleziona la seconda giocatrice:", players, index=1)

    # 📊 **Confronto Statistiche Base**
    st.subheader("📊 Confronto tra Giocatrici")

    if all(col in stats_df.columns for col in ["PLAYER_NAME", "POINTS", "TOTAL_REBOUNDS", "ASSISTS", "STEALS", "BLOCKS"]):
        player1_stats = stats_df[stats_df["PLAYER_NAME"] == selected_player1].mean(numeric_only=True)
        player2_stats = stats_df[stats_df["PLAYER_NAME"] == selected_player2].mean(numeric_only=True)

        compare_df = pd.DataFrame({
            "Statistiche": ["Punti", "Rimbalzi", "Assist", "Rubate", "Blocchi"],
            selected_player1: [player1_stats["POINTS"], player1_stats["TOTAL_REBOUNDS"], player1_stats["ASSISTS"], player1_stats["STEALS"], player1_stats["BLOCKS"]],
            selected_player2: [player2_stats["POINTS"], player2_stats["TOTAL_REBOUNDS"], player2_stats["ASSISTS"], player2_stats["STEALS"], player2_stats["BLOCKS"]],
        })

        fig_compare = px.bar(compare_df, x="Statistiche", y=[selected_player1, selected_player2],
                             title=f"Confronto {selected_player1} vs {selected_player2}",
                             barmode="group")
        st.plotly_chart(fig_compare)

    # 📈 **Andamento delle Prestazioni nel Tempo**
    st.subheader("📈 Andamento delle Prestazioni")
    if all(col in stats_df.columns for col in ["GAMES", "POINTS", "TOTAL_REBOUNDS", "ASSISTS"]):
        fig_trend = px.line(stats_df[stats_df["PLAYER_NAME"].isin([selected_player1, selected_player2])],
                            x="GAMES", y="POINTS", color="PLAYER_NAME",
                            title=f"Andamento dei Punti nel Tempo: {selected_player1} vs {selected_player2}",
                            markers=True)
        st.plotly_chart(fig_trend)

    # 🔄 **Radar Chart per confronto multi-statistica**
    st.subheader("🔄 Confronto Multi-Statistica")
    if all(col in stats_df.columns for col in ["POINTS", "TOTAL_REBOUNDS", "ASSISTS", "STEALS", "BLOCKS"]):
        radar_df = pd.DataFrame({
            "Statistiche": ["Punti", "Rimbalzi", "Assist", "Rubate", "Blocchi"],
            selected_player1: [player1_stats["POINTS"], player1_stats["TOTAL_REBOUNDS"], player1_stats["ASSISTS"], player1_stats["STEALS"], player1_stats["BLOCKS"]],
            selected_player2: [player2_stats["POINTS"], player2_stats["TOTAL_REBOUNDS"], player2_stats["ASSISTS"], player2_stats["STEALS"], player2_stats["BLOCKS"]],
        })

        fig_radar = px.line_polar(radar_df.melt(id_vars="Statistiche"), r="value", theta="Statistiche", 
                                  color="variable", line_close=True,
                                  title=f"Radar Chart: {selected_player1} vs {selected_player2}")
        st.plotly_chart(fig_radar)


stats_df = pd.read_excel(stats_file)

# Normalizziamo i nomi delle squadre per evitare errori di formattazione
stats_df["TEAM_NAME"] = stats_df["TEAM_NAME"].str.strip().str.upper()

# Lista delle squadre disponibili
team_list = sorted(stats_df["TEAM_NAME"].unique())

# Interfaccia Streamlit
st.title("📊 Analisi Statistiche - per Squadra")

# Selezione della squadra
selected_team = st.selectbox("🏀 Seleziona una squadra:", team_list)

# Filtriamo i dati della squadra selezionata
team_data = stats_df[stats_df["TEAM_NAME"] == selected_team]

if team_data.empty:
    st.warning("⚠️ Nessun dato disponibile per questa squadra.")
else:
    st.subheader(f"📌 Statistiche per {selected_team}")

    # Mostriamo la tabella dei dati
    st.dataframe(team_data)

    # Selezione della metrica da visualizzare
    stat_columns = [col for col in stats_df.columns if col not in ["TEAM_NAME", "PLAYER_NAME"]]
    selected_stat = st.selectbox("📈 Seleziona una statistica:", stat_columns)

    # 📊 Grafico a barre per la statistica selezionata
    fig_bar = px.bar(
        team_data,
        x="PLAYER_NAME",
        y=selected_stat,
        title=f"{selected_stat} per giocatrice",
        color="PLAYER_NAME"
    )
    st.plotly_chart(fig_bar)

    # 📊 Distribuzione della statistica scelta
    fig_hist = px.histogram(
        team_data,
        x=selected_stat,
        nbins=10,
        title=f"Distribuzione di {selected_stat}",
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig_hist)

    # 📌 Comparazione tra due statistiche
    selected_stat_2 = st.selectbox("📊 Seleziona una seconda statistica:", stat_columns)
    fig_scatter = px.scatter(
        team_data,
        x=selected_stat,
        y=selected_stat_2,
        text="PLAYER_NAME",
        title=f"Confronto {selected_stat} vs {selected_stat_2}",
        color="PLAYER_NAME",
        size_max=15
    )
    fig_scatter.update_traces(textposition="top center")
    st.plotly_chart(fig_scatter)

    # 📌 Radar Chart per confronto multiplo
    num_players = len(team_data)
    if num_players > 1:
        selected_players = st.multiselect("👤 Seleziona giocatrici per radar chart:", team_data["PLAYER_NAME"].unique())

        if selected_players:
            radar_data = team_data[team_data["PLAYER_NAME"].isin(selected_players)]
            fig_radar = go.Figure()
            for _, row in radar_data.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=row[stat_columns].values,
                    theta=stat_columns,
                    fill="toself",
                    name=row["PLAYER_NAME"]
                ))
            fig_radar.update_layout(title="📡 Radar Chart Statistiche")
            st.plotly_chart(fig_radar)

# Verifica che siano stati caricati i file
if not roster_files or not stats_file or not teams_file:
    st.warning("⚠️ Carica tutti i file necessari per procedere.")
else:
    # 📂 Carica i file CSV e Excel
    # Carica i file roster per ogni anno (2021-2025)
    rosters_df = pd.concat([pd.read_csv(file) for file in roster_files], ignore_index=True)

    # Carica il file delle statistiche
    stats_df = pd.read_excel(stats_file)

    # Carica il file delle squadre (non utilizzato direttamente per ora, ma può servire)
    teams_df = pd.read_csv(teams_file)

    # Normalizziamo i nomi delle squadre per evitare errori di formattazione
    rosters_df["team"] = rosters_df["team"].str.strip().str.upper()

    # Lista delle squadre disponibili
    team_list = sorted(rosters_df["team"].unique())

    # Interfaccia Streamlit
    st.title("📊 Analisi Statistiche - per Squadra")

    # Selezione della squadra
    selected_team = st.selectbox("🏀 Seleziona una squadra:", team_list)

    # Filtriamo i dati della squadra selezionata
    team_data = rosters_df[rosters_df["team"] == selected_team]

    if team_data.empty:
        st.warning("⚠️ Nessun dato disponibile per questa squadra.")
    else:
        st.subheader(f"📌 Statistiche per {selected_team}")

        # Mostriamo la tabella dei dati
        st.dataframe(team_data)

        # Selezione della metrica da visualizzare (altezza, posizione, ecc.)
        stat_columns = ["height_clean", "position", "year", "hometown", "homestate", "previous_school"]  # Aggiungi altre colonne se necessario
        selected_stat = st.selectbox("📈 Seleziona una statistica:", stat_columns)

        # 📊 Grafico a barre per la statistica selezionata
        if selected_stat in ["height_clean", "year"]:  # Per colonna numerica
            fig_bar = px.bar(
                team_data,
                x="name",
                y=selected_stat,
                title=f"{selected_stat} per giocatrice",
                color="name"
            )
            st.plotly_chart(fig_bar)

        elif selected_stat == "position":  # Per colonna categorica (posizione)
            fig_bar = px.bar(
                team_data,
                x="position",
                title=f"Distribuzione per posizione",
                color="position",
                category_orders={"position": sorted(team_data["position"].unique())}
            )
            st.plotly_chart(fig_bar)

        # 📊 Distribuzione della statistica scelta (per colonne numeriche come height, year)
        if selected_stat in ["height_clean", "year"]:
            fig_hist = px.histogram(
                team_data,
                x=selected_stat,
                nbins=10,
                title=f"Distribuzione di {selected_stat}",
                color_discrete_sequence=["#1f77b4"]
            )
            st.plotly_chart(fig_hist)

        # 📌 Comparazione tra due statistiche (altezza vs posizione, ad esempio)
        selected_stat_2 = st.selectbox("📊 Seleziona una seconda statistica:", stat_columns)
        fig_scatter = px.scatter(
            team_data,
            x=selected_stat,
            y=selected_stat_2,
            text="name",
            title=f"Confronto {selected_stat} vs {selected_stat_2}",
            color="name",
            size_max=15
        )
        fig_scatter.update_traces(textposition="top center")
        st.plotly_chart(fig_scatter)

        # 📌 Radar Chart per confronto multiplo (puoi scegliere statistiche numeriche da confrontare)
        num_players = len(team_data)
        if num_players > 1:
            selected_players = st.multiselect("👤 Seleziona giocatrici per radar chart:", team_data["name"].unique())

            if selected_players:
                radar_data = team_data[team_data["name"].isin(selected_players)]
                fig_radar = go.Figure()
                for _, row in radar_data.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=row[stat_columns].values,  # Adatta le colonne numeriche che vuoi nel radar chart
                        theta=stat_columns,
                        fill="toself",
                        name=row["name"]
                    ))
                fig_radar.update_layout(title="📡 Radar Chart Statistiche")
                st.plotly_chart(fig_radar)
                
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

   
# Footer
st.write("App creata da Giulia (e Chat) usando Streamlit e Plotly")
