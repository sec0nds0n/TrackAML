from flask_restx import Namespace, Resource, fields
from flask import request, g, abort
from psycopg2.extras import RealDictCursor

from ..utils import login_required, roles_required, jwt_required, jwt_roles_required
from ..database import get_db_connection
from ..services.case_service import (
    list_cases,
    assign_case,                 # assign user → case (dipakai /cases/<id>/assign)
    create_case,
    update_case,
    get_case_with_assignments,
    get_active_case_count,
    get_urgent_case_count,
    get_recent_cases,
)

api = Namespace('cases', description='Manage AML cases')

# ===== Enum mapping yang valid ke DB =====
# DB enum case_type_enum berisi: 'anomaly transaction', 'suspicious wallet'
CASE_TYPE_MAP = {
    'wallet': 'suspicious wallet',
    'transaction': 'anomaly transaction',
    'tx': 'anomaly transaction',
}

# ---------- Swagger Models ----------
assignment_model = api.model('Assignment', {
    'user_id': fields.Integer,
    'assigned_at': fields.DateTime
})

case_model = api.model('Case', {
    'id': fields.Integer,
    'case_type': fields.String,          # 'anomaly transaction' | 'suspicious wallet'
    'reference_id': fields.String,       # tx hash / address
    'payload': fields.Raw,
    'status': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'reason': fields.String,
    'source': fields.String,
    'description': fields.String,
    'severity': fields.String,
    'tags': fields.List(fields.String),
    'assignments': fields.List(fields.Nested(assignment_model))
})

case_create_model = api.model('CaseCreate', {
    'type': fields.String(required=True, description="transaction | wallet"),
    'reference_id': fields.String(required=True, description='tx_hash atau address'),
})

case_update_model = api.model('CaseUpdate', {
    'description': fields.String,
    'status': fields.String,
    'reason': fields.String,
    'source': fields.String,
    'tags': fields.List(fields.String),
    'severity': fields.String,
})

active_count_model = api.model('ActiveCaseCount', {
    'count': fields.Integer(required=True)
})

urgent_count_model = api.model('UrgentCaseCount', {
    'count': fields.Integer(required=True)
})

# NEW: link entity → case (dipakai frontend)
assign_entity_model = api.model('AssignCaseIn', {
    'entity_type': fields.String(required=True, enum=['wallet', 'tx']),
    'entity_key': fields.String(required=True, description='wallet address / tx hash'),
    'case_id': fields.Integer(required=False, description='Jika diisi, pakai case tersebut'),
    'title': fields.String(required=False, description='Judul case baru bila case_id kosong'),
    'severity': fields.String(required=False)
})

assign_payload_model = api.model('AssignPayload', {
    'user_id': fields.Integer(required=True, description='ID pengguna')
})

# ---------- Helpers ----------
def row_to_case(row):
    return {
        "id": row["id"],
        "case_type": row["case_type"],
        "reference_id": row["reference_id"],
        "payload": row.get("payload") or {},
        "status": row["status"],
        "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        "reason": row.get("reason"),
        "source": row.get("source"),
        "description": row.get("description"),
        "severity": row.get("severity"),
        "tags": row.get("tags") or [],
    }

# ---------- Routes ----------

@api.route('')
class CaseList(Resource):
    @api.marshal_list_with(case_model)
    # @login_required
    @jwt_required
    def get(self):
        """List cases (non-admin hanya melihat case yg di-assign ke dirinya)"""
        limit = request.args.get('limit', default=50, type=int)
        all_cases = list_cases(limit)

        role = getattr(g, 'role', None)
        user_id = getattr(g, 'user_id', None)
        if role == 'admin' or user_id is None:
            return all_cases

        visible = []
        for c in all_cases:
            assigned_user_ids = [a.get('user_id') for a in c.get('assignments', [])]
            if user_id in assigned_user_ids:
                visible.append(c)
        return visible

    @api.expect(case_create_model)
    # @login_required
    @jwt_required
    def post(self):
        """Create a new case from anomaly or blacklist"""
        data = request.json or {}
        case_type_in = (data.get('type') or '').strip().lower()   # 'transaction' / 'wallet'
        reference = (data.get('reference_id') or '').strip()

        if not reference:
            return {'message': 'Reference is required'}, 400

        mapped = CASE_TYPE_MAP.get(case_type_in)
        if mapped is None:
            return {'message': 'Invalid case type'}, 400

        try:
            case_id = create_case(mapped, reference)   # service harus menerima enum final
            return {'message': 'Case created successfully', 'case_id': case_id}, 201
        except Exception as e:
            return {'message': str(e)}, 500


@api.route('/<int:case_id>/assign')
class CaseAssign(Resource):
    """Assign case ke user tertentu (admin / ops)"""
    @api.expect(assign_payload_model)
    # @login_required
    # @roles_required('admin')
    @jwt_required
    @jwt_roles_required('admin', 'analyst_L2', 'analyst_L1')
    def post(self, case_id):
        user_id = (request.get_json() or {}).get('user_id')
        if not user_id:
            return {'message': 'user_id required'}, 400
        assign_case(case_id, user_id)
        return {'status': 'assigned'}, 200


@api.route('/<int:case_id>')
class CaseDetail(Resource):
    """GET & PATCH gabung dalam satu resource"""

    # @login_required
    @jwt_required
    def get(self, case_id: int):
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    id,
                    case_type::text   AS case_type,
                    reference_id,
                    payload,
                    status::text      AS status,
                    created_at,
                    updated_at,
                    reason,
                    source,
                    description,
                    severity::text    AS severity,
                    COALESCE(tags, ARRAY[]::text[]) AS tags
                FROM cases
                WHERE id = %s
            """, (case_id,))
            row = cur.fetchone()
            if not row:
                abort(404, description='Case not found')
            return row_to_case(row), 200

    @api.expect(case_update_model)
    # @login_required
    @jwt_required
    def patch(self, case_id):
        """Update case (hanya admin atau user yang di-assign)"""
        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404

        role = getattr(g, 'role', None)
        user_id = getattr(g, 'user_id', None)
        assigned_user_ids = [a.get('user_id') for a in case.get('assignments', [])]

        if not (role == 'admin' or (user_id and user_id in assigned_user_ids)):
            return {'message': 'You are not allowed to edit this case'}, 403

        try:
            update_case(case_id, request.get_json() or {})
            return {'message': 'Case updated successfully'}, 200
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error', 'detail': str(e)}, 500


@api.route('/active-count')
class ActiveCaseCount(Resource):
    @api.marshal_with(active_count_model, code=200)
    def get(self):
        return get_active_case_count(), 200


@api.route('/urgent-count')
class UrgentCaseCount(Resource):
    @api.marshal_with(urgent_count_model, code=200)
    def get(self):
        return get_urgent_case_count(), 200


@api.route('/recent')
class CaseRecent(Resource):
    def get(self):
        """List recent cases for dashboard (exclude Dropped/Resolved)"""
        limit = request.args.get('limit', default=10, type=int)
        return get_recent_cases(limit), 200


# ========= NEW: Link entity (wallet/tx) ke case =========
@api.route('/assign')
class AssignEntityToCase(Resource):
    @api.expect(assign_entity_model, validate=True)
    # @login_required
    @jwt_required
    def post(self):
        """
        Assign wallet/tx menjadi entri di tabel cases.
        Jika sudah ada case untuk entity tsb → kembalikan case_id yang ada.
        """
        p = request.json or {}
        et = (p.get('entity_type') or '').strip().lower()   # 'wallet' | 'tx'
        ek = (p.get('entity_key') or '').strip()
        if not ek or et not in ('wallet', 'tx'):
            return {'message': 'Bad payload'}, 400

        case_type_enum_text = CASE_TYPE_MAP[et]  # 'suspicious wallet' / 'anomaly transaction'

        with get_db_connection() as conn, conn.cursor() as cur:
            # Cek sudah ada
            cur.execute("""
                SELECT id FROM cases
                 WHERE case_type::text = %s AND reference_id = %s
            """, (case_type_enum_text, ek))
            existing = cur.fetchone()
            if existing:
                return {'message': 'Case already exists', 'case_id': existing[0]}, 200

            # Buat baru
            cur.execute("""
                INSERT INTO cases (case_type, reference_id, status, severity, created_at)
                VALUES (%s::case_type_enum, %s, 'Under Review', %s, NOW())
                RETURNING id
            """, (case_type_enum_text, ek, p.get('severity') or 'medium'))
            case_id = cur.fetchone()[0]
            conn.commit()

        return {'ok': True, 'case_id': case_id}, 201