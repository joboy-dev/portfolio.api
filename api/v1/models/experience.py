import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Experience(BaseTableModel):
    __tablename__ = 'experiences'

    company = sa.Column(sa.String, nullable=False)
    location = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False)
    start_date = sa.Column(sa.DateTime, nullable=False)
    end_date = sa.Column(sa.DateTime, nullable=True)
    file_id = sa.Column(sa.String, nullable=True)
    description = sa.Column(sa.Text, nullable=True)
    
    company_logo = relationship(
        'File', uselist=False,
        primaryjoin="and_(File.id==foreign(Experience.file_id), File.is_deleted==False)",
        lazy='selectin'
    )
