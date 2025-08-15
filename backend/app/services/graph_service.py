from .transaction_service import get_transactions_from_neo4j  # atau path yg sesuai

def get_wallet_graph(address: str, sort_by: str = "timestamp", order: str = "desc", limit: int = 30):
    """
    Pulangkan JSON:
      { nodes: [{id, label}], edges: [{id, from, to, value, timestamp}] }
    berdasarkan transaksi hasil Neo4j.
    """
    rows = get_transactions_from_neo4j(
        wallet=address, sort_by=sort_by, order=order, limit=limit
    )
    nodes, edges, seen = [], [], set()

    def add_node(addr):
        if addr and addr not in seen:
            nodes.append({"id": addr, "label": addr})
            seen.add(addr)

    for sender, receiver, value, timestamp in rows:
        add_node(sender)
        add_node(receiver)
        edges.append({
            "id": f"{sender}->{receiver}@{timestamp}",
            "from": sender,
            "to": receiver,
            "value": float(value) if value is not None else 0.0,
            "timestamp": timestamp
        })

    return {"nodes": nodes, "edges": edges}