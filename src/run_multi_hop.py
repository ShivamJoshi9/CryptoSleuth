from src.data_pipeline import DataPipeline
from src.graph_builder import GraphBuilder
from src.multi_hop_expander import MultiHopExpander
from src.config import EXCHANGE_ADDRESSES

import networkx as nx
import pandas as pd
import os

# 🔐 TEMPORARY (do NOT commit)
API_KEY = "GT9V4F1TK8N2NQ4Q6E2XU21TAFPCFDVIJP"

# 🔹 Wallet to start investigation
START_WALLET = "0x0b3e01C1397551CBe713B4eAA15aac9f1ac211dA"


def main():
    # ===============================
    # 1️⃣ Initialize components
    # ===============================
    dp = DataPipeline(API_KEY)
    gb = GraphBuilder()

    expander = MultiHopExpander(dp, gb, EXCHANGE_ADDRESSES)

    # ===============================
    # 2️⃣ Multi-hop expansion
    # ===============================
    expander.expand(
        start_wallet=START_WALLET,
        max_hops=3,
        stop_at_exchange=True
    )

    print("\n==== GRAPH BUILT ====")
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
    nx.write_gexf(gb.G, "data/graphs/multihop_graph.gexf")
    print("✔ Graph saved to data/graphs/multihop_graph.gexf")

    # ===============================
    # 5️⃣ Save fund-flow paths
    # ===============================
    with open("data/paths/fund_flow_paths.txt", "w") as f:
        for ex in EXCHANGE_ADDRESSES:
            if ex not in gb.G:
                continue
            try:
                path = nx.shortest_path(gb.G, START_WALLET, ex)
                f.write(" -> ".join(path) + "\n")
            except nx.NetworkXNoPath:
                pass

    print("✔ Paths saved to data/paths/fund_flow_paths.txt")

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
    df_edges.to_csv("data/edges/multihop_edges.csv", index=False)
    print("✔ Edges saved to data/edges/multihop_edges.csv")


if __name__ == "__main__":
    main()



#python -m src.run_multi_hop
#0x742d35Cc6634C0532925a3b844Bc454e4438f44e
