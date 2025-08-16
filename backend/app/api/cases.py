from flask_restx import Namespace, Resource, fields
from flask import request, g, abort
from psycopg2 import errors as pg_errors
from psycopg2.extras import RealDictCursor, Json
from flask import current_app, send_file
from werkzeug.utils import secure_filename
from ..utils import login_required, roles_required, jwt_required, jwt_roles_required
from ..database import get_db_connection
from ..services.case_service import (
    list_cases,
    assign_case,
    create_case,
    update_case,
    get_case_with_assignments,
    get_active_case_count,
    get_urgent_case_count,
    get_recent_cases,
    can_user_see_case,
    list_case_comments,
    add_case_comment,
)

import hashlib, os, re



api = Namespace('cases', description='Manage AML cases')

# ===== Enum mapping yang valid ke DB =====
# DB enum case_type_enum berisi: 'anomaly transaction', 'suspicious wallet'
CASE_TYPE_MAP = {
    'wallet': 'suspicious wallet',
    'transaction': 'anomaly transaction',
    'tx': 'anomaly transaction',
}

MENTION_RE = re.compile(r'@([A-Za-z0-9_\.]{2,32})')

# --- enum normalizer (dinamis dari DB) ---
ENUM_CACHE = {}  # {'case_severity_enum': {'medium': 'MEDIUM', ...}, ...}
def enum_canon(enum_name: str, val):
    """Kembalikan label enum di DB yang cocok (case-insensitive), atau None."""
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    m = ENUM_CACHE.get(enum_name)
    if m is None:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                SELECT e.enumlabel
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = %s
            """, (enum_name,))
            rows = cur.fetchall()
        # map lowercase -> label persis di DB
        m = {r[0].lower(): r[0] for r in rows}
        ENUM_CACHE[enum_name] = m
    return m.get(s.lower())

def _allowed_file(app_cfg, filename: str) -> bool:
    ext = (filename.rsplit('.', 1)[-1] or '').lower()
    return ext in (app_cfg.get('ALLOWED_EXTENSIONS') or set())

# ---------- Swagger Models ----------
assignment_model = api.model('Assignment', {
    'user_id': fields.Integer,
    'assigned_at': fields.DateTime
})

case_model = api.model('Case', {
    'id': fields.Integer,
    'case_type': fields.String,
    'reference_id': fields.String,
    'payload': fields.Raw,
    'status': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'reason': fields.String,
    'source': fields.String,
    'description': fields.String,
    'severity': fields.String,
    'tags': fields.List(fields.String),
    'assignments': fields.List(fields.Nested(assignment_model)),
    'title': fields.String,
    'priority': fields.String,
    'typology': fields.String,
    'tlp': fields.String,
    'visibility': fields.String,
    'sla_due_at': fields.DateTime,
    'owner_id': fields.Integer,
})

case_create_model = api.model('CaseCreate', {
    'type': fields.String(required=True, description="transaction | wallet"),
    'reference_id': fields.String(required=True, description='tx_hash atau address'),
    'title': fields.String,
    'priority': fields.String,
    'typology': fields.String,
    'severity': fields.String,
    'reason': fields.String,
    'source': fields.String,
    'description': fields.String,
    'tags': fields.List(fields.String),
    'tlp': fields.String,
    'visibility': fields.String,
    'sla_due_at': fields.DateTime,
    'payload': fields.Raw,
    'assignToMe': fields.Boolean,
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
    'severity': fields.String(required=False),
    'priority': fields.String,
    'typology': fields.String,
    'reason': fields.String,
    'tags': fields.List(fields.String),
    'tlp': fields.String,
    'visibility': fields.String,
    'sla_due_at': fields.DateTime,
    'payload': fields.Raw,
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
        "title": row.get("title"),
        "priority": row.get("priority"),
        "typology": row.get("typology"),
        "tlp": row.get("tlp"),
        "visibility": row.get("visibility"),
        "sla_due_at": row.get("sla_due_at").isoformat() if row.get("sla_due_at") else None,
        "owner_id": row.get("owner_id"),
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
        data = request.json or {}
        case_type_in = (data.get('type') or '').strip().lower()
        reference = (data.get('reference_id') or '').strip()
        if not reference:
            return {'message': 'Reference is required'}, 400

        mapped = CASE_TYPE_MAP.get(case_type_in)
        if mapped is None:
            return {'message': 'Invalid case type'}, 400

        owner_id = None
        if data.get('assignToMe'):
            owner_id = getattr(g, 'user_id', None)

        # normalisasi ke label enum di DB
        norm = {
            'severity':   enum_canon('case_severity_enum',   data.get('severity')),
            'priority':   enum_canon('case_priority_enum',   data.get('priority')),
            'tlp':        enum_canon('tlp_enum',             data.get('tlp')),
            'visibility': enum_canon('visibility_enum',      data.get('visibility')),
        }
        
        try:
            case_id = create_case(
                mapped, reference,
                title=data.get('title'),
                priority=norm['priority'],
                typology=data.get('typology'),
                severity=norm['severity'],
                reason=data.get('reason'),
                source=data.get('source'),
                description=data.get('description'),
                tags=data.get('tags') or [],
                tlp=norm['tlp'],
                visibility=norm['visibility'],
                sla_due_at=data.get('sla_due_at'),
                owner_id=owner_id,
                payload=data.get('payload') or {},
            )
            return {'message': 'Case created successfully', 'case_id': case_id}, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except (pg_errors.InvalidTextRepresentation, pg_errors.UndefinedObject) as e:
            return {'message': 'Invalid enum value', 'detail': str(e).split('\n')[0]}, 400
        except Exception as e:
            return {'message': str(e)}, 500


@api.route('/<int:case_id>/assign')
class CaseAssign(Resource):
    """Assign case ke user tertentu (admin / ops)"""
    @api.expect(assign_payload_model)
    # @login_required
    # @roles_required('admin')
    @jwt_required
    @jwt_roles_required('admin', 'analyst_l2', 'analyst_l1', 'exchanger')
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
                    COALESCE(tags, ARRAY[]::text[]) AS tags,
                    title,
                    priority::text     AS priority,
                    typology,
                    tlp::text          AS tlp,
                    visibility::text   AS visibility,
                    sla_due_at,
                    owner_id
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
        # mapping ke label enum DB; default severity -> 'medium' versi DB
        sev = enum_canon('case_severity_enum', p.get('severity')) or enum_canon('case_severity_enum', 'medium')
        pri = enum_canon('case_priority_enum', p.get('priority'))
        tlp = enum_canon('tlp_enum', p.get('tlp'))
        vis = enum_canon('visibility_enum', p.get('visibility'))
        
        et = (p.get('entity_type') or '').strip().lower()
        ek = (p.get('entity_key') or '').strip()
        if not ek or et not in ('wallet', 'tx'):
            return {'message': 'Bad payload'}, 400

        case_type_enum_text = CASE_TYPE_MAP[et]

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
            cols = [
                'case_type', 'reference_id', 'status',
                'severity', 'reason', 'title', 'priority', 'typology',
                'tags', 'tlp', 'visibility', 'sla_due_at', 'payload'
            ]
            vals = [
                case_type_enum_text, ek, 'Under Review',
                sev, p.get('reason'), p.get('title'), pri, p.get('typology'),
                (p.get('tags') or []), tlp, vis, p.get('sla_due_at'),
                Json(p.get('payload') or {})
            ]
            
            sql = """
                INSERT INTO cases (
                    case_type, reference_id, status,
                    severity, reason, title, priority, typology,
                    tags, tlp, visibility, sla_due_at, payload
                )
                VALUES (
                    %s::case_type_enum, %s, %s::case_status_enum,
                    %s::case_severity_enum, %s, %s, %s::case_priority_enum, %s,
                    %s::text[], %s::tlp_enum, %s::visibility_enum, %s::timestamptz, %s::jsonb
                )
                RETURNING id
            """
            try:
                cur.execute(sql, vals)
                case_id = cur.fetchone()[0]
                conn.commit()
            except (pg_errors.InvalidTextRepresentation, pg_errors.UndefinedObject) as e:
                conn.rollback()
                return {'message': 'Invalid enum value', 'detail': str(e).split('\n')[0]}, 400
            
@api.route('/<int:case_id>/comments')
class CaseComments(Resource):
    @jwt_required
    def get(self, case_id: int):
        # izin akses
        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404
        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT c.id,
                    c.case_id,
                    c.user_id,
                    c.body,
                    c.visibility::text AS visibility,
                    c.created_at,
                    u.username
                FROM case_comments c
            LEFT JOIN users u ON u.id = c.user_id
                WHERE c.case_id = %s
            ORDER BY c.created_at DESC
            """, (case_id,))
            comments = cur.fetchall()

            # ambil mentions per comment
            if comments:
                cur.execute("""
                    SELECT m.comment_id, m.user_id, u.username
                    FROM case_comment_mentions m
                LEFT JOIN users u ON u.id = m.user_id
                    WHERE m.comment_id = ANY(%s)
                """, ([c["id"] for c in comments],))
                mention_rows = cur.fetchall()
                by_comment = {}
                for r in mention_rows:
                    by_comment.setdefault(r["comment_id"], []).append(
                        {"user_id": r["user_id"], "username": r["username"]}
                    )
                for c in comments:
                    c["mentions"] = by_comment.get(c["id"], [])
        return comments, 200

    @jwt_required
    def post(self, case_id: int):
        data = request.get_json(silent=True) or {}
        body = (data.get('body') or '').strip()
        visibility = (data.get('visibility') or 'internal').strip().lower()

        if not body:
            return {'message': 'Comment body is required'}, 400

        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404

        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO case_comments (case_id, user_id, body, visibility)
                VALUES (%s, %s, %s, %s::visibility_enum)
                RETURNING id
            """, (case_id, user['id'], body, visibility))
            new_id = cur.fetchone()['id']

            # --- Mention handling ---
            usernames = set(MENTION_RE.findall(body or ""))  # cari @username
            if usernames:
                cur.execute(
                    "SELECT id, username FROM users WHERE username = ANY(%s)",
                    (list(usernames),)
                )
                rows = cur.fetchall()
                for u in rows:
                    cur.execute("""
                        INSERT INTO case_comment_mentions (comment_id, user_id)
                        VALUES (%s, %s)
                        ON CONFLICT (comment_id, user_id) DO NOTHING
                    """, (new_id, u["id"]))
            conn.commit()

        return {'id': new_id, 'message': 'OK'}, 201
    
@api.route('/<int:case_id>/attachments')
class CaseAttachments(Resource):
    @jwt_required
    def get(self, case_id: int):
        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404
        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, filename, content_type, size_bytes, description,
                       tlp::text AS tlp, visibility::text AS visibility,
                       created_at
                  FROM case_attachments
                 WHERE case_id = %s
              ORDER BY created_at DESC
            """, (case_id,))
            rows = cur.fetchall()

        # tambahkan URL unduh
        for r in rows:
            r['download_url'] = f"/api/cases/{case_id}/attachments/{r['id']}/download"
        return rows, 200

    @jwt_required
    def post(self, case_id: int):
        app_cfg = current_app.config
        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404
        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        if 'file' not in request.files:
            return {'message': 'file field is required (multipart/form-data)'}, 400

        f = request.files['file']
        if f.filename == '':
            return {'message': 'Empty filename'}, 400
        if not _allowed_file(app_cfg, f.filename):
            return {'message': 'File type not allowed'}, 415

        orig = secure_filename(f.filename)
        content = f.read()
        size = len(content)
        sha256 = hashlib.sha256(content).hexdigest()
        ext = (orig.rsplit('.', 1)[-1] or '').lower()
        stored = f"{case_id}_{sha256[:16]}.{ext}"

        # simpan ke disk: uploads/cases/<id>/
        case_dir = os.path.join(app_cfg['UPLOAD_DIR'], 'cases', str(case_id))
        os.makedirs(case_dir, exist_ok=True)
        stored_path = os.path.join(case_dir, stored)
        with open(stored_path, 'wb') as out:
            out.write(content)

        description = (request.form.get('description') or '').strip() or None
        tlp = (request.form.get('tlp') or 'GREEN').upper()
        visibility = (request.form.get('visibility') or 'internal').lower()

        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO case_attachments
                    (case_id, user_id, filename, stored_name, content_type, size_bytes, sha256, description,
                     tlp, visibility)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s,
                        %s::tlp_enum, %s::visibility_enum)
                RETURNING id
            """, (case_id, user['id'], orig, stored, f.mimetype, size, sha256, description, tlp, visibility))
            att_id = cur.fetchone()[0]
            conn.commit()

        return {'id': att_id, 'message': 'Uploaded'}, 201
    
@api.route('/<int:case_id>/attachments/<int:att_id>/download')
class AttachmentDownload(Resource):
    @jwt_required
    def get(self, case_id: int, att_id: int):
        app_cfg = current_app.config
        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404
        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT filename, stored_name, content_type
                  FROM case_attachments
                 WHERE id = %s AND case_id = %s
            """, (att_id, case_id))
            row = cur.fetchone()

        if not row:
            return {'message': 'Attachment not found'}, 404

        file_path = os.path.join(app_cfg['UPLOAD_DIR'], 'cases', str(case_id), row['stored_name'])
        if not os.path.exists(file_path):
            return {'message': 'File missing on server'}, 410

        return send_file(file_path, as_attachment=True, download_name=row['filename'],
                         mimetype=row.get('content_type') or 'application/octet-stream')
        