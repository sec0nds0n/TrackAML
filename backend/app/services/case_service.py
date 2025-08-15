from ..database import get_db_connection
import datetime, json
from psycopg2.extras import RealDictCursor

ENUM_MAP = {
  'transaction':'anomaly transaction',
  'wallet':'suspicious wallet'
}

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

def assign_case(case_id: int, user_id: int):
    """Assign case ke user tertentu."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM case_assignments WHERE case_id = %s", (case_id,))
    cur.execute("""
        INSERT INTO case_assignments (case_id, user_id, assigned_at)
        VALUES (%s, %s, NOW())
    """, (case_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
    
def create_case(case_type_in, reference_id, severity='medium'):
    # case_type_in bisa 'wallet'/'transaction' atau enum final
    mapped = CASE_TYPE_MAP.get(case_type_in, case_type_in)
    if mapped not in ('suspicious wallet', 'anomaly transaction'):
        raise ValueError('Invalid case_type')

    with get_db_connection() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO cases (case_type, reference_id, status, severity, created_at)
            VALUES (%s::case_type_enum, %s, 'Under Review', %s, NOW())
            RETURNING id
        """, (mapped, reference_id, severity))
        cid = cur.fetchone()[0]
        conn.commit()
        return cid

def update_case(case_id, data: dict):
    allowed_fields = ['description', 'status', 'reason', 'source', 'tags']
    updates = {}
    values = []

    for field in allowed_fields:
        if field in data:
            updates[field] = data[field]

    if not updates:
        raise ValueError("No valid fields to update")

    set_clauses = []
    for field in updates:
        set_clauses.append(f"{field} = %s")
        values.append(updates[field])

    values.append(case_id)

    sql = f"""
        UPDATE cases
        SET {', '.join(set_clauses)},
            updated_at = NOW()
        WHERE id = %s
    """

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, values)
    conn.commit()
    cur.close()
    conn.close()
    
def can_user_see_case(case, user):
    if user['role'] == 'admin':
        return True
    if 'assignments' not in case:
        return False

    # Ambil role dari user yang ditugaskan
    assigned_roles = [a['role'] for a in case['assignments'] if 'role' in a]

    return user['role'] in assigned_roles

def get_case_with_assignments(case_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT c.*, 
               json_agg(json_build_object(
                  'user_id', ca.user_id,
                  'assigned_at', ca.assigned_at
               )) AS assignments
        FROM cases c
        LEFT JOIN case_assignments ca ON ca.case_id = c.id
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
        WHERE status::text NOT IN ('Dropped','Resolved')
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