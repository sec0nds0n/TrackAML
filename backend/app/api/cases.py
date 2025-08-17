from flask_restx import Namespace, Resource, fields
from flask import request, g, abort, url_for
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
from ..services.notification_service import create_notification

from io import BytesIO
from datetime import datetime, date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
from reportlab.pdfbase.pdfmetrics import stringWidth

import hashlib, os, re

class CasePDFRenderer:
    """Renderer yang fokus ke layout/visual, meniru gaya UI di frontend."""

    PALETTE = {
        "text": colors.HexColor("#0F172A"),
        "muted": colors.HexColor("#64748B"),
        "border": colors.HexColor("#E2E8F0"),
        "soft": colors.HexColor("#F8FAFC"),
        "primary": colors.HexColor("#111827"),
        "chip_bg": colors.HexColor("#EDF2FF"),
        "chip_fg": colors.HexColor("#1D4ED8"),
        # badge warna (mapping severity/status/TLP)
        "success_bg": colors.HexColor("#DCFCE7"),
        "success_fg": colors.HexColor("#166534"),
        "warn_bg":    colors.HexColor("#FEF9C3"),
        "warn_fg":    colors.HexColor("#854D0E"),
        "danger_bg":  colors.HexColor("#FEE2E2"),
        "danger_fg":  colors.HexColor("#991B1B"),
        "info_bg":    colors.HexColor("#E0F2FE"),
        "info_fg":    colors.HexColor("#075985"),
        # TLP
        "tlp_red":    colors.HexColor("#FCA5A5"),
        "tlp_amber":  colors.HexColor("#FDE68A"),
        "tlp_green":  colors.HexColor("#86EFAC"),
        "tlp_white":  colors.HexColor("#E5E7EB"),
    }

    def __init__(self, case_id: int, generated_at_utc: str):
        self.case_id = case_id
        self.generated_at_utc = generated_at_utc
        self.styles = getSampleStyleSheet()

        # Override / tambah style mirip frontend
        self.styles.add(ParagraphStyle(
            name="H1",
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=self.PALETTE["primary"],
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name="Subtle",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=self.PALETTE["muted"]
        ))
        self.styles.add(ParagraphStyle(
            name="Label",
            fontName="Helvetica-Bold",
            fontSize=9.3,
            leading=12,
            textColor=self.PALETTE["muted"]
        ))
        self.styles.add(ParagraphStyle(
            name="Body",
            fontName="Helvetica",
            fontSize=10.5,
            leading=14,
            textColor=self.PALETTE["text"]
        ))
        self.styles.add(ParagraphStyle(
            name="H2",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=self.PALETTE["primary"],
            spaceBefore=8,
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name="Meta",
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=self.PALETTE["text"]
        ))
        self.styles.add(ParagraphStyle(
            name="SmallMuted",
            fontName="Helvetica",
            fontSize=8.8,
            leading=11,
            textColor=self.PALETTE["muted"]
        ))

    # ---------- util kecil ----------
    def _p(self, txt, style="Body"):
        # Normalisasi ke string
        if txt is None:
            s = "-"
        elif isinstance(txt, (datetime, date)):
            s = txt.isoformat()
        else:
            s = str(txt)

        # Escape mini-HTML ReportLab (agar &, <, > aman)
        s = (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))

        return Paragraph(s, self.styles[style])

    def _badge(self, text, kind="info"):
        # kecil ala <Tag/>: Table 1 sel + padding + rounded illusion
        bg = self.PALETTE["info_bg"]; fg = self.PALETTE["info_fg"]
        if kind == "success": bg, fg = self.PALETTE["success_bg"], self.PALETTE["success_fg"]
        if kind == "warn":    bg, fg = self.PALETTE["warn_bg"],    self.PALETTE["warn_fg"]
        if kind == "danger":  bg, fg = self.PALETTE["danger_bg"],  self.PALETTE["danger_fg"]

        t = Table([[Paragraph(f'<font color="{fg}"><b>{text}</b></font>', self.styles["SmallMuted"])]])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
            ("RIGHTPADDING",(0,0), (-1,-1), 4),
            ("TOPPADDING",  (0,0), (-1,-1), 2),
            ("BOTTOMPADDING",(0,0), (-1,-1), 2),
            ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
            ("BOX",         (0,0), (-1,-1), 0.25, bg),
        ]))
        return t

    def _tlp_badge(self, tlp):
        t = (tlp or "").upper()
        if t == "RED":    return self._badge("RED", "danger")
        if t == "AMBER":  return self._badge("AMBER", "warn")
        if t == "GREEN":  return self._badge("GREEN", "success")
        if t == "WHITE":  return self._badge("WHITE", "info")
        return self._badge(t or "-")

    def _status_badge(self, status):
        s = (status or "").lower()
        if s in ("resolved",):          k="success"
        elif s in ("under review","pending","escalated"): k="warn"
        elif s in ("rejected","dropped"): k="danger"
        else: k="info"
        return self._badge(status or "-", k)

    def _severity_badge(self, sev):
        s = (sev or "").lower()
        if s == "low": k="success"
        elif s in ("medium","moderate"): k="warn"
        elif s in ("high","critical","very high"): k="danger"
        else: k="info"
        return self._badge(sev or "-", k)

    def _keyval_grid(self, pairs, col_widths=(28*mm, 55*mm, 28*mm, 55*mm)):
        """
        pairs: list of (label, flowable/value), disusun 2 kolom (label-value, label-value)
        """
        # jadikan baris 4 kolom
        rows = []
        buf = []
        for i, (k, v) in enumerate(pairs):
            buf.extend([Paragraph(k, self.styles["Label"]), v if hasattr(v, "wrapOn") else self._p(str(v), "Meta")])
            if len(buf) == 4:
                rows.append(buf); buf=[]
        if buf:
            # lengkapi kolom kosong jika ganjil
            while len(buf) < 4: buf.append("")
            rows.append(buf)

        t = Table(rows, colWidths=col_widths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING",(0,0), (-1,-1), 0),
            ("RIGHTPADDING",(0,0), (-1,-1), 8),
        ]))
        return t

    def _table(self, headers, rows, colWidths=None):
        data = [
            [Paragraph(f"<b>{h}</b>", self.styles["SmallMuted"]) for h in headers]
        ] + [[(c if hasattr(c, "wrapOn") else self._p(str(c), "Body")) for c in r] for r in rows]

        t = Table(data, colWidths=colWidths, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), self.PALETTE["soft"]),
            ("TEXTCOLOR", (0,0), (-1,0), self.PALETTE["muted"]),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 9),
            ("LINEBELOW", (0,0), (-1,0), 0.6, self.PALETTE["border"]),
            ("GRID", (0,1), (-1,-1), 0.25, self.PALETTE["border"]),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#FAFAFA")]),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",(0,0), (-1,-1), 6),
            ("RIGHTPADDING",(0,0), (-1,-1), 6),
            ("TOPPADDING",(0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
        ]))
        return t

    # ---------- public ----------
    def build(self, payload: dict) -> BytesIO:
        """
        payload = {
          "case": {...}, "notes":[...], "comments":[...],
          "attachments":[...], "activity":[...]
        }
        """
        c = payload.get("case") or {}
        notes = payload.get("notes") or []
        comments = payload.get("comments") or []
        atts = payload.get("attachments") or []
        acts = payload.get("activity") or []

        buf = BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=16*mm, rightMargin=16*mm,
            topMargin=16*mm, bottomMargin=16*mm
        )

        def footer(canvas, _doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(self.PALETTE["muted"])
            footer_text = f"CASE-{self.case_id}  •  {self.generated_at_utc} UTC  •  Page {_doc.page}"
            canvas.drawRightString(A4[0] - 15*mm, 12*mm, footer_text)
            canvas.restoreState()

        story = []

        # Header (Title)
        title = f"CASE-{self.case_id} — { (c.get('title') or c.get('case_type') or 'Case').title() } { (c.get('reference_id') or '')[:6] }…"
        story.append(Paragraph(title, self.styles["H1"]))
        story.append(Paragraph(f"Generated at {self.generated_at_utc} UTC", self.styles["Subtle"]))
        story.append(Spacer(1, 5))

        story.append(HRFlowable(color=self.PALETTE["border"], thickness=0.6, width="100%"))
        story.append(Spacer(1, 6))

        # Summary grid (meta)
        pairs = [
            ("Status", self._status_badge(c.get("status"))),
            ("Severity", self._severity_badge(c.get("severity") or c.get("risk_level"))),
            ("Priority", self._badge(c.get("priority") or "-", "info")),
            ("TLP", self._tlp_badge(c.get("tlp"))),
            ("Visibility", self._badge((c.get("visibility") or "internal").title(), "info")),
            ("Case Type", self._p((c.get("case_type") or "-").title(), "Meta")),
            ("Reference", self._p(c.get("reference_id") or "-", "Meta")),
            ("Assigned To", self._p(", ".join(c.get("assignees") or [c.get("assigned_to") or c.get("owner_username") or "-"]), "Meta")),
            ("Created At", self._p(c.get("created_at") or "-", "Meta")),
            ("Updated At", self._p(c.get("updated_at") or "-", "Meta")),
            ("SLA Due", self._p(c.get("sla_due_at") or "-", "Meta")),
            ("Tags", self._p(", ".join(c.get("tags") or []) or "-", "Meta")),
        ]
        story.append(self._keyval_grid(pairs))
        story.append(Spacer(1, 8))

        # Description
        story.append(Paragraph("Description", self.styles["H2"]))
        story.append(self._p(c.get("description") or c.get("reason") or "-"))
        story.append(Spacer(1, 8))

        # Notes
        story.append(Paragraph("Notes", self.styles["H2"]))
        if not notes:
            story.append(self._p("—"))
        else:
            for n in notes:
                who = n.get("username") or n.get("user") or "-"
                ts = n.get("created_at") or "-"
                vis = n.get("visibility") or "internal"
                meta = Paragraph(f"<b>{who}</b> • {ts} • <i>{vis}</i>", self.styles["SmallMuted"])
                story.append(KeepTogether([meta, Spacer(1, 2), self._p(n.get("body") or "-"), Spacer(1, 6)]))

        story.append(Spacer(1, 4))

        # Comments
        story.append(Paragraph("Comments", self.styles["H2"]))
        if not comments:
            story.append(self._p("—"))
        else:
            for cm in comments:
                who = cm.get("username") or cm.get("user") or "-"
                ts = cm.get("created_at") or "-"
                vis = cm.get("visibility") or "internal"
                meta = Paragraph(f"<b>{who}</b> • {ts} • <i>{vis}</i>", self.styles["SmallMuted"])
                story.append(KeepTogether([meta, Spacer(1, 2), self._p(cm.get("body") or "-"), Spacer(1, 6)]))

        story.append(Spacer(1, 6))

        # Attachments
        story.append(Paragraph("Attachments", self.styles["H2"]))
        if not atts:
            story.append(self._p("—"))
        else:
            rows = []
            for a in atts:
                rows.append([
                    self._p(a.get("filename") or "-"),
                    self._p(a.get("mime_type") or a.get("content_type") or "-"),
                    self._p(a.get("size_human") or a.get("size") or "-"),
                    self._p(a.get("tlp") or "-"),
                    self._p(a.get("visibility") or "-"),
                    self._p(a.get("created_at") or "-"),
                    self._p(a.get("description") or "-"),
                ])
            story.append(self._table(
                ["Filename", "Type", "Size", "TLP", "Vis.", "Uploaded At", "Description"],
                rows,
                colWidths=[55*mm, 28*mm, 18*mm, 12*mm, 12*mm, 32*mm, None]
            ))

        story.append(Spacer(1, 8))

        # Activity
        story.append(Paragraph("Activity Timeline", self.styles["H2"]))
        if not acts:
            story.append(self._p("—"))
        else:
            act_rows = []
            for r in acts:
                action = r.get("action") or "-"
                who    = r.get("user") or "-"
                ts     = r.get("timestamp") or "-"
                comment= r.get("comment") or ""
                line = Paragraph(f"<b>{action}</b> — <i>{who}</i> • {ts}<br/>{comment}", self.styles["Body"])
                act_rows.append([line])
            story.append(self._table(["Activity"], act_rows, colWidths=[None]))

        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        buf.seek(0)
        return buf

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
    'notes': fields.String,
})

case_update_model = api.model('CaseUpdate', {
    'title': fields.String,
    'description': fields.String,
    'status': fields.String,
    'reason': fields.String,
    'source': fields.String,
    'tags': fields.List(fields.String),
    'severity': fields.String,
    'priority': fields.String,
    'typology': fields.String,
    'tlp': fields.String,
    'visibility': fields.String,
    'sla_due_at': fields.DateTime,
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
                tags=data.get('tags'),
                tlp=norm['tlp'],
                visibility=norm['visibility'],
                sla_due_at=data.get('sla_due_at'),
                owner_id=owner_id,
                payload=data.get('payload') or {},
            )
            initial_note = (data.get('notes') or '').strip()
            if initial_note:
                with get_db_connection() as conn, conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO case_notes (case_id, user_id, body, visibility)
                        VALUES (%s, %s, %s, %s::visibility_enum)
                    """, (case_id, getattr(g, 'user_id', None), initial_note, 'internal'))
                    conn.commit()
                
            creator_role = (getattr(g, 'role', '') or '').lower()
            if creator_role == 'analyst_l1':
                with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # pilih L2 dengan open case paling sedikit
                    cur.execute("""
                        SELECT u.id
                        FROM users u
                        LEFT JOIN case_assignments ca ON ca.user_id = u.id
                        LEFT JOIN cases c ON c.id = ca.case_id
                                            AND lower(c.status::text) NOT IN ('resolved','dropped')
                        WHERE lower(u.role) = 'analyst_l2'
                        GROUP BY u.id
                        ORDER BY COUNT(CASE WHEN c.id IS NOT NULL THEN 1 END) ASC, u.id ASC
                        LIMIT 1
                    """)
                    row = cur.fetchone()
                    if row and row.get('id'):
                        assign_case(case_id, row['id'], replace=False)
                        create_notification(
                            user_id=row['id'],
                            ntype='case_assigned',
                            message=f'You have been assigned to Case #{case_id}',
                            meta={'case_id': case_id}
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
        create_notification(
            user_id=user_id,
            ntype='case_assigned',
            message=f'You have been assigned to Case #{case_id}',
            meta={'case_id': case_id}
        )
        return {'status': 'assigned'}, 200


@api.route('/<int:case_id>')
class CaseDetail(Resource):
    @jwt_required
    def get(self, case_id: int):
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            # case + owner username
            cur.execute("""
                SELECT c.*,
                       u.username AS owner_username
                  FROM cases c
             LEFT JOIN users u ON u.id = c.owner_id
                 WHERE c.id = %s
            """, (case_id,))
            row = cur.fetchone()
            if not row:
                abort(404, description='Case not found')

            # assignments (id, username, role)
            cur.execute("""
                SELECT u.id, u.username, u.role
                  FROM case_assignments ca
                  JOIN users u ON u.id = ca.user_id
                 WHERE ca.case_id = %s
              ORDER BY LOWER(u.username)
            """, (case_id,))
            assigns = cur.fetchall() or []

        base = row_to_case(row)  # keep your existing normalization
        base['owner'] = {
            'id': row.get('owner_id'),
            'username': row.get('owner_username')
        }
        base['assignments'] = assigns
        return base, 200
    
    @api.expect(case_update_model)
    @jwt_required
    def patch(self, case_id: int):
        data = request.get_json(silent=True) or {}

        # normalisasi enum → label di DB (biar aman dari InvalidTextRepresentation)
        def norm(enum_name, key):
            if key in data and data[key] is not None:
                data[key] = enum_canon(enum_name, data[key])

        norm('case_severity_enum', 'severity')
        norm('case_priority_enum', 'priority')
        norm('tlp_enum', 'tlp')
        norm('visibility_enum', 'visibility')
        norm('case_status_enum', 'status')

        # dukung tags berupa string "a, b, c"
        if isinstance(data.get('tags'), str):
            data['tags'] = [s.strip() for s in data['tags'].split(',') if s.strip()]

        # update di service
        update_case(case_id, data)

        return {'message': 'Updated'}, 200

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
                return {'message': 'Created', 'case_id': case_id}, 201
            
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
                SELECT 
                    id,
                    filename,
                    mime_type AS content_type,
                    size_bytes,
                    created_at,
                    url,
                    sha256,
                    user_id
                FROM case_attachments
                WHERE case_id = %s
                ORDER BY created_at DESC
            """, (case_id,))
            rows = cur.fetchall()
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
                    (case_id, user_id, filename, mime_type, size_bytes, sha256, url,
                    description, tlp, visibility)
                VALUES
                    (%s, %s, %s, %s, %s, %s, %s,
                    %s, %s::tlp_enum, %s::visibility_enum)
                RETURNING id
            """, (case_id, user['id'], orig, f.mimetype, size, sha256, stored,
                description, tlp, visibility))
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
                SELECT filename, url, mime_type
                FROM case_attachments
                WHERE id = %s AND case_id = %s
            """, (att_id, case_id))
            row = cur.fetchone()

        if not row:
            return {'message': 'Attachment not found'}, 404

        stored_name = row['url']  # nama file yang kita simpan ke kolom url saat upload
        file_path = os.path.join(app_cfg['UPLOAD_DIR'], 'cases', str(case_id), stored_name)
        if not os.path.exists(file_path):
            return {'message': 'File missing on server'}, 410

        return send_file(
            file_path,
            as_attachment=True,
            download_name=row['filename'],
            mimetype=row.get('mime_type') or 'application/octet-stream'
        )
        
@api.route('/<int:case_id>/activity')
class CaseActivity(Resource):
    @jwt_required
    def get(self, case_id: int):
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                WITH base AS (
                    -- created
                    SELECT 'created'::text AS kind, c.created_at AS at, c.owner_id::int AS user_id,
                           NULL::int AS ref_id, NULL::text AS body, NULL::text AS filename, NULL::text AS visibility
                    FROM cases c WHERE c.id = %s

                    UNION ALL
                    -- comments
                    SELECT 'comment', cm.created_at, cm.user_id::int, cm.id::int,
                           cm.body::text, NULL::text, cm.visibility::text
                    FROM case_comments cm WHERE cm.case_id = %s

                    UNION ALL
                    -- attachments
                    SELECT 'attachment', a.created_at, a.user_id::int, a.id::int,
                           NULL::text, a.filename::text, NULL::text
                    FROM case_attachments a WHERE a.case_id = %s

                    UNION ALL
                    -- assignments
                    SELECT 'assign', ca.assigned_at, ca.user_id::int, ca.id::int,
                           NULL::text, NULL::text, NULL::text
                    FROM case_assignments ca WHERE ca.case_id = %s

                    UNION ALL
                    -- notes (baru)
                    SELECT 'note', n.created_at, n.user_id::int, n.id::int,
                           n.body::text, NULL::text, n.visibility::text
                    FROM case_notes n WHERE n.case_id = %s
                )
                SELECT b.kind, b.at, b.ref_id, b.body, b.filename, b.visibility, u.username
                FROM base b
                LEFT JOIN users u ON u.id = b.user_id
                ORDER BY b.at DESC
            """, (case_id, case_id, case_id, case_id, case_id))
            rows = cur.fetchall()

        out = []
        for r in rows:
            kind = r['kind']
            action = (
                'Case Created' if kind == 'created' else
                'Comment Added' if kind == 'comment' else
                'Document Uploaded' if kind == 'attachment' else
                'Assigned' if kind == 'assign' else
                'Note Added' if kind == 'note' else kind.title()
            )
            at = r['at']
            out.append({
                'id': r['ref_id'] or (f"{kind}-{int(at.timestamp())}" if hasattr(at, "timestamp") else f"{kind}"),
                'action': action,
                'user': r.get('username') or 'System',
                'timestamp': at.isoformat() if hasattr(at, "isoformat") else str(at),
                'comment': r.get('body'),
                'filename': r.get('filename'),
                'kind': kind,
                'visibility': r.get('visibility'),
            })
        return out, 200

@api.route('/<int:case_id>/notes')
class CaseNotes(Resource):
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
                SELECT n.id, n.case_id, n.user_id, n.body,
                       n.visibility::text AS visibility, n.created_at,
                       u.username
                FROM case_notes n
                LEFT JOIN users u ON u.id = n.user_id
                WHERE n.case_id = %s
                ORDER BY n.created_at DESC
            """, (case_id,))
            rows = cur.fetchall()
        return rows, 200

    @jwt_required
    def post(self, case_id: int):
        data = request.get_json(silent=True) or {}
        body = (data.get('body') or '').strip()
        visibility = (data.get('visibility') or 'internal').strip().lower()
        if not body:
            return {'message': 'Note body is required'}, 400

        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404
        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                INSERT INTO case_notes (case_id, user_id, body, visibility)
                VALUES (%s, %s, %s, %s::visibility_enum)
                RETURNING id, created_at
            """, (case_id, user['id'], body, visibility))
            row = cur.fetchone()
            conn.commit()
        return {'id': row['id'], 'created_at': row['created_at'].isoformat()}, 201
    
@api.route('/<int:case_id>/export.pdf')
class CaseExportPdf(Resource):
    @jwt_required
    def get(self, case_id: int):
        # --- 1) Authz & case ---
        case = get_case_with_assignments(case_id)
        if not case:
            return {'message': 'Case not found'}, 404
        user = {'id': getattr(g, 'user_id', None), 'role': getattr(g, 'role', None)}
        if not can_user_see_case(case, user):
            return {'message': 'Forbidden'}, 403

        # --- 2) Kumpulkan data pendukung (naik ASC biar urut kronologis) ---
        with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            # attachments
            cur.execute("""
                SELECT id, filename, url AS stored_name, mime_type, size_bytes, created_at,
                       COALESCE(description,'') AS description,
                       COALESCE(tlp::text,'') AS tlp,
                       COALESCE(visibility::text,'') AS visibility
                FROM case_attachments
                WHERE case_id = %s
                ORDER BY created_at ASC
            """, (case_id,))
            attachments = cur.fetchall() or []
            for a in attachments:
                a['size'] = f"{(a.get('size_bytes') or 0) / 1024 / 1024:.2f} MB"   # renderer support 'size' / 'size_human'

            # comments
            cur.execute("""
                SELECT c.id, c.body, c.created_at, c.visibility::text AS visibility,
                       COALESCE(u.username,'User') AS username
                FROM case_comments c
                LEFT JOIN users u ON u.id = c.user_id
                WHERE c.case_id = %s
                ORDER BY c.created_at ASC
            """, (case_id,))
            comments = cur.fetchall() or []

            # notes
            cur.execute("""
                SELECT n.id, n.body, n.created_at, n.visibility::text AS visibility,
                       COALESCE(u.username,'User') AS username
                FROM case_notes n
                LEFT JOIN users u ON u.id = n.user_id
                WHERE n.case_id = %s
                ORDER BY n.created_at ASC
            """, (case_id,))
            notes = cur.fetchall() or []

            # activity (created, comment, attachment, assign, note)
            cur.execute("""
                WITH base AS (
                    SELECT 'created'::text AS kind, c.created_at AS at, c.owner_id::int AS user_id,
                           NULL::int AS ref_id, NULL::text AS body, NULL::text AS filename, NULL::text AS visibility
                    FROM cases c WHERE c.id = %s
                    UNION ALL
                    SELECT 'comment', cm.created_at, cm.user_id::int, cm.id::int,
                           cm.body::text, NULL::text, cm.visibility::text
                    FROM case_comments cm WHERE cm.case_id = %s
                    UNION ALL
                    SELECT 'attachment', a.created_at, a.user_id::int, a.id::int,
                           NULL::text, a.filename::text, NULL::text
                    FROM case_attachments a WHERE a.case_id = %s
                    UNION ALL
                    SELECT 'assign', ca.assigned_at, ca.user_id::int, ca.id::int,
                           NULL::text, NULL::text, NULL::text
                    FROM case_assignments ca WHERE ca.case_id = %s
                    UNION ALL
                    SELECT 'note', n.created_at, n.user_id::int, n.id::int,
                           n.body::text, NULL::text, n.visibility::text
                    FROM case_notes n WHERE n.case_id = %s
                )
                SELECT b.kind, b.at, b.ref_id, b.body, b.filename, b.visibility, u.username
                FROM base b
                LEFT JOIN users u ON u.id = b.user_id
                ORDER BY b.at ASC
            """, (case_id, case_id, case_id, case_id, case_id))
            act_rows = cur.fetchall() or []

        # --- 3) Normalisasi data ke bentuk yg diminta renderer ---
        assigned_names = [a.get('username') for a in (case.get('assignments') or []) if a.get('username')]
        def _iso(v):
            return v if isinstance(v, str) else (v.isoformat() if v else None)
        case_for_pdf = {
            'id': case['id'],
            'title': case.get('title'),
            'case_type': case.get('case_type'),
            'reference_id': case.get('reference_id'),
            'status': case.get('status'),
            'severity': case.get('severity'),
            'priority': case.get('priority'),
            'typology': case.get('typology'),
            'tlp': case.get('tlp'),
            'visibility': case.get('visibility'),
            'created_at': _iso(case.get('created_at')),
            'updated_at': _iso(case.get('updated_at')),
            'sla_due_at': _iso(case.get('sla_due_at')),
            'tags': case.get('tags') or [],
            'description': case.get('description'),
            'reason': case.get('reason'),
            'source': case.get('source'),
            'assignees': assigned_names,
            'assigned_to': ", ".join(assigned_names) if assigned_names else None,
            'owner_username': case.get('owner_username') or (case.get('owner') or {}).get('username'),
        }

        # mapping activity → format renderer
        action_map = {
            'created': 'Case Created',
            'comment': 'Comment Added',
            'attachment': 'Document Uploaded',
            'assign': 'Assigned',
            'note': 'Note Added',
        }
        activity_for_pdf = [{
            'action': action_map.get(r['kind'], r['kind'].title()),
            'user': r.get('username') or 'System',
            'timestamp': r['at'].isoformat() if hasattr(r['at'], 'isoformat') else str(r['at']),
            'comment': r.get('body') or r.get('filename') or '',
            'kind': r['kind'],
        } for r in act_rows]

        payload = {
            'case': case_for_pdf,
            'notes': notes,
            'comments': comments,
            'attachments': [{
                'filename': a.get('filename'),
                'mime_type': a.get('mime_type'),
                'size': a.get('size'),               # sudah kita isi di atas
                'size_human': a.get('size'),
                'tlp': a.get('tlp'),
                'visibility': a.get('visibility'),
                'created_at': a.get('created_at'),
                'description': a.get('description') or '',
            } for a in attachments],
            'activity': activity_for_pdf,
        }

        # --- 4) Render dengan CasePDFRenderer ---
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        renderer = CasePDFRenderer(case_id, generated_at)
        pdf_buf = renderer.build(payload)

        # --- 5) Kirim file ---
        return send_file(
            pdf_buf,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"CASE-{case_id}.pdf"
        )
