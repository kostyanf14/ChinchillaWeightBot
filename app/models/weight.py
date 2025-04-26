from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

from app.config import Config

from . import Chinchilla

TABLE = "weights"
ATTRIBUTES = ["chinchilla_id", "time", "weight"]
PREFIXED_ATTRIBUTES = [f'"{TABLE}"."{attr}"' for attr in ATTRIBUTES]
INSERT_SQL = f'INSERT INTO "{TABLE}" ({",".join(ATTRIBUTES)}) VALUES ({",".join(["?"] * len(ATTRIBUTES))})'
UPDATE_SQL = f'UPDATE "{TABLE}" SET {",".join([f"{attr} = ?" for attr in ATTRIBUTES])} WHERE "id" = ?'
FETCH_SQL = f'SELECT "{TABLE}"."id", {",".join(PREFIXED_ATTRIBUTES)} FROM "{TABLE}"'
DEFAULT_ORDER = f'ORDER BY "{TABLE}"."time" ASC'
FETCH_SQL_DEFAULT_ORDER = f'{FETCH_SQL} {DEFAULT_ORDER}'


@dataclass
class Weight:
    id: Optional[int] = None
    chinchilla_id: Optional[int] = None
    time: Optional[int] = None
    weight: Optional[int] = None

    def __attribute_before_type_cast(self, attribute: str) -> Any:
        return getattr(self, attribute)

    def save(self):
        with Config.database.get_connection() as db:
            if self.time is None:
                self.time = int(time.time())
            attrs = [self.__attribute_before_type_cast(attr) for attr in ATTRIBUTES]
            if self.id is None:
                cursor = db.execute(INSERT_SQL, attrs)
                self.id = cursor.lastrowid
            else:
                db.execute(UPDATE_SQL, attrs + [self.id])

    def get_chinchilla(self) -> Chinchilla | None:
        if self.chinchilla_id is None:
            return None
        return Chinchilla.find(self.chinchilla_id)

    def get_time_str(self) -> str | None:
        if self.time is None:
            return None
        return datetime.fromtimestamp(self.time).strftime("%Y-%m-%d %H:%M:%S")

    def destroy(self):
        with Config.database.get_connection() as db:
            db.execute(f'DELETE FROM "{TABLE}" WHERE "id" = ?', (self.id,))

    @staticmethod
    def all() -> List[Weight]:
        cursor = Config.database.execute(FETCH_SQL_DEFAULT_ORDER)
        return [Weight(*values) for values in cursor.fetchall()]

    @staticmethod
    def all_by_chinchilla(chinchilla_id: int) -> List[Weight]:
        cursor = Config.database.execute(
            f'{FETCH_SQL} WHERE "chinchilla_id" = ? {DEFAULT_ORDER}',
            (chinchilla_id,))
        return [Weight(*values) for values in cursor.fetchall()]

    @staticmethod
    def find(weight_id: int) -> Weight:
        row = Config.database.execute(f'{FETCH_SQL} WHERE "id" = ?', (weight_id,)).fetchone()
        if row is None:
            raise ValueError(f'Weight with id {weight_id} not found')
        return Weight(*row)
