from typing import Type, Any

import vector
from duit.utils import _vector
from pythonosc import osc_message_builder
from pythonosc.osc_message_builder import OscMessageBuilder

from duit_osc.adapter.BaseOscMessageAdapter import BaseOscMessageAdapter


class VectorOscAdapter(BaseOscMessageAdapter):
    def handles_type(self, obj: Any) -> bool:
        return isinstance(obj, vector.Vector)

    def create_message(self, address: str, value: vector.Vector) -> OscMessageBuilder:
        msg = osc_message_builder.OscMessageBuilder(address)

        components = _vector.get_vector_attributes(value)
        for comp in components:
            comp_value = getattr(value, comp)
            msg.add_arg(float(comp_value))

        return msg

    def parse_message(self, data_type: Type, *values: Any) -> Any:
        if issubclass(data_type, vector.Vector2D):
            return vector.obj(x=values[0], y=values[1])
        elif issubclass(data_type, vector.Vector3D):
            return vector.obj(x=values[0], y=values[1], z=values[2])
        elif issubclass(data_type, vector.Vector4D):
            return vector.obj(x=values[0], y=values[1], z=values[2], t=values[3])
        else:
            return None
