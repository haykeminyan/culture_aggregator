from piccolo.apps.user.tables import BaseUser
from piccolo.columns import UUID, Timestamp, ForeignKey
from piccolo.table import Table
from piccolo_api.session_auth.tables import SessionsBase

class Sessions(SessionsBase, tablename="sessions"):
    pass


class AdminUser(BaseUser, tablename='admin_user'):
    pass
