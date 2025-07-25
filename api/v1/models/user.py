import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class User(BaseTableModel):
    __tablename__ = 'users'
    
    email = sa.Column(sa.String, unique=True, index=True)
    password = sa.Column(sa.String, nullable=True)
    is_active = sa.Column(sa.Boolean, server_default='true')
    is_superuser = sa.Column(sa.Boolean, server_default='false')
    last_login = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    
    def to_dict(self, excludes = ...):
        return super().to_dict(excludes=['password', 'is_superuser'])
