import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property                      

from api.core.base.base_model import BaseTableModel


class File(BaseTableModel):
    __tablename__ = 'files'
    
    file_name = sa.Column(sa.String(255), nullable=False, index=True)
    file_path = sa.Column(sa.String(1000), nullable=False, index=True)
    file_size = sa.Column(sa.Integer)
    model_id = sa.Column(sa.String, nullable=True, index=True)
    model_name = sa.Column(sa.String(255), nullable=False, index=True)
    url = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text)
    content = sa.Column(sa.Text)
    label = sa.Column(sa.String)
