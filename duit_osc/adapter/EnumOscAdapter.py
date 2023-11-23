from enum import Enum, EnumMeta
from typing import Any

from pythonosc import osc_message_builder
from pythonosc.osc_message_builder import OscMessageBuilder

from duit_osc.adapter.BaseOscMessageAdapter import BaseOscMessageAdapter


class EnumOscAdapter(BaseOscMessageAdapter):
    def handles_type(self, obj: Any) -> bool:
        return isinstance(obj, Enum)

    def create_message(self, address: str, value: Enum) -> OscMessageBuilder:
        msg = osc_message_builder.OscMessageBuilder(address)
        msg.add_arg(value.name)
        return msg

    def parse_message(self, data_type: EnumMeta, *values: Any) -> Any:
        options = {o.name: o for o in list(data_type)}
        return options[values[0]]
