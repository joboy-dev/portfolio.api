import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Award(BaseTableModel):
    __tablename__ = 'awards'
    
    name = sa.Column(sa.String, nullable=False)
    issuer = sa.Column(sa.String, nullable=False)
    issue_date = sa.Column(sa.DateTime, nullable=True)
    file_id = sa.Column(sa.String, nullable=True)
    
    issuer_image = relationship(
        'File', uselist=False,
        primaryjoin="and_(File.id==foreign(Award.file_id), File.is_deleted==False)",
        lazy='selectin'
    )
