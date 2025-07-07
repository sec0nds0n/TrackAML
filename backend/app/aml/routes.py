import os
import joblib
import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, abort
from ..database import get_db_connection
from ..services.transaction_service import (
    get_risky_interactions,
    detect_recurring_transactions_raw,
    get_blacklist_interactions,
    detect_repeated_value_transactions,
    detect_large_tx_for_wallet,
    get_hourly_transaction_count,
    get_transactions_from_neo4j,
    get_color,
    get_transitive_risk_graph
)
from ..services.kyc_service import (
    get_wallet_summary,
    check_wallet_in_history,
    get_top_transactions,
    get_top_receivers,
    get_top_senders,
    is_wallet_blacklisted, 
)
from ..services.neo4j_sync import migrate_transactions, label_blacklisted_wallets
from ..services.risk_analysis import calculate_wallet_risk
from flask import (
    Blueprint, render_template, request,
    flash, redirect, url_for, current_app
)

# Load model & scaler sekali saat import
BASE_DIR      = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL_DIR     = os.path.join(BASE_DIR, 'models')
IF_MODEL_PATH = os.path.join(MODEL_DIR, 'isolation_forest_best_model.pkl')
SCALER_PATH   = os.path.join(MODEL_DIR, 'scaler_if.pkl')
if_model  = joblib.load(IF_MODEL_PATH)
if_scaler = joblib.load(SCALER_PATH)

aml_bp = Blueprint('aml', __name__, template_folder='../templates/aml')

@aml_bp.route('/')
def dashboard():
    wallet = request.args.get('wallet', '').strip().lower()

    try:
        nodes, edges = get_graph_data(wallet)
    except Exception:
        nodes, edges = [], []

    # kirim semua variabel ke template
    return render_template(
        'aml/transitive_risk.html',
        wallet=wallet,
        nodes=nodes,
        edges=edges
    )

@aml_bp.route('/sync', methods=['POST'])
def sync():
    migrate_transactions()
    label_blacklisted_wallets()
    calculate_wallet_risk()
    flash("✅ Sinkronisasi database berhasil!", "success")
    return redirect(url_for('aml.dashboard'))

@aml_bp.route('/wallet', methods=['GET', 'POST'])
def wallet():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT address, queried_at FROM wallet_history "
        "ORDER BY queried_at DESC LIMIT 10;"
    )
    wallets = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('aml/wallet.html', wallets=wallets)

@aml_bp.route('/transaction_analysis', methods=['GET'])
def transaction_analysis():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    wallet = request.args.get('wallet', '').strip().lower()
    sort_by = request.args.get('sort_by', 'timestamp')
    order = request.args.get('order', 'desc')
    page = int(request.args.get('page', 1))
    per_page = 10

    valid_columns = ['value', 'timestamp']
    if sort_by not in valid_columns:
        sort_by = 'timestamp'

    order_query = "ASC" if order == "asc" else "DESC"

    conn = get_db_connection()
    cur = conn.cursor()

    # Query transaksi dengan filter pencarian dan pagination
    offset = (page - 1) * per_page
    sql_query = f"""
        SELECT sender, receiver, value, timestamp
        FROM transactions
        {" WHERE sender ILIKE %s OR receiver ILIKE %s" if wallet else ""}
        ORDER BY {sort_by} {order_query}
        LIMIT %s OFFSET %s
    """
    params = (f"%{wallet}%", f"%{wallet}%", per_page, offset) if wallet else (per_page, offset)

    cur.execute(sql_query, params)
    transactions = cur.fetchall()
    
    # Query untuk transaksi anomaly
    anomaly_query = """
        SELECT sender, receiver, value, timestamp
        FROM transactions
        WHERE is_anomaly = TRUE
    """
    # Jika ada wallet, tambahkan kondisi pencarian
    if wallet:
        anomaly_query += " AND (sender ILIKE %s OR receiver ILIKE %s)"

    anomaly_query += " ORDER BY timestamp ASC"
    
    # Tentukan parameter pencarian untuk anomaly
    anomaly_params = (f"%{wallet}%", f"%{wallet}%",) if wallet else ()
    
    cur.execute(anomaly_query, anomaly_params)
    anomaly_transactions = cur.fetchall()
    
    # Hitung total halaman secara lebih optimal
    if wallet:
        cur.execute("SELECT COUNT(*) FROM transactions WHERE sender ILIKE %s OR receiver ILIKE %s",
                    (f"%{wallet}%", f"%{wallet}%"))
    else:
        cur.execute("SELECT COUNT(*) FROM transactions")
    
    total_rows = cur.fetchone()[0]
    total_pages = (total_rows // per_page) + (1 if total_rows % per_page > 0 else 0)

    # Ambil data untuk grafik (hanya jika wallet adalah alamat wallet yang spesifik)
    timestamps, values, point_colors = [], [], []
    if wallet and not ('%' in wallet or '_' in wallet):  # Pastikan ini alamat wallet, bukan wildcard search
        cur.execute("""
            SELECT timestamp, value, is_anomaly
            FROM transactions 
            WHERE sender = %s OR receiver = %s
            ORDER BY timestamp ASC
        """, (wallet, wallet))

        data = cur.fetchall()
        timestamps = [row[0].strftime("%Y-%m-%d %H:%M:%S") for row in data]
        values = [row[1] for row in data]
        
        point_colors = ['red' if row[2] else 'blue' for row in data]

    cur.close()
    conn.close()

    return render_template("transaction_analysis.html",
                           transactions=transactions,
                           wallet=wallet,
                           sort_by=sort_by,
                           order=order,
                           page=page,
                           total_pages=total_pages,
                           timestamps=timestamps,
                           values=values,
                           point_colors=point_colors,
                           anomaly_transactions=anomaly_transactions)
    
@aml_bp.route("/kyc", methods=["GET", "POST"])
def kyc():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    #wallet = request.args.get("wallet") or None
    wallet = request.args.get('wallet', '').strip().lower()
    risk_profile = "Unknown"
    blacklist_interactions = []
    is_blacklisted = None
    top_transactions = []
    top_receivers = []
    top_senders = []
    timestamps = []
    values = []
    sender_hourly_tx_counts = []
    receiver_hourly_tx_counts = []
    risky_interactions = []
    recurring_pattern = []
    wallet_summary = None
    
    wallet_not_found = False

    if request.method == "POST":
        wallet = request.form.get("wallet_address").strip().lower()

    if wallet:
        # Gunakan fungsi dari kyc_service.py
        if not check_wallet_in_history(wallet):
            wallet_not_found = True  # Wallet belum ada di history
        else:
            # Wallet ada di history, lanjutkan analisis
            is_blacklisted = is_wallet_blacklisted(wallet)
            if is_blacklisted:
                risk_profile = f"⚠️ BLACKLISTED ({is_blacklisted['source']}: {is_blacklisted['reason']})"
            else:
                # 🔹 Ambil profil risiko dari database `wallet_risk`
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT risk_profile FROM wallet_risk WHERE address = %s", (wallet,))
                result = cur.fetchone()
                
                if result:
                    risk_profile = result[0]  # Jika ditemukan di database
                else:
                    risk_profile = "Unknown"  # Jika tidak ada di database

                cur.close()
                conn.close()

            wallet_summary = get_wallet_summary(wallet)
            top_transactions = get_top_transactions(wallet)
            top_receivers = get_top_receivers(wallet)
            top_senders = get_top_senders(wallet)
            risky_interactions = get_risky_interactions(wallet)
            recurring_pattern = detect_recurring_transactions_raw(wallet)
            blacklist_interactions = get_blacklist_interactions(wallet)
            sender_hourly_tx_counts, receiver_hourly_tx_counts = get_hourly_transaction_count(wallet)

    return render_template("kyc.html", 
                           receiver_hourly_tx_counts=receiver_hourly_tx_counts,
                           sender_hourly_tx_counts=sender_hourly_tx_counts,
                           risky_interactions=risky_interactions,
                           recurring_pattern=recurring_pattern,
                           wallet=wallet,
                           risk_profile=risk_profile,
                           is_blacklisted=is_blacklisted,
                           blacklist_interactions=blacklist_interactions,
                           wallet_summary=wallet_summary,
                           top_transactions=top_transactions, 
                           top_receivers=top_receivers, 
                           top_senders=top_senders,
                           timestamps=timestamps,
                           values=values,
                           wallet_not_found=wallet_not_found)
    
@aml_bp.route('/fetch_transactions', methods=['POST'])
def fetch_transactions():
    if 'username' not in session:
        return redirect(url_for('login'))

    wallet_address = request.form['wallet']
    force = request.form.get('force_update') == 'yes'

    success, message = fetch_and_analyze_wallet(wallet_address)

    if success:
        flash(f"✅ {message}", "success")
    else:
        flash(f"❌ {message}", "danger")

    return redirect(url_for('wallet'))

@aml_bp.route('/update_all_wallets', methods=['POST'])
def update_all_wallets():
    key = current_app.config.get('ETHERSCAN_API_KEY')
    if not key:
        flash("🔑 Etherscan API key is not set in config!", "danger")
        return redirect(url_for('aml.wallet'))

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT address FROM wallet_history")
    wallets = cur.fetchall()

    success_count = 0
    fail_count = 0

    for (wallet_address,) in wallets:
        try:
            url = (
                "https://api.etherscan.io/api"
                f"?module=account&action=txlist"
                f"&address={wallet_address}"
                f"&sort=asc&apikey={key}"
            )
            response = requests.get(url).json()

            if response.get("status") != "1" or "result" not in response:
                fail_count += 1
                continue

            transactions = response["result"]

            for tx in transactions:
                tx_hash = tx["hash"]
                sender = tx["from"]
                receiver = tx["to"]
                value = int(tx["value"]) / 1e18
                timestamp = tx["timeStamp"]

                cur.execute("""
                    INSERT INTO transactions (tx_hash, sender, receiver, value, timestamp)
                    VALUES (%s, %s, %s, %s, TO_TIMESTAMP(%s))
                    ON CONFLICT (tx_hash) DO NOTHING
                """, (tx_hash, sender, receiver, value, timestamp))

            # update queried_at
            cur.execute("""
                UPDATE wallet_history
                SET queried_at = NOW()
                WHERE address = %s
            """, (wallet_address,))
            conn.commit()
            success_count += 1

        except Exception as e:
            print(f"Error saat update {wallet_address}: {e}")
            fail_count += 1
            conn.rollback()

    cur.close()
    conn.close()

    flash(f"🔄 Selesai update {success_count} wallet. Gagal: {fail_count}", "info")
    return redirect(url_for('aml.wallet'))

@aml_bp.route('/transaction_graph', methods=['GET'])
def transaction_graph():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    wallet = request.args.get('search', '')
    top_10 = request.args.get('top_10', 'false') == 'true'

    limit = 10 if top_10 else 30
    sort_by = "value" if top_10 else "timestamp"
    order = "desc"

    transactions = get_transactions_from_neo4j(
        wallet=wallet, 
        sort_by=sort_by,  
        order=order,      
        limit=limit
    )

    nodes = []
    edges = []
    seen_wallets = set()
    color_legend = {}

    for sender, receiver, value, timestamp in transactions:
        sender_color = get_color(sender)
        receiver_color = get_color(receiver)
        if sender not in seen_wallets:
            nodes.append({"id": sender, "color": sender_color})  
            seen_wallets.add(sender)
            color_legend[sender] = sender_color  

        if receiver not in seen_wallets:
            nodes.append({"id": receiver, "color": receiver_color})  
            seen_wallets.add(receiver)
            color_legend[receiver] = receiver_color  

        edges.append({
            "from": sender, "to": receiver, 
            "label": f"{value} ETH", 
            "timestamp": timestamp
        })

    return render_template("transaction_graph.html", 
                           nodes=nodes, edges=edges, 
                           wallet=wallet, 
                           color_legend=color_legend,  
                           top_10=top_10)
    
@aml_bp.route('/transitive_risk')
def transitive_risk():
    if 'username' not in session:
        return redirect(url_for('auth.login'))

    wallet = request.args.get('search','').strip()
    if not wallet:
        flash("🔍 Masukkan wallet untuk dianalisis.", "warning")
        return redirect(url_for('wallet'))

    # ambil nodes (id,color), edges
    nodes, edges, color_legend = get_transitive_risk_graph(wallet)

    # Beri label angka untuk tiap node kecuali target
    labeled_nodes = []
    legend_map    = {}  # label → address
    for idx, n in enumerate(nodes):
        # jika ini node target, label = address, else label = idx
        if n["id"] == wallet:
            label = n["id"]
        else:
            label = str(idx)
        labeled_nodes.append({
            "id":    n["id"],
            "color": n["color"],
            "label": label
        })
        legend_map[label] = n["id"]

    if len(labeled_nodes) <= 1:
        flash(f"ℹ️ Tidak ada koneksi blacklist ke {wallet}", "info")

    return render_template(
        "transitive_risk.html",
        nodes=labeled_nodes,
        edges=edges,
        wallet=wallet,
        legend_map=legend_map
    )

@aml_bp.route('/advance_analysis', methods=['GET'])
def advance_analysis():
    if 'username' not in session:
        return redirect(url_for('login'))

    wallet = request.args.get("search")
    anomalies = detect_large_tx_for_wallet(wallet)
    sender_hourly_tx_counts, receiver_hourly_tx_counts = get_hourly_transaction_count(wallet)
    risky_interactions = []
    risky_interactions = get_risky_interactions(wallet)
    blacklist_interactions = get_blacklist_interactions(wallet)
    recurring_pattern = detect_recurring_transactions_raw(wallet)
    repeated_value_transactions = detect_repeated_value_transactions(wallet)
    
    return render_template("advance_analysis.html", 
                           anomalies=anomalies, 
                           receiver_hourly_tx_counts=receiver_hourly_tx_counts,
                           sender_hourly_tx_counts=sender_hourly_tx_counts,
                           risky_interactions=risky_interactions,
                           blacklist_interactions=blacklist_interactions,
                           recurring_pattern=recurring_pattern,
                           repeated_value_transactions=repeated_value_transactions,
                           wallet=wallet)
    
@aml_bp.route("/check_darkweb", methods=["GET"])
def check_darkweb():
    wallet = request.args.get("search")
    if not wallet:
        flash("Harap masukkan alamat wallet!", "warning")
        return redirect(url_for("kyc"))  # Redirect jika wallet kosong

    ahmia_results = search_ahmia(wallet)
    dread_results = search_dread(wallet)
    
    return render_template("darkweb_results.html", 
                           wallet=wallet, 
                           ahmia_results=ahmia_results,
                           dread_results=dread_results)