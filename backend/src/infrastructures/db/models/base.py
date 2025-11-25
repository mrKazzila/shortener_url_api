from typing import Annotated

from sqlalchemy import MetaData, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        },
    )

    type_annotation_map = {Annotated[str, 256]: String(256)}

    repr_max_columns_number = 3
    repr_add_cols = ()

    def __repr__(self) -> str:
        """Pretty model logs."""
        cols = []

        for id_, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_add_cols or id_ < self.repr_max_columns_number:
                cols.append(f"{col}={getattr(self, col)}")

        return f"\n<Model {self.__class__.__name__}: {', '.join(cols)}>\n"
