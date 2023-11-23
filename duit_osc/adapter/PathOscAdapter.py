from pathlib import Path
from typing import Type, Any

from pythonosc import osc_message_builder
from pythonosc.osc_message_builder import OscMessageBuilder

from duit_osc.adapter.BaseOscMessageAdapter import BaseOscMessageAdapter


class PathOscAdapter(BaseOscMessageAdapter):
    def handles_type(self, obj: Any) -> bool:
        return isinstance(obj, Path)

    def create_message(self, address: str, value: Path) -> OscMessageBuilder:
        msg = osc_message_builder.OscMessageBuilder(address)
        msg.add_arg(str(value))
        return msg

    def parse_message(self, data_type: Type[Path], *values: Any) -> Any:
        return Path(values[0])
