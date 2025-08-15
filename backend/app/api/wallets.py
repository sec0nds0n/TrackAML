from flask_restx import Namespace, Resource, fields
from flask import request, abort
from psycopg2.extras import RealDictCursor

from ..database import get_db_connection
from ..services.wallet_service import (
    update_all_wallets_logic,
    sync_database_logic,
    fetch_all_transactions,
    get_wallet_kyc,
    get_wallet_balance_stats,
    get_wallet_risk_flags
)
from ..services.transaction_service import (
    get_first_large_tx_api,
    get_wallet_risk_metrics,
)
from ..services.kyc_service import (
    check_wallet_in_history,
)
from ..services.graph_service import get_wallet_graph

# Satu namespace saja: /api/wallets
api = Namespace('wallets', description='Wallet endpoints')

# ====== Models (Swagger) ======
wallet_history_row = api.model('WalletHistoryRow', {
    'address': fields.String(required=True, description='Wallet address'),
    'queried_at': fields.DateTime(required=False, description='Last queried timestamp'),
})

history_check_model = api.model('WalletHistoryCheck', {
    'address': fields.String(description='Wallet address'),
    'in_history': fields.Boolean(description='Is the address stored in history'),
})

# ====== Admin/maintenance endpoints ======
@api.route('/update-all')
class UpdateAllWallets(Resource):
    # @jwt_required
    def post(self):
        """Fetch & update all wallets from history table"""
        success, fail = update_all_wallets_logic()
        return {
            "message": f"Selesai update {success} wallet. Gagal: {fail}",
            "success": success,
            "failed": fail
        }, 200

@api.route('/sync')
class SyncDatabase(Resource):
    # @jwt_required
    def post(self):
        """Sinkronisasi database ke Neo4j dan update blacklist"""
        ok = sync_database_logic()
        if not ok:
            return {"message": "Neo4j tidak tersedia, sync gagal."}, 503
        return {"message": "✅ Sinkronisasi database berhasil!"}, 200

# ====== History (recent searched wallets) ======
@api.route('/history')
class WalletHistory(Resource):
    @api.marshal_list_with(wallet_history_row)
    def get(self):
        """List recent wallet history (limit 10)"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT address, queried_at
            FROM wallet_history
            ORDER BY queried_at DESC NULLS LAST
            LIMIT 10
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            {"address": r[0], "queried_at": r[1] if r[1] else None}
            for r in rows
        ]

# ====== Wallet detail/summary ======
@api.route('/<string:address>/summary')
@api.param('address', 'Wallet address')
class WalletSummary(Resource):
    def get(self, address):
        """Get KYC/summary for a wallet"""
        data = get_wallet_kyc(address)
        if not data:
            abort(404, 'Wallet not found')
        return data

@api.route('/<string:address>/history-check')
@api.param('address', 'Wallet address')
class WalletHistoryCheck(Resource):
    @api.marshal_with(history_check_model)
    def get(self, address):
        """Check if wallet exists in history"""
        return {'address': address, 'in_history': check_wallet_in_history(address)}

# ====== Transactions ======
@api.route('/<string:address>/transactions/all')
@api.param('address', 'Wallet address')
class WalletTransactionsAll(Resource):
    def get(self, address):
        """Get all transactions of a wallet (no pagination)"""
        return fetch_all_transactions(address)

@api.route('/transactions')
class WalletTransactionsPaged(Resource):
    def get(self):
        """
        Paginated transactions for a given wallet.
        Query params:
          - wallet: address (required)
          - page:   int (default 1)
          - per_page: int (default 20)
        """
        wallet = request.args.get('wallet')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        if not wallet:
            return {"message": "wallet is required"}, 400

        offset = (page - 1) * per_page

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT sender, receiver, value, timestamp
            FROM transactions
            WHERE sender = %s OR receiver = %s
            ORDER BY timestamp DESC
            LIMIT %s OFFSET %s
        """, (wallet, wallet, per_page, offset))
        rows = cur.fetchall()

        cur.execute("""
            SELECT COUNT(*) FROM transactions
            WHERE sender = %s OR receiver = %s
        """, (wallet, wallet))
        total = cur.fetchone()[0]

        cur.close()
        conn.close()

        return {
            "transactions": [
                {"sender": r[0], "receiver": r[1], "value": r[2], "timestamp": r[3].isoformat()}
                for r in rows
            ],
            "total": total,
            "page": page,
            "per_page": per_page
        }

# ====== Large transactions & alerts ======
@api.route('/<string:address>/large-transactions')
@api.param('address', 'Wallet address')
class WalletLargeTransactions(Resource):
    def get(self, address):
        """Get first large transactions for a wallet (above threshold)."""
        data = get_first_large_tx_api(address)
        if not data:
            return [], 204
        return data, 200

@api.route('/<string:address>/alerts')
@api.param('address', 'Wallet address')
class WalletAlerts(Resource):
    def get(self, address):
        """List alerts generated for a wallet"""
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id, detector_name, payload, created_at
            FROM alerts
            WHERE wallet_address = %s
            ORDER BY created_at DESC
        """, (address,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows, 200
    
@api.route('/<string:address>/stats')
class WalletStats(Resource):
    def get(self, address):
        data = get_wallet_balance_stats(address)
        return {
            "address": data["address"],
            "symbol": data["symbol"],
            "balance": data["balance"],
            "balanceUSD": data["balance_usd"],
            "totalReceived": data["total_received"],
            "totalSent": data["total_sent"],
            "transactionCount": data["transaction_count"],
            "uniqueCounterparties": data["unique_counterparties"],
            # === Tambahan untuk frontend card "Transaksi Pertama / Terakhir" ===
            "firstTx": {
                "txHash": data["first_tx"]["txHash"],
                "sender": data["first_tx"]["sender"],
                "receiver": data["first_tx"]["receiver"],
                "value": data["first_tx"]["value"],
                "timestamp": data["first_tx"]["timestamp"],
            },
            "lastTx": {
                "txHash": data["last_tx"]["txHash"],
                "sender": data["last_tx"]["sender"],
                "receiver": data["last_tx"]["receiver"],
                "value": data["last_tx"]["value"],
                "timestamp": data["last_tx"]["timestamp"],
            },
        }, 200
        
@api.route('/<string:address>/risk-metrics')
class WalletRiskMetrics(Resource):
    def get(self, address):
        hv  = float(request.args.get('highValueEth', 10))
        cut = int(request.args.get('riskScoreCutoff', 70))
        try:
            return get_wallet_risk_metrics(address, hv, cut), 200
        except Exception as e:
            # log e jika perlu
            return {"message": "Failed to compute risk metrics"}, 500
        
@api.route('/<string:address>/risk-flags')
class WalletRiskFlags(Resource):
    def get(self, address):
        data = get_wallet_risk_flags(address)
        return data, 200
    
@api.route('/<string:address>/graph')
@api.param('address', 'Wallet address')
class WalletGraph(Resource):
    def get(self, address):
        """
        Graph data:
        - mode=summary : 3 largest tx + 3 most-frequent counterparties
        - (opsional) mode=raw   : fallback ke limit/sort_by/order seperti sekarang
        """
        mode = request.args.get('mode', 'summary')
        if mode != 'summary':
            # --- fallback lama: optional, kalau masih mau dipakai ---
            limit   = int(request.args.get('limit', 30))
            sort_by = request.args.get('sort_by', 'timestamp')
            order   = request.args.get('order', 'desc')
            return get_graph_raw(address, limit, sort_by, order), 200

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # --- 3 transaksi terbesar (single tx), arah sesuai data ---
        cur.execute("""
            SELECT sender, receiver, value, timestamp
            FROM transactions
            WHERE sender = %s OR receiver = %s
            ORDER BY value DESC
            LIMIT 3
        """, (address, address))
        largest = cur.fetchall()

        # --- 3 counterparty paling sering bertransaksi dengan address ---
        cur.execute("""
            WITH all_tx AS (
              SELECT sender, receiver, value,
                     CASE WHEN sender = %s THEN receiver ELSE sender END AS counterparty,
                     CASE WHEN sender = %s THEN 1 ELSE 0 END AS is_out,
                     CASE WHEN receiver = %s THEN 1 ELSE 0 END AS is_in
              FROM transactions
              WHERE sender = %s OR receiver = %s
            )
            SELECT counterparty,
                   COUNT(*)                      AS cnt,
                   SUM(value)                    AS total_value,
                   SUM(is_out)                   AS out_cnt,
                   SUM(is_in)                    AS in_cnt
            FROM all_tx
            GROUP BY counterparty
            ORDER BY cnt DESC, total_value DESC
            LIMIT 3
        """, (address, address, address, address, address))
        freq = cur.fetchall()

        cur.close(); conn.close()

        # --- Build nodes ---
        nodes = {}
        def add_node(addr):
            if addr not in nodes:
                nodes[addr] = {"id": addr, "label": addr}

        add_node(address)
        for r in largest:
            add_node(r["sender"]); add_node(r["receiver"])
        for r in freq:
            add_node(r["counterparty"])

        # --- Build edges ---
        edges = []
        # largest edges (tiap baris = 1 transaksi)
        for i, r in enumerate(largest, 1):
            edges.append({
                "id": f"largest-{i}",
                "etype": "largest",
                "from": r["sender"],
                "to": r["receiver"],
                "value": float(r["value"]),
                "timestamp": r["timestamp"].isoformat() if r.get("timestamp") else None
            })

        # frequency edges (agregat ke tiap counterparty)
        for i, r in enumerate(freq, 1):
            # arah: mayoritas arah transaksi
            direction_from = address if (r["out_cnt"] or 0) >= (r["in_cnt"] or 0) else r["counterparty"]
            direction_to   = r["counterparty"] if direction_from == address else address
            edges.append({
                "id": f"freq-{i}",
                "etype": "freq",
                "from": direction_from,
                "to": direction_to,
                "count": int(r["cnt"]),
                "total": float(r["total_value"] or 0.0),
            })

        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }, 200