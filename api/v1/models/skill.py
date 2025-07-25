import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Skill(BaseTableModel):
    __tablename__ = 'skills'

    name = sa.Column(sa.String, nullable=False)
    proficiency = sa.Column(sa.Integer)
    file_id = sa.Column(sa.String, nullable=True)
    
    skill_logo = relationship(
        'File', uselist=False,
        primaryjoin="and_(File.id==foreign(Skill.file_id), File.is_deleted==False)",
        lazy='selectin'
    )
