from typing import Type, Any

from pythonosc import osc_message_builder
from pythonosc.osc_message_builder import OscMessageBuilder

from duit_osc.adapter.BaseOscMessageAdapter import BaseOscMessageAdapter


class DefaultOscAdapter(BaseOscMessageAdapter):
    def handles_type(self, obj: Any) -> bool:
        return True

    def create_message(self, address: str, value: Any) -> OscMessageBuilder:
        msg = osc_message_builder.OscMessageBuilder(address)
        msg.add_arg(value)
        return msg

    def parse_message(self, data_type: Type, *values: Any) -> Any:
        return data_type(values[0])
