"""仓储基类：通用 CRUD，减少各实体的样板代码。"""

from typing import Generic, Optional, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, session: Session, model: type[ModelT]):
        self._session = session
        self._model = model

    def add(self, obj: ModelT) -> ModelT:
        self._session.add(obj)
        return obj

    def get(self, obj_id: int) -> Optional[ModelT]:
        return self._session.get(self._model, obj_id)

    def list(self, *, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        stmt = select(self._model).order_by(self._model.id).limit(limit).offset(offset)
        return self._session.scalars(stmt).all()
