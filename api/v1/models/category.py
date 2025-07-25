import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session, backref

from api.core.base.base_model import BaseTableModel


class Category(BaseTableModel):
    __tablename__ = 'categories'
    
    name = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    slug = sa.Column(sa.String, nullable=True, index=True, unique=True)
    model_type = sa.Column(sa.String, nullable=False, index=True)
   
   
class CategoryAssociation(BaseTableModel):
    __tablename__ = "category_association"
    
    entity_id = sa.Column(sa.String, nullable=False, index=True)
    model_type = sa.Column(sa.String, nullable=False, index=True)
    category_id = sa.Column(sa.String, sa.ForeignKey('categories.id'), nullable=False, index=True)

    category = relationship("Category", backref="category_assoc")
