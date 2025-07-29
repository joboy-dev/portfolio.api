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
    features = sa.Column(sa.JSON, nullable=True)
    challenges_and_solutions = sa.Column(sa.JSON, nullable=True)
    results = sa.Column(sa.JSON, nullable=True)
    technical_details = sa.Column(sa.JSON, nullable=True)
    domain = sa.Column(sa.String, nullable=False, index=True)
    project_type = sa.Column(sa.String, nullable=False, index=True)
    role = sa.Column(sa.String, nullable=False, index=True)
    client = sa.Column(sa.String, nullable=True)
    sector = sa.Column(sa.String, nullable=True, index=True)
    start_date = sa.Column(sa.DateTime, nullable=True)
    end_date = sa.Column(sa.DateTime, nullable=True)
    status = sa.Column(sa.String, nullable=True, index=True)
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
