from flask_restx import Namespace, Resource, fields
from flask import request, g
from ..utils import jwt_required, jwt_roles_required
from ..services.notification_service import list_notifications, mark_all_read

api = Namespace('notifications', description='User notifications')

notif_model = api.model('Notification', {
    'id':        fields.Integer,
    'type':      fields.String,
    'message':   fields.String,
    'meta':      fields.Raw,
    'is_read':   fields.Boolean,
    'created_at': fields.DateTime
})

@api.route('')
class NotificationsResource(Resource):
    @api.marshal_list_with(notif_model)
    @jwt_required   # ganti login_required
    def get(self):
        unread = request.args.get('unread') in ('1', 'true', 'yes')
        limit = int(request.args.get('limit', 20))

        user_id = getattr(g, 'user_id', None)
        if not user_id:
            return {'message': 'Unauthorized'}, 401

        return list_notifications(user_id, unread_only=unread, limit=limit)

    @jwt_required
    def post(self):
        action = (request.json or {}).get('action')
        user_id = getattr(g, 'user_id', None)
        if not user_id:
            return {'message': 'Unauthorized'}, 401

        if action == 'mark_all_read':
            mark_all_read(user_id)
            return {'ok': True}
        return {'message': 'Unknown action'}, 400