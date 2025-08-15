from flask_restx import Namespace, Resource, fields
from app.services.risk_analysis import get_wallet_risk_distribution

api = Namespace('risk', description='Risk related endpoints')

dist_pct_model = api.model('WalletRiskPct', {
    'critical': fields.Float,
    'high': fields.Float,
    'medium': fields.Float,
})

dist_model = api.model('WalletRiskDistribution', {
    'total': fields.Integer,
    'critical': fields.Integer,
    'high': fields.Integer,
    'medium': fields.Integer,
    'pct': fields.Nested(dist_pct_model)
})

@api.route('/wallets/distribution')
class WalletRiskDistribution(Resource):
    @api.marshal_with(dist_model, code=200)
    def get(self):
        """Distribusi wallet per kategori risiko (critical/high/medium)"""
        return get_wallet_risk_distribution(), 200