import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Service(BaseTableModel):
    __tablename__ = 'services'

    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text)
    skills = sa.Column(sa.JSON)
    file_id = sa.Column(sa.String, nullable=True)
    
    service_logo = relationship(
        'File', uselist=False,
        primaryjoin="and_(File.id==foreign(Service.file_id), File.is_deleted==False)",
        lazy='selectin'
    )
