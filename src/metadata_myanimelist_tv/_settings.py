from dataclasses import dataclass
from dataclasses_json import (
    dataclass_json,
    Undefined,
    DataClassJsonMixin,
)


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class AddOnSettings(DataClassJsonMixin):
    client_id: str
    preferred_language: str
