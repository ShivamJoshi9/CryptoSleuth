# src/app.py

from flask import Flask, render_template, request, redirect, url_for

from src.data_pipeline import DataPipeline
from src.graph_builder import GraphBuilder
from src.multi_hop_expander import MultiHopExpander
from src.config import EXCHANGE_ADDRESSES

app = Flask(__name__)

# 🔐 API KEY (replace with your own)
API_KEY = "GT9V4F1TK8N2NQ4Q6E2XU21TAFPCFDVIJP"

# Initialize components
dp = DataPipeline(API_KEY)
gb = GraphBuilder()
expander = MultiHopExpander(dp, gb, EXCHANGE_ADDRESSES)

# Global state (simple session-like behavior)
current_wallet = None
path = []


# ===============================
# 🏠 HOME PAGE
# ===============================
@app.route("/", methods=["GET", "POST"])
def index():
    global current_wallet, path

    if request.method == "POST":
        wallet = request.form.get("wallet")

        if not wallet:
            return redirect(url_for("index"))

        current_wallet = wallet
        path = [wallet]

        return redirect(url_for("explore"))

    return render_template("index.html")


# ===============================
# 🔍 EXPLORE PAGE
# ===============================
@app.route("/explore")
def explore():
    MAX_EDGES = 5
    global current_wallet, path

    if not current_wallet:
        return redirect(url_for("index"))

    # Fetch neighbors
    try:
        neighbors = expander.get_next_addresses(current_wallet)
    except Exception as e:
        print("Error fetching data:", e)
        neighbors = {}

    # Sort by ETH value
    neighbors = dict(sorted(
        neighbors.items(),
        key=lambda x: x[1].get("value", 0),
        reverse=True
    ))

# ===============================
# 🔹 BUILD GRAPH DATA
# ===============================

    nodes = []
    edges = []

    # 🔥 1. Add PATH (horizontal line)
    for i, addr in enumerate(path):

        nodes.append({
            "id": addr,
            "x": i * 250,
            "y": 0
        })

        if i > 0:
            edges.append({
                "from": path[i - 1],
                "to": addr
            })

    # 🔥 2. Add CURRENT NEIGHBORS (expand options)

    count = 0
    y_start = -200
    gap = 80

    for i, (addr, data) in enumerate(neighbors.items()):

        if addr not in path:

            if addr not in [n["id"] for n in nodes]:
                nodes.append({
                    "id": addr,
                    "x": len(path) * 250,
                    "y": y_start + count * gap   # 🔥 FIX: use count
                })

            edges.append({
                "from": current_wallet,
                "to": addr,
                "value": data.get("value", 0),
                "is_exchange": addr in EXCHANGE_ADDRESSES
            })

            count += 1

            if count >= MAX_EDGES:   # 🔥 FIX: use count
                break

    # ===============================
    # 🔹 RENDER TEMPLATE
    # ===============================
    return render_template(
        "explore.html",
        wallet=current_wallet,
        neighbors=neighbors,
        path=path,
        exchanges=list(EXCHANGE_ADDRESSES),
        nodes=nodes,
        edges=edges
    )


# ===============================
# ➡️ SELECT NEXT WALLET
# ===============================
@app.route("/select/<address>")

def select(address):
    global current_wallet, path

    current_wallet = address

    # Avoid duplicate in path
    if not path or path[-1] != address:
        path.append(address)

    # Stop if exchange
    if address in EXCHANGE_ADDRESSES:
        print("🚨 Exchange reached:", address)
    # Do NOT stop — continue exploration

    return redirect(url_for("explore"))

# ===============================
# 🔄 RESET (START NEW)
# ===============================

@app.route("/reset")
def reset():
    global current_wallet, path

    current_wallet = None
    path = []

    return redirect(url_for("index"))


# ===============================
# 🚀 RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)