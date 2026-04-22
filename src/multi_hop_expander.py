# src/multi_hop_expander.py

from collections import deque

class MultiHopExpander:
    def __init__(self, data_pipeline, graph_builder, exchange_addresses=None):
        self.dp = data_pipeline
        self.gb = graph_builder
        self.exchange_addresses = set(exchange_addresses or [])

    # ✅ NEW: Get next-hop neighbors (manual mode support)
    def get_next_addresses(self, wallet: str):
        """
        Fetch neighbors with transaction stats (value + count)
        """
        try:
            df = self.dp.fetch_transactions(wallet)
        except Exception as e:
            print(f"[ERROR] Failed to fetch {wallet}: {e}")
            return {}

        if df.empty:
            return {}

        self.gb.build_graph(df)

        from_col = "from"
        to_col = "to"
        value_col = "value"

        stats = {}

        for _, row in df.iterrows():
            from_addr = row[from_col]
            to_addr = row[to_col]
            value = float(row[value_col]) / 1e18  # wei → ETH

            # Determine neighbor
            if from_addr.lower() == wallet.lower():
                addr = to_addr
            else:
                addr = from_addr

            if addr == wallet:
                continue

            if addr not in stats:
                stats[addr] = {"value": 0, "count": 0}

            stats[addr]["value"] += value
            stats[addr]["count"] += 1

        return stats

    # 🔹 EXISTING BFS (kept for optional auto mode)
    def expand(
        self,
        start_wallet: str,
        max_hops: int = 2,
        stop_at_exchange: bool = True
    ):
        visited = set()
        queue = deque([(start_wallet, 0)])

        while queue:
            wallet, depth = queue.popleft()

            if wallet in visited or depth > max_hops:
                continue

            print(f"[HOP {depth}] Expanding wallet: {wallet}")
            visited.add(wallet)

            try:
                df = self.dp.fetch_transactions(wallet)
            except Exception as e:
                print(f"[SKIP] Failed to fetch {wallet}: {e}")
                continue

            self.gb.build_graph(df)

            if stop_at_exchange and wallet in self.exchange_addresses:
                print(f"[STOP] Exchange reached: {wallet}")
                continue

            neighbors = set(df["to"]).union(set(df["from"]))
            neighbors.discard(wallet)

            for n in neighbors:
                if n not in visited:
                    queue.append((n, depth + 1))

        print("[DONE] Multi-hop expansion complete")