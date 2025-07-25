import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Project(BaseTableModel):
    __tablename__ = 'projects'

    name = sa.Column(sa.String, nullable=False)
    tagline = sa.Column(sa.String, nullable=True)
    slug = sa.Column(sa.String, nullable=False, index=True, unique=True)
    description = sa.Column(sa.Text)
    tools = sa.Column(sa.JSON)
    domain = sa.Column(sa.String, nullable=False)
    project_type = sa.Column(sa.String, nullable=False)
    role = sa.Column(sa.String, nullable=False)
    client = sa.Column(sa.String, nullable=True)
    github_link = sa.Column(sa.String, nullable=True)
    postman_link = sa.Column(sa.String, nullable=True)
    live_link = sa.Column(sa.String, nullable=True)
    google_drive_link = sa.Column(sa.String, nullable=True)
    figma_link = sa.Column(sa.String, nullable=True)
    
    files = relationship(
        'File',
        primaryjoin="and_(foreign(File.model_id)==Project.id, File.is_deleted==False)",
        lazy='selectin'
    )
    
    tags = relationship(
        "Tag",
        secondary='tag_association',
        primaryjoin="and_(Project.id==foreign(TagAssociation.entity_id), "
                   "TagAssociation.model_type=='projects', "
                   "TagAssociation.is_deleted==False)",
        secondaryjoin="and_(Tag.id==foreign(TagAssociation.tag_id), "
                     "Tag.is_deleted==False)",
        backref="projects",
        lazy='selectin',
        viewonly=True
    )
