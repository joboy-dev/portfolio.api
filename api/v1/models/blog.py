import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Blog(BaseTableModel):
    __tablename__ = 'blogs'


    tags = relationship(
        "Tag",
        secondary='tag_association',
        primaryjoin="and_(Blog.id==foreign(TagAssociation.entity_id), "
                   "TagAssociation.model_type=='blogs', "
                   "TagAssociation.is_deleted==False)",
        secondaryjoin="and_(Tag.id==foreign(TagAssociation.tag_id), "
                     "Tag.is_deleted==False)",
        backref="blogs",
        lazy='selectin',
        viewonly=True
    )
    
    categories = relationship(
        'Category',
        secondary='category_association',
        primaryjoin='and_(foreign(CategoryAssociation.entity_id)==Blog.id, '
                   'CategoryAssociation.is_deleted==False, '
                   'CategoryAssociation.model_type=="blogs")',
        secondaryjoin='and_(Category.id==foreign(CategoryAssociation.category_id), '
                     'Category.is_deleted==False)',
        lazy='selectin',
        backref='blogs',
        viewonly=True
    )