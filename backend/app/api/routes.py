import json
from flask import Blueprint, request, abort, make_response
from flask_restx import Api, Resource, Namespace, fields
from psycopg2.extras import RealDictCursor
from ..utils import jwt_required, jwt_roles_required, roles_required
from ..database import get_db_connection

# Import namespaces from submodules
from .users import api as ns_users
from .auth import api as ns_auth
from .cases import api as ns_cases
from .wallets import api as ns_wallets
from .compliance import api as compliance_ns
from .risk import api as risk_ns
from .alerts import api as alerts_ns
from .regulatory import api as regulatory_api
from .notifications import api as notifications_api

# Import service functions
from ..services.transaction_service import (
    get_high_risk_address_count,
    get_anomaly_transaction_count,
    get_anomaly_cases,
    get_transaction_details,
    get_first_large_tx_api,
    get_blacklisted_wallets_count,
    get_anomaly_transactions,
    get_blacklisted_wallets,
    get_suspicious_summary,
    _normalize_to_eth,
)
from ..services.risk_analysis import (
    get_risk_distribution,
    get_wallet_risk_cases,
    get_high_risk_address_count as ra_get_high_risk_count,
)
from ..services.kyc_service import (
    check_wallet_in_history
)
from ..services.wallet_service import (
    get_wallet_kyc,
    fetch_all_transactions
)
from ..services.search_service import (
    save_search_query,
    get_recent_searches
)
from ..services.darkweb_service import (
    search_ahmia,
    search_dread,
    save_darkweb_results,
    get_darkweb_results
)

# Blueprint dan API setup
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(
    api_bp,
    version='1.0',
    title='TrackAML API',
    description='Auto-documented API for TrackAML using Swagger UI',
)

@api.representation('application/json')
def output_json(data, code, headers=None):
    """
    Gunakan default=str sehingga datetime → string via str(obj)
    """
    resp = make_response(json.dumps(data, default=str), code)
    resp.headers.extend(headers or {})
    return resp

# Define Namespaces
ns_anomalies = Namespace('anomalies', description='Anomaly endpoints')
ns_risk = Namespace('risk', description='Risk-related endpoints')
ns_aml = Namespace('aml-cases', description='AML Case endpoints')
ns_tx = Namespace('transactions', description='Transaction endpoints')
ns_search = Namespace('search', description='Search history endpoints')
ns_darkweb = Namespace('darkweb', description='Dark Web search endpoints')
ns_graph = Namespace('aml', description='AML analytics & graph endpoints')

# Models for documentation
risk_count_model = api.model('HighRiskCount', {
    'high_risk_addresses': fields.Integer(description='Count of high risk addresses')
})
anom_count_model = api.model('AnomalyCount', {
    'count': fields.Integer(description='Count of anomaly transactions')
})
search_list_model = api.model('RecentSearches', {
    'searches': fields.List(fields.String, description='Recent search queries')
})
wallet_history_model = api.model('WalletHistoryCheck', {
    'address': fields.String(description='Wallet address'),
    'in_history': fields.Boolean(description='In history flag')
})
darkweb_result = api.model('DarkWebResult', {
    'title': fields.String, 'url': fields.String
})

# Models untuk anomaly transactions dan blacklisted wallets
anomaly_tx_model = ns_anomalies.model('AnomalyTransaction', {
    'tx_hash': fields.String(description='Hash transaksi'),
    'sender': fields.String(description='Alamat pengirim'),
    'receiver': fields.String(description='Alamat penerima'),
    'value': fields.Float(description='Nilai transaksi'),
    'timestamp': fields.DateTime(description='Waktu transaksi'),
    'detector': fields.String(description='Detektor anomaly'),
    'reason': fields.String(description='Alasan anomaly')
})

# Page model untuk response {items,total}
anomaly_tx_page_model = ns_anomalies.model('AnomalyTransactionPage', {
    'items': fields.List(fields.Nested(anomaly_tx_model)),
    'total': fields.Integer(description='Total baris sebelum paging')
})

blacklisted_wallet_model = ns_anomalies.model('BlacklistedWallet', {
    'address': fields.String(description='Alamat wallet'),
    'source': fields.String(description='Sumber blacklist'),
    'category': fields.String(description='Kategori'),
    'reason': fields.String(description='Alasan'),
    'added_on': fields.DateTime(description='Waktu ditambahkan')
})

# Anomaly endpoints
@ns_anomalies.route('/count')
class AnomalyCount(Resource):
    @ns_anomalies.marshal_with(anom_count_model)
    def get(self):
        c = get_anomaly_transaction_count()
        if isinstance(c, dict):
            c = c.get('count', c.get('total_anomalies', 0))
        return {'count': int(c)}
@ns_anomalies.route('/transactions')
class AnomalyTransactionList(Resource):
    @ns_anomalies.marshal_with(anomaly_tx_page_model)
    def get(self):
        limit  = request.args.get('limit', type=int) or request.args.get('size', type=int) or 50
        if request.args.get('offset') is not None:
            offset = max(0, int(request.args.get('offset', 0)))
        else:
            page   = max(1, int(request.args.get('page', 1)))
            offset = (page - 1) * limit

        sort_by  = request.args.get('sort_by')  or 'created_at'
        sort_dir = request.args.get('sort_dir') or 'desc'
        q        = request.args.get('q') or ''
        detector = request.args.get('detector') or ''

        return get_anomaly_transactions(
            limit=limit, offset=offset,
            sort_by=sort_by, sort_dir=sort_dir,
            q=q, detector=detector,
            include_total=True
        )
@ns_anomalies.route('/blacklist')
class BlacklistedWalletList(Resource):
    def get(self):
        limit  = request.args.get('limit', type=int) or 50
        offset = request.args.get('offset', type=int) or 0
        q      = request.args.get('q') or ''
        sort_by  = request.args.get('sort_by')  or 'added_on'
        sort_dir = request.args.get('sort_dir') or 'desc'
        return get_blacklisted_wallets(
            limit=limit, offset=offset,
            q=q, sort_by=sort_by, sort_dir=sort_dir,
            include_total=False  # atau True kalau butuh total-nya juga
        )
@ns_anomalies.route('/summary')
class AnomalySummary(Resource):
    def get(self):
        """Summary untuk kartu dashboard suspicious transactions"""
        return get_suspicious_summary()
    
@ns_anomalies.route('/blacklist/count')
class BlacklistCount(Resource):
    @ns_anomalies.marshal_with(anom_count_model)  # { "count": int }
    def get(self):
        return get_blacklisted_wallets_count()
    
# Risk endpoints
@ns_risk.route('/high-risk-addresses/count')
class HighRiskAddressesCount(Resource):
    def get(self):
        # Ambil threshold (opsional)
        thr = request.args.get('threshold', type=float)
        data = ra_get_high_risk_count(threshold=thr) if thr is not None else ra_get_high_risk_count()

        # Normalisasi bentuk respons supaya frontend selalu dapat "count"
        count = data.get('count') or data.get('high_risk_addresses') or 0
        payload = { "count": int(count) }

        # Lewatkan field tambahan kalau ada (opsional)
        for k in ("by_chain", "threshold", "today", "yesterday", "delta_pct", "direction"):
            if k in data and data[k] is not None:
                payload[k] = data[k]

        return payload

@ns_risk.route('/distribution')
class RiskDistribution(Resource):
    def get(self):
        """Get distribution of risk profiles"""
        return get_risk_distribution()

# AML Case endpoints
@ns_aml.route('/anomalies')
class AMLAnomalies(Resource):
    def get(self):
        """Get recent anomaly-based AML cases"""
        limit = request.args.get('limit', default=10, type=int)
        return get_anomaly_cases(limit)

@ns_aml.route('/wallet-risk')
class AMLWalletRisk(Resource):
    def get(self):
        """Get recent wallet-risk AML cases"""
        limit = request.args.get('limit', default=10, type=int)
        return get_wallet_risk_cases(limit)

# Transaction endpoints
@ns_tx.route('/<string:tx_hash>')
@ns_tx.param('tx_hash', 'Transaction hash')
class TransactionDetail(Resource):
    def get(self, tx_hash):
        """Get details of a specific transaction"""
        data = get_transaction_details(tx_hash)
        if not data:
            abort(404, 'Transaction not found')
        return data

# Search endpoints
@ns_search.route('')
class UnifiedSearch(Resource):
    def get(self):
        """Search for transaction or wallet"""
        q = request.args.get('q', '').strip()
        if not q:
            abort(400, 'Query "q" is required')
        save_search_query(q)
        tx = get_transaction_details(q)
        if tx:
            return {'type': 'transaction', 'data': tx}
        summary = get_wallet_kyc(q)
        if summary:
            return {'type': 'wallet', 'data': summary}
        abort(404, 'No transaction or wallet found')

@ns_search.route('/recent')
class RecentSearches(Resource):
    @ns_search.marshal_with(search_list_model)
    def get(self):
        """Get recent search queries"""
        return {'searches': get_recent_searches(limit=5)}

# Dark Web search endpoints
@ns_darkweb.route('/ahmia/<string:address>')
class AhmiaSearch(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    @ns_darkweb.param('address', 'Wallet address')
    def get(self, address):
        """Search wallet address on Ahmia (dark web)"""
        return search_ahmia(address)

@ns_darkweb.route('/dread/<string:address>')
class DreadSearch(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    @ns_darkweb.param('address', 'Wallet address')
    def get(self, address):
        """Search wallet address on Dread forum (dark web)"""
        return search_dread(address)

@ns_darkweb.route('/stored/<string:address>')
class DarkwebStored(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    @ns_darkweb.param('address', 'Wallet address')
    def get(self, address):
        """Get stored Dark Web results for a wallet"""
        return get_darkweb_results(address)

@ns_darkweb.route('/stored/<string:source>/<string:address>')
class DarkwebStoredBySource(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    @ns_darkweb.param('source', 'Source: ahmia or dread')
    @ns_darkweb.param('address', 'Wallet address')
    def get(self, source, address):
        """Get stored Dark Web results filtered by source"""
        return get_darkweb_results(address, source)
    
@ns_graph.route('/addresses/<string:address>/flow_sankey')
class FlowSankey(Resource):
    def get(self, address):
        # params
        depth = request.args.get('depth', default=2, type=int)
        limit_peers = request.args.get('limit_peers', default=30, type=int)
        limit_peers = max(5, min(limit_peers, 200))

        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT LOWER(address) AS a FROM blacklist_addresses")
            blacklisted = {row["a"] for row in cur.fetchall()}

            cur.execute("SELECT LOWER(address) AS a FROM wallet_risk WHERE risk_profile = 'High Risk'")
            high_risk = {row["a"] for row in cur.fetchall()}

            cur.execute("""
                SELECT sender, receiver, value, timestamp
                FROM transactions
                WHERE lower(sender) = lower(%s) OR lower(receiver) = lower(%s)
            """, (address, address))
            rows = cur.fetchall()

        incoming_total = 0.0
        outgoing_total = 0.0
        by_peer = {}

        for r in rows:
            s, rcpt, v, _ts = r["sender"], r["receiver"], r["value"], r["timestamp"]
            v_eth = _normalize_to_eth(float(v) if v is not None else 0.0)
            if not v_eth:
                continue
            if rcpt.lower() == address.lower():
                direction, peer = "in", s
                incoming_total += v_eth
            else:
                direction, peer = "out", rcpt
                outgoing_total += v_eth

            key = (direction, peer)
            by_peer.setdefault(key, {"sum": 0.0, "count": 0})
            by_peer[key]["sum"] += v_eth
            by_peer[key]["count"] += 1

        peers_sorted = sorted(by_peer.items(), key=lambda kv: kv[1]["sum"], reverse=True)[:limit_peers]

        nodes = [{"name": address}]
        node_set = {address.lower()}
        links = []

        def peer_flag(lower_addr: str) -> str:
            if lower_addr in blacklisted: return "blacklisted"
            if lower_addr in high_risk:   return "risky"
            return "normal"

        for (direction, peer), agg in peers_sorted:
            pl = peer.lower()
            if pl not in node_set:
                nodes.append({"name": peer})
                node_set.add(pl)
            flag = peer_flag(pl)
            if direction == "in":
                links.append({"source": peer, "target": address, "value": round(agg["sum"], 6), "flag": flag})
            else:
                links.append({"source": address, "target": peer, "value": round(agg["sum"], 6), "flag": flag})

        by_sum = sorted(((peer, v) for ((_, peer), v) in by_peer.items()), key=lambda x: x[1]["sum"], reverse=True)[:3]
        by_cnt = sorted(((peer, v) for ((_, peer), v) in by_peer.items()), key=lambda x: x[1]["count"], reverse=True)[:3]

        return {
            "nodes": nodes,
            "links": links,
            "summary": {
                "incoming_total": round(incoming_total, 6),
                "outgoing_total": round(outgoing_total, 6),
                "top_biggest": [{"peer": p, "total": round(v["sum"], 6)} for p, v in by_sum],
                "top_frequent": [{"peer": p, "count": v["count"]} for p, v in by_cnt]
            }
        }

# Register namespaces
api.add_namespace(ns_anomalies)
api.add_namespace(ns_risk)
api.add_namespace(ns_aml)
api.add_namespace(ns_tx)
api.add_namespace(ns_wallets)
api.add_namespace(ns_search)
api.add_namespace(ns_darkweb)
api.add_namespace(ns_users)
api.add_namespace(ns_auth)
api.add_namespace(ns_cases)
api.add_namespace(compliance_ns)
api.add_namespace(risk_ns)
api.add_namespace(alerts_ns)
api.add_namespace(regulatory_api)
api.add_namespace(notifications_api)
api.add_namespace(ns_graph)