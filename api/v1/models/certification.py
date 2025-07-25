import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Certification(BaseTableModel):
    __tablename__ = 'certifications'

    name = sa.Column(sa.String, nullable=False)
    issuer = sa.Column(sa.String, nullable=False)
    issue_date = sa.Column(sa.DateTime, nullable=True)
    credential_id = sa.Column(sa.String, nullable=True)
    credential_url = sa.Column(sa.String, nullable=True)
    issuer_file_id = sa.Column(sa.String, nullable=True)
    
    issuer_image = relationship(
        'File', uselist=False,
        primaryjoin="and_(File.id==foreign(Certification.issuer_file_id), File.is_deleted==False)",
        lazy='selectin'
    )
    
    certification_file = relationship(
        'File', uselist=False,
        primaryjoin="and_(foreign(File.model_id)==Certification.id, File.is_deleted==False)",
        lazy='selectin'
    )
