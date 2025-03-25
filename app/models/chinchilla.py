from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, List, Optional

from app.config import Config


TABLE = "chinchillas"
ATTRIBUTES = ["name"]
PREFIXED_ATTRIBUTES = [f'"{TABLE}"."{attr}"' for attr in ATTRIBUTES]
INSERT_SQL = f'INSERT INTO "{TABLE}" ({",".join(ATTRIBUTES)}) VALUES ({",".join(["?"] * len(ATTRIBUTES))})'
UPDATE_SQL = f'UPDATE "{TABLE}" SET {",".join([f"{attr} = ?" for attr in ATTRIBUTES])} WHERE "id" = ?'
FETCH_SQL = f'SELECT "{TABLE}"."id", {",".join(PREFIXED_ATTRIBUTES)} FROM "{TABLE}"'

logger = logging.getLogger(__name__)


@dataclass
class Chinchilla:
    id: Optional[int] = None
    name: Optional[str] = None

    def __attribute_before_type_cast(self, attribute: str) -> Any:
        return getattr(self, attribute)

    def save(self):
        with Config.database.get_connection() as db:
            attrs = [self.__attribute_before_type_cast(attr) for attr in ATTRIBUTES]
            if self.id is None:
                cursor = db.execute(INSERT_SQL, attrs)
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, attrs + [self.id])

    def destroy(self):
        with Config.database.get_connection() as db:
            db.execute(f'DELETE FROM "{TABLE}" WHERE "id" = ?', (self.id,))

    @staticmethod
    def all() -> List[Chinchilla]:
        cursor = Config.database.execute(FETCH_SQL)
        return [Chinchilla(*values) for values in cursor.fetchall()]

    @staticmethod
    def find(chinchilla_id: int) -> Chinchilla:
        row = Config.database.execute(f'{FETCH_SQL} WHERE "id" = ?', (chinchilla_id,)).fetchone()
        if row is None:
            raise ValueError(f'Chinchilla with id {chinchilla_id} not found')
        return Chinchilla(*row)
