import json
from flask import Blueprint, request, abort, make_response
from flask_restx import Api, Resource, Namespace, fields
from psycopg2.extras import RealDictCursor
from ..utils import jwt_required, jwt_roles_required, roles_required

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
    @ns_anomalies.marshal_list_with(anomaly_tx_model)
    def get(self):
        """List semua transaksi dengan is_anomaly = TRUE"""
        return get_anomaly_transactions()

@ns_anomalies.route('/blacklist')
class BlacklistedWalletList(Resource):
    @ns_anomalies.marshal_list_with(blacklisted_wallet_model)
    def get(self):
        """List semua wallet yang diblacklist"""
        return get_blacklisted_wallets()
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