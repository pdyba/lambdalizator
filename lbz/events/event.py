from __future__ import annotations

import json


# TODO: Implement the hash method to stay compatible with pylint requirements
class Event:  # pylint: disable=eq-without-hash
    type: str

    def __init__(self, data: dict, *, event_type: str | None = None) -> None:
        self.data = data
        self.type = event_type or self.type

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Event):
            return self.type == other.type and self.data == other.data
        return False

    def __repr__(self) -> str:
        return f"Event(type='{self.type}', data={self.data})"

    @staticmethod
    def serialize(data: dict) -> str:
        return json.dumps(data, default=str)

    @property
    def serialized_data(self) -> str:
        return self.serialize(self.data)
