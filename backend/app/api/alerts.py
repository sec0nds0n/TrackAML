from flask_restx import Namespace, Resource
from flask import request, current_app
from ..database import get_db_connection

api = Namespace('alerts', description='Unified AML alerts')

@api.route('')
class Alerts(Resource):
    def get(self):
        limit = request.args.get('limit', default=50, type=int)

        sql = """
        SELECT * FROM (
            -- 1) wallet_risk -> map ke severity & teks sendiri
            SELECT
                ('wr_' || address)                         AS id,
                CASE
                  WHEN LOWER(TRIM(COALESCE(risk_profile,''))) = 'critical'      THEN 'critical'
                  WHEN LOWER(TRIM(COALESCE(risk_profile,''))) IN ('high','high risk') THEN 'high'
                  ELSE 'medium'
                END                                         AS type,
                ('Wallet flagged: ' || COALESCE(risk_profile,'Unknown')) AS title,
                ('Address ' || address || ' flagged as ' ||
                 COALESCE(risk_profile,'Unknown'))          AS description,
                last_updated                                 AS ts,
                'ETH'                                        AS crypto,            -- default (belum ada kolom chain)
                NULL::text                                   AS amount,
                COALESCE(risk_score, 0)::int                 AS severity,          -- 0..100 kalau nilai kamu memang skala itu
                ARRAY['wallet-risk']::text[]                 AS tags
            FROM wallet_risk
            WHERE COALESCE(risk_profile,'') <> ''

            UNION ALL

            -- 2) blacklist_addresses -> selalu critical
            SELECT
                ('bl_' || address)                           AS id,
                'critical'                                   AS type,
                'Blacklisted address detected'               AS title,
                COALESCE('['||COALESCE(category,'unknown')||'] '||reason,
                         'Address is on blacklist')          AS description,
                added_on                                     AS ts,
                'ETH'                                        AS crypto,
                NULL::text                                   AS amount,
                95                                           AS severity,          -- fixed near-critical
                ARRAY['blacklist']::text[]                   AS tags
            FROM blacklist_addresses
        ) t
        ORDER BY ts DESC
        LIMIT %s;
        """

        conn = get_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, (limit,))
                rows = cur.fetchall()

            # mapping hasil ke JSON yang ramah frontend
            results = []
            for (id_, typ, title, desc, ts, crypto, amount, severity, tags) in rows:
                results.append({
                    "id": id_,
                    "type": typ,                # 'critical' | 'high' | 'medium'
                    "title": title,
                    "description": desc,
                    "timestamp": ts.isoformat() if ts else None,
                    "crypto": crypto,
                    "amount": amount,
                    "severity": int(severity) if severity is not None else None,
                    "source": "wallet_risk" if id_.startswith("wr_") else "blacklist",
                    "tags": tags or []
                })
            return results, 200
        except Exception:
            current_app.logger.exception("Failed to fetch alerts")
            return [], 200 
        finally:
            conn.close()