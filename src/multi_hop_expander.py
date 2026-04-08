# src/multi_hop_expander.py

from collections import deque

class MultiHopExpander:
    def __init__(self, data_pipeline, graph_builder, exchange_addresses=None):
        self.dp = data_pipeline
        self.gb = graph_builder
        self.exchange_addresses = set(exchange_addresses or [])

    def expand(
        self,
        start_wallet: str,
        max_hops: int = 2,
        stop_at_exchange: bool = True
    ):
        """
        Perform BFS-based multi-hop expansion from a wallet
        """
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

            # Add transactions to graph
            self.gb.build_graph(df)

            # Stop if exchange found
            if stop_at_exchange and wallet in self.exchange_addresses:
                print(f"[STOP] Exchange reached: {wallet}")
                continue

            # Extract neighbors
            neighbors = set(df["to"]).union(set(df["from"]))
            neighbors.discard(wallet)

            for n in neighbors:
                if n not in visited:
                    queue.append((n, depth + 1))

        print("[DONE] Multi-hop expansion complete")
