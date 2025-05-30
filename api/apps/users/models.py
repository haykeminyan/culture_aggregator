from datetime import datetime

from piccolo.apps.user.tables import BaseUser
from piccolo.columns import UUID, Timestamp, ForeignKey
from piccolo.table import Table
from piccolo_api.session_auth.tables import SessionsBase

class Sessions(SessionsBase, tablename="sessions"):
    @property
    def has_expired(self):
        return self.expiry_date <= datetime.utcnow()


class AdminUser(BaseUser, tablename='admin_user'):
    pass
