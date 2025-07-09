import json
from flask import Blueprint, request, abort, make_response
from flask_restx import Api, Resource, Namespace, fields
from .users import api as ns_users
from .auth import api as ns_auth

from ..services.transaction_service import (
    get_high_risk_address_count,
    get_anomaly_transaction_count,
    get_anomaly_cases,
    get_transaction_details,
    get_first_large_tx_api,
)
from ..services.risk_analysis import (
    get_risk_distribution,
    get_wallet_risk_cases,
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
ns_wallets = Namespace('wallets', description='Wallet endpoints')
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

# Anomaly endpoints
@ns_anomalies.route('/count')
class AnomalyCount(Resource):
    @ns_anomalies.marshal_with(anom_count_model)
    def get(self):
        """Get count of anomaly transactions"""
        return {'count': get_anomaly_transaction_count()}

# Risk endpoints
@ns_risk.route('/high-risk-addresses/count')
class HighRiskCount(Resource):
    @ns_risk.marshal_with(risk_count_model)
    def get(self):
        """Get count of high risk addresses"""
        return get_high_risk_address_count()

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

# Wallet endpoints
@ns_wallets.route('/<string:address>/summary')
@ns_wallets.param('address', 'Wallet address')
class WalletSummary(Resource):
    def get(self, address):
        """Get KYC summary for a wallet"""
        data = get_wallet_kyc(address)
        if not data:
            abort(404, 'Wallet not found')
        return data

@ns_wallets.route('/<string:address>/history-check')
@ns_wallets.param('address', 'Wallet address')
class WalletHistoryCheck(Resource):
    @ns_wallets.marshal_with(wallet_history_model)
    def get(self, address):
        """Check if wallet exists in history"""
        return {'address': address, 'in_history': check_wallet_in_history(address)}

@ns_wallets.route('/<string:address>/transactions/all')
@ns_wallets.param('address', 'Wallet address')
class WalletTransactionsAll(Resource):
    def get(self, address):
        """Get all transactions of a wallet (no pagination)"""
        return fetch_all_transactions(address)
    
@ns_wallets.route('/<string:address>/large-transactions')
@ns_wallets.param('address', 'Wallet address')
class WalletLargeTransactions(Resource):
    def get(self, address):
        """Get first large transactions for a wallet (above threshold)."""
        data = get_first_large_tx_api(address)
        if not data:
            return [], 204
        return data, 200

@ns_wallets.route('/<string:address>/alerts')
class WalletAlerts(Resource):
    def get(self, address):
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
@ns_darkweb.param('address', 'Wallet address')
class AhmiaSearch(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    def get(self, address):
        """Search wallet address on Ahmia (dark web)"""
        return search_ahmia(address)

@ns_darkweb.route('/dread/<string:address>')
@ns_darkweb.param('address', 'Wallet address')
class DreadSearch(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    def get(self, address):
        """Search wallet address on Dread forum (dark web)"""
        return search_dread(address)

@ns_darkweb.route('/stored/<string:address>')
@ns_darkweb.param('address', 'Wallet address')
class DarkwebStored(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
    def get(self, address):
        """Get stored Dark Web results for a wallet"""
        return get_darkweb_results(address)

@ns_darkweb.route('/stored/<string:source>/<string:address>')
@ns_darkweb.param('source', 'Source: ahmia or dread')
@ns_darkweb.param('address', 'Wallet address')
class DarkwebStoredBySource(Resource):
    @ns_darkweb.marshal_list_with(darkweb_result)
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