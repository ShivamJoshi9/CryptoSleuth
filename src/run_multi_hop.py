# src/run_multi_hop.py

from src.data_pipeline import DataPipeline
from src.graph_builder import GraphBuilder
from src.multi_hop_expander import MultiHopExpander
from src.config import EXCHANGE_ADDRESSES

import networkx as nx
import pandas as pd
import os

# 🔐 TEMPORARY (move to .env later)
API_KEY = "GT9V4F1TK8N2NQ4Q6E2XU21TAFPCFDVIJP"

# 🔹 Start wallet
START_WALLET = "0x0b3e01C1397551CBe713B4eAA15aac9f1ac211dA"


def main():
    # ===============================
    # 1️⃣ Initialize components
    # ===============================
    dp = DataPipeline(API_KEY)
    gb = GraphBuilder()
    expander = MultiHopExpander(dp, gb, EXCHANGE_ADDRESSES)

    # ===============================
    # 2️⃣ Manual Multi-hop (No limit)
    # ===============================
    current_wallet = START_WALLET
    visited = set()
    path = [START_WALLET]

    hop = 1

    while True:
        print(f"\n🔎 Hop {hop}")
        print(f"Current Wallet: {current_wallet}")

        neighbors = expander.get_next_addresses(current_wallet)

        # ✅ Avoid revisiting
        neighbors = [n for n in neighbors if n not in visited]

        if not neighbors:
            print("No more new connections.")
            break

        print("\nConnected wallets:")
        for i, addr in enumerate(neighbors):
            tag = " (EXCHANGE)" if addr in EXCHANGE_ADDRESSES else ""
            print(f"{i}: {addr}{tag}")

        user_input = input("\nSelect index OR press 'q' to stop: ")

        if user_input.lower() == 'q':
            print("Stopping investigation...")
            break

        try:
            choice = int(user_input)
            selected_wallet = neighbors[choice]
        except:
            print("Invalid input. Try again.")
            continue

        visited.add(current_wallet)
        current_wallet = selected_wallet
        path.append(selected_wallet)

        # ✅ 🚨 Exchange auto-stop (your addition)
        if current_wallet in EXCHANGE_ADDRESSES:
            print("🚨 Exchange reached. Stopping.")
            break

        hop += 1

    print("\n==== FINAL GRAPH BUILT ====")
    print("Nodes:", len(gb.G.nodes()))
    print("Edges:", len(gb.G.edges()))

    # ===============================
    # 3️⃣ Create output folders
    # ===============================
    os.makedirs("data/graphs", exist_ok=True)
    os.makedirs("data/paths", exist_ok=True)
    os.makedirs("data/edges", exist_ok=True)

    # ===============================
    # 4️⃣ Save graph (Gephi)
    # ===============================
    nx.write_gexf(gb.G, "data/graphs/manual_graph.gexf")
    print("✔ Graph saved to data/graphs/manual_graph.gexf")

    # ===============================
    # 5️⃣ Save selected path
    # ===============================
    with open("data/paths/manual_path.txt", "w") as f:
        f.write(" -> ".join(path))

    print("✔ Path saved to data/paths/manual_path.txt")

    # ===============================
    # 6️⃣ Save edges as CSV
    # ===============================
    edges = []
    for u, v, data in gb.G.edges(data=True):
        edges.append({
            "from": u,
            "to": v,
            "value": data.get("value"),
            "timestamp": data.get("timestamp"),
            "tx_hash": data.get("hash")
        })

    df_edges = pd.DataFrame(edges)
    df_edges.to_csv("data/edges/manual_edges.csv", index=False)
    print("✔ Edges saved to data/edges/manual_edges.csv")


if __name__ == "__main__":
    main()