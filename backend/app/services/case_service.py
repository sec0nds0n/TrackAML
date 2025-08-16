from ..database import get_db_connection
import datetime, json
from psycopg2.extras import RealDictCursor, Json

ENUM_MAP = {
  'transaction':'anomaly transaction',
  'wallet':'suspicious wallet'
}

# --- enum normalizer (dinamis dari DB) ---
ENUM_CACHE = {}
def enum_canon(enum_name: str, val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    m = ENUM_CACHE.get(enum_name)
    if m is None:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.enumlabel
            FROM pg_enum e
            JOIN pg_type t ON e.enumtypid = t.oid
            WHERE t.typname = %s
        """, (enum_name,))
        rows = cur.fetchall()
        cur.close(); conn.close()
        m = {r[0].lower(): r[0] for r in rows}
        ENUM_CACHE[enum_name] = m
    return m.get(s.lower())

def list_cases(limit: int = 50) -> list:
    """Get daftar case terbaru, lengkap dengan assignments."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT c.*, 
               COALESCE(json_agg(
                   json_build_object(
                       'user_id', ca.user_id,
                       'assigned_at', ca.assigned_at
                   ) 
               ) FILTER (WHERE ca.user_id IS NOT NULL), '[]') AS assignments
        FROM cases c
        LEFT JOIN case_assignments ca ON ca.case_id = c.id
        GROUP BY c.id
        ORDER BY c.created_at DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def assign_case(case_id: int, user_id: int, *, replace: bool = False):
    """Assign user ke case. 
    Jika replace=True, hapus assignment lain di case tsb (single-owner style).
    Default: tambah/refresh assignment (kolaborasi)."""
    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        if replace:
            cur.execute("DELETE FROM case_assignments WHERE case_id = %s", (case_id,))
        cur.execute("""
            INSERT INTO case_assignments (case_id, user_id, assigned_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (case_id, user_id) 
            DO UPDATE SET assigned_at = EXCLUDED.assigned_at
        """, (case_id, user_id))
        conn.commit()
    
def create_case(case_type_enum_text: str, reference_id: str, **kw) -> int:
    kw = dict(kw)  # jangan ubah argumen caller
    # Normalisasi ke label enum di DB (boleh None → kolom pakai default/nullable)
    if 'severity'   in kw: kw['severity']   = enum_canon('case_severity_enum',   kw.get('severity'))
    if 'priority'   in kw: kw['priority']   = enum_canon('case_priority_enum',   kw.get('priority'))
    if 'tlp'        in kw: kw['tlp']        = enum_canon('tlp_enum',             kw.get('tlp'))
    if 'visibility' in kw: kw['visibility'] = enum_canon('visibility_enum',      kw.get('visibility'))
    
    allowed = {
        'title': ('title', None),
        'priority': ('priority', 'case_priority_enum'),
        'typology': ('typology', None),
        'severity': ('severity', 'case_severity_enum'),
        'reason': ('reason', None),
        'source': ('source', None),
        'description': ('description', None),
        'tags': ('tags', 'text[]'),
        'tlp': ('tlp', 'tlp_enum'),
        'visibility': ('visibility', 'visibility_enum'),
        'sla_due_at': ('sla_due_at', 'timestamptz'),
        'owner_id': ('owner_id', None),
        'payload': ('payload', 'jsonb'),
    }

    cols = ['case_type', 'reference_id', 'status']
    casts = ['case_type_enum', None, 'case_status_enum']
    vals = [case_type_enum_text, reference_id, 'Under Review']

    for key, (col, cast) in allowed.items():
        if key in kw and kw[key] is not None:
            cols.append(col); casts.append(cast)
            vals.append(Json(kw[key]) if cast == 'jsonb' else kw[key])

    placeholders = []
    for cast in casts:
        if cast == 'case_type_enum':
            placeholders.append('%s::case_type_enum')
        elif cast == 'case_status_enum':
            placeholders.append('%s::case_status_enum')
        elif cast == 'case_severity_enum':
            placeholders.append('%s::case_severity_enum')
        elif cast == 'case_priority_enum':
            placeholders.append('%s::case_priority_enum')
        elif cast == 'tlp_enum':
            placeholders.append('%s::tlp_enum')
        elif cast == 'visibility_enum':
            placeholders.append('%s::visibility_enum')
        elif cast == 'timestamptz':
            placeholders.append('%s::timestamptz')
        elif cast == 'jsonb':
            placeholders.append('%s::jsonb')
        elif cast == 'text[]':
            placeholders.append('%s::text[]')
        else:
            placeholders.append('%s')

    sql = f"INSERT INTO cases ({', '.join(cols)}) VALUES ({', '.join(placeholders)}) RETURNING id"

    conn = get_db_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, vals)
            case_id = cur.fetchone()[0]
        return case_id
    finally:
        conn.close()

def update_case(case_id: int, data: dict):
    # field yang diizinkan dan cast-nya (None = text/integer biasa)
    allowed = {
        'title': None,
        'description': None,
        'reason': None,
        'source': None,
        'tags': 'text[]',
        'status': 'case_status_enum',
        'severity': 'case_severity_enum',
        'priority': 'case_priority_enum',
        'typology': None,
        'tlp': 'tlp_enum',
        'visibility': 'visibility_enum',
        'sla_due_at': 'timestamptz',
        'owner_id': None,
        'payload': 'jsonb',
    }

    set_clauses, values = [], []
    for key, cast in allowed.items():
        if key in data:
            if cast:
                set_clauses.append(f"{key} = %s::{cast}")
            else:
                set_clauses.append(f"{key} = %s")
            values.append(data[key])

    if not set_clauses:
        raise ValueError("No valid fields to update")

    values.append(case_id)
    sql = f"""
        UPDATE cases
           SET {', '.join(set_clauses)},
               updated_at = NOW()
         WHERE id = %s
    """

    conn = get_db_connection()
    with conn, conn.cursor() as cur:
        cur.execute(sql, values)
    
def can_user_see_case(case: dict, user: dict) -> bool:
    if not user:
        return False
    if user.get('role') == 'admin':
        return True
    if case.get('owner_id') and case['owner_id'] == user.get('id'):
        return True
    for a in (case.get('assignments') or []):
        if a and a.get('user_id') == user.get('id'):
            return True
    return False

def get_case_with_assignments(case_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT c.*,
               COALESCE(
                 json_agg(
                   json_build_object(
                     'user_id', ca.user_id,
                     'assigned_at', ca.assigned_at,
                     'username', u.username,
                     'role', u.role
                   )
                   ORDER BY ca.assigned_at DESC
                 ) FILTER (WHERE ca.user_id IS NOT NULL),
                 '[]'::json
               ) AS assignments
        FROM cases c
        LEFT JOIN case_assignments ca ON ca.case_id = c.id
        LEFT JOIN users u ON u.id = ca.user_id
        WHERE c.id = %s
        GROUP BY c.id
    """, (case_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row

def get_active_case_count():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM cases
        WHERE status IS NOT NULL
            AND status NOT IN ('Resolved'::case_status_enum, 'Dropped'::case_status_enum);
    """)
    count = cur.fetchone()[0] or 0
    cur.close()
    conn.close()
    return {"count": int(count)}

def get_urgent_case_count():
    """
    Active cases dengan severity High/Critical.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*)
        FROM cases
        WHERE (status IS NULL OR LOWER(status::text) NOT IN ('resolved','dropped'))
          AND severity IS NOT NULL
          AND LOWER(severity::text) IN ('high','critical');
    """)
    count = cur.fetchone()[0] or 0
    cur.close(); conn.close()
    return {"count": int(count)}

def get_recent_cases(limit: int = 10):
    """
    Ambil kasus terbaru (exclude Dropped/Resolved), urut desc by created_at.
    Mengembalikan field minimal untuk tabel dashboard.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            id,
            case_type::text,
            reference_id,
            status::text,
            COALESCE(severity::text, '') AS severity,
            created_at,
            payload
        FROM cases
        WHERE lower(status::text) NOT IN ('dropped','resolved')
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()
    results = []
    for (cid, case_type, ref, status, severity, created_at, payload) in rows:
        # payload bisa dict atau string tergantung driver
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except Exception:
                payload = {}
        payload = payload or {}

        chain  = payload.get('chain') or ('ETH' if str(ref).startswith('0x') else None)
        amount = payload.get('amount') or payload.get('value')  # fallback key lain

        results.append({
            "id": cid,
            "case_type": case_type,
            "reference_id": ref,
            "status": status,
            "severity": severity or None,
            "created_at": created_at.isoformat(),
            "payload": {
                "chain": chain,
                "amount": amount
            }
        })

    cur.close()
    conn.close()
    return results

def list_case_comments(case_id: int) -> list:
    with get_db_connection() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT c.id, c.case_id, c.user_id, c.body,
                   c.visibility::text AS visibility, c.created_at
              FROM case_comments c
             WHERE c.case_id = %s
             ORDER BY c.created_at DESC
        """, (case_id,))
        return cur.fetchall()

def add_case_comment(case_id: int, user_id: int, body: str, visibility: str = 'internal') -> int:
    # Normalisasi visibility, hanya izinkan enum yang berlaku
    vis = (visibility or 'internal').lower()
    if vis not in ('internal', 'external'):
        vis = 'internal'
    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO case_comments (case_id, user_id, body, visibility)
            VALUES (%s, %s, %s, %s::visibility_enum)
            RETURNING id
        """, (case_id, user_id, body, vis))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id