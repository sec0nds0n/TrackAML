from flask_restx import Namespace, Resource, fields, abort
from flask import session
from ..database import get_db_connection
from ..services.kyc_service import check_wallet_in_history
from ..services.kyc_service import get_wallet_summary
from ..services.wallet_service import (
    is_wallet_blacklisted,
    get_top_transactions,
    get_top_receivers,
    get_top_senders,
)
from ..services.transaction_service import (
    get_hourly_transaction_count,
    detect_recurring_transactions_raw,
    get_risky_interactions,
    get_blacklist_interactions,
)
from ..services.compliance_service import (
    compute_compliance_scores,
    overall_score,
    get_wallet_compliance_score,  # pastikan fungsi ini memang ada
)

api = Namespace('compliance', description='Compliance metrics')

# ----- Swagger Models -----
score_model = api.model('WalletComplianceScore', {
    'score': fields.Float(required=True, description='Percent normal wallets'),
    'total_wallets': fields.Integer,
    'anomalous_wallets': fields.Integer,
    'high_risk_wallets': fields.Integer,
    'blacklisted_wallets': fields.Integer,
})

breakdown_model = api.model('ComplianceBreakdown', {
    'kyc_compliance': fields.Integer,
    'transaction_monitoring': fields.Integer,
    'sanctions_screening': fields.Integer,
    'risk_assessment': fields.Integer,
    'regulatory_compliance': fields.Integer,
})

compliance_wrapper = api.model('Compliance', {
    'score': fields.Integer,
    'breakdown': fields.Nested(breakdown_model),
})

response_model = api.model('ComplianceResponse', {
    'wallet': fields.String,
    'wallet_not_found': fields.Boolean,
    'risk_profile': fields.String,
    'is_blacklisted': fields.Raw,
    'summary': fields.Raw,
    'top_transactions': fields.List(fields.Raw),
    'top_receivers': fields.List(fields.Raw),
    'top_senders': fields.List(fields.Raw),
    'risky_interactions': fields.List(fields.Raw),
    'recurring_pattern': fields.Raw,
    'blacklist_interactions': fields.List(fields.Raw),
    'hourly_counts': fields.Raw,
    'compliance': fields.Nested(compliance_wrapper),
    'last_updated': fields.Raw,
})

# ----- Routes -----
@api.route('/score')
class WalletComplianceScore(Resource):
    @api.marshal_with(score_model, code=200)
    def get(self):
        return get_wallet_compliance_score(), 200

@api.route('/<string:addr>')
class WalletCompliance(Resource):
    @api.response(200, 'OK', response_model)
    @api.response(401, 'Unauthorized')
    def get(self, addr: str):
        # Session-based access
        # if 'username' not in session:
        #     abort(401, 'Unauthorized')

        wallet = (addr or '').strip().lower()
        if not wallet:
            abort(400, 'wallet address is required')

        if not check_wallet_in_history(wallet):
            return {"wallet": wallet, "wallet_not_found": True}, 200

        blacklisted = is_wallet_blacklisted(wallet)
        summary = get_wallet_summary(wallet)
        top_transactions = get_top_transactions(wallet) or []
        top_receivers = get_top_receivers(wallet) or []
        top_senders = get_top_senders(wallet) or []
        risky_interactions = get_risky_interactions(wallet) or []
        recurring_pattern = detect_recurring_transactions_raw(wallet) or ""
        blacklist_interactions = get_blacklist_interactions(wallet) or []
        sender_hourly, receiver_hourly = get_hourly_transaction_count(wallet)

        # risk_profile dari tabel wallet_risk
        risk_profile = "Unknown"
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT risk_profile FROM wallet_risk WHERE address = %s", (wallet,))
        row = cur.fetchone()
        if row and row[0]:
            risk_profile = row[0]
        cur.close()
        conn.close()

        scores = compute_compliance_scores(
            has_kyc_profile=(risk_profile != "Unknown"),
            sanctions_hits=len(blacklist_interactions) + (1 if blacklisted else 0),
            risky_interactions=len(risky_interactions),
            recurring_flags=1 if recurring_pattern else 0,
            high_freq_flags=1 if (sum(sender_hourly) + sum(receiver_hourly)) > 50 else 0
        )
        total = overall_score(scores)

        return {
            "wallet": wallet,
            "wallet_not_found": False,
            "risk_profile": risk_profile,
            "is_blacklisted": blacklisted,
            "summary": summary,
            "top_transactions": top_transactions,
            "top_receivers": top_receivers,
            "top_senders": top_senders,
            "risky_interactions": risky_interactions,
            "recurring_pattern": recurring_pattern,
            "blacklist_interactions": blacklist_interactions,
            "hourly_counts": {"sender": sender_hourly, "receiver": receiver_hourly},
            "compliance": {"score": total, "breakdown": scores},
            "last_updated": None
        }, 200