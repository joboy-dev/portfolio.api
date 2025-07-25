import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Message(BaseTableModel):
    __tablename__ = 'messages'

    name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False, index=True)
    phone_country_code = sa.Column(sa.String, nullable=True)
    phone_number = sa.Column(sa.String, nullable=True)
    location = sa.Column(sa.String, nullable=True)
    message = sa.Column(sa.Text, nullable=False)
