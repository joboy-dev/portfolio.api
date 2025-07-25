import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session

from api.core.base.base_model import BaseTableModel


class Testimonial(BaseTableModel):
    __tablename__ = 'testimonials'

    name = sa.Column(sa.String, nullable=False)
    title = sa.Column(sa.String, nullable=False)
    rating = sa.Column(sa.Integer, default=1)
    message = sa.Column(sa.Text, nullable=False)
    is_published = sa.Column(sa.Boolean, server_default="false")
