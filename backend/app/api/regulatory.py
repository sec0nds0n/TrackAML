from flask_restx import Namespace, Resource, fields

api = Namespace('regulatory', description='Regulatory updates (static curated, for now)')

update_model = api.model('RegulatoryUpdate', {
    'id':         fields.String,
    'title':      fields.String,
    'issuer':     fields.String,      # Bappebti, BI, OJK, PPATK, etc.
    'jurisdiction': fields.String,    # Indonesia
    'status':     fields.String,      # IN_EFFECT | UPDATED | LIVE | REVIEWED
    'summary':    fields.String,
    'tag':        fields.String,      # e.g., "Bappebti"
    'time_ago':   fields.String,      # "2 hours ago"
    'link':       fields.String,      # URL resmi (portal JDIH/siaran pers)
})

# Kurasi INDONESIA (statis dulu)
UPDATES_ID = [
    {
        "id": "id-1",
        "title": "Pedoman Perdagangan Pasar Fisik Aset Kripto",
        "issuer": "Bappebti",
        "jurisdiction": "Indonesia",
        "status": "IN_EFFECT",
        "summary": "Persyaratan pendaftaran pedagang aset kripto, kewajiban KYC/AML, pencatatan & pelaporan transaksi.",
        "tag": "Bappebti",
        "time_ago": "2 hours ago",
        "link": "https://jdih.bappebti.go.id/"  # halaman JDIH Bappebti
    },
    {
        "id": "id-2",
        "title": "Daftar Aset Kripto yang Diperdagangkan (Whitelist)",
        "issuer": "Bappebti",
        "jurisdiction": "Indonesia",
        "status": "UPDATED",
        "summary": "Hanya aset dalam whitelist yang boleh diperdagangkan; ada mekanisme evaluasi & delisting periodik.",
        "tag": "Bappebti",
        "time_ago": "1 day ago",
        "link": "https://jdih.bappebti.go.id/"
    },
    {
        "id": "id-3",
        "title": "Bursa Kripto, Lembaga Kliring & Kustodian Domestik",
        "issuer": "Bappebti",
        "jurisdiction": "Indonesia",
        "status": "LIVE",
        "summary": "Perdagangan melalui bursa kripto lokal dengan kliring & penyimpanan terpusat untuk perlindungan nasabah.",
        "tag": "Bappebti",
        "time_ago": "3 days ago",
        "link": "https://jdih.bappebti.go.id/"
    },
    {
        "id": "id-4",
        "title": "Larangan Kripto sebagai Alat Pembayaran",
        "issuer": "Bank Indonesia",
        "jurisdiction": "Indonesia",
        "status": "IN_EFFECT",
        "summary": "Aset kripto bukan alat pembayaran yang sah; pembatasan pada penggunaan pembayaran di sistem pembayaran.",
        "tag": "BI",
        "time_ago": "1 week ago",
        "link": "https://jdih.bi.go.id/"   # portal JDIH BI
    }
]

@api.route('/updates')
class RegulatoryUpdates(Resource):
    @api.marshal_list_with(update_model)
    def get(self):
        return UPDATES_ID, 200
