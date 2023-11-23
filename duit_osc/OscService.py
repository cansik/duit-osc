from functools import partial
from typing import TypeVar, Generic, Optional, List, Any, Type

from duit.annotation.AnnotationFinder import AnnotationFinder
from duit.model.DataField import DataField
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

from duit_osc.OscDirection import OscDirection
from duit_osc.OscEndpoint import OscEndpoint
from duit_osc.adapter.BaseOscMessageAdapter import BaseOscMessageAdapter
from duit_osc.adapter.DefaultOscAdapter import DefaultOscAdapter
from duit_osc.adapter.EnumOscAdapter import EnumOscAdapter

T = TypeVar('T')


class OscService(Generic[T]):
    def __init__(self, host: str = "0.0.0.0",
                 in_port: Optional[int] = 8000,
                 out_port: Optional[int] = 9000,
                 allow_broadcast: bool = True):
        self.host = host
        self.in_port = in_port
        self.out_port = out_port
        self.allow_broadcast = allow_broadcast

        self.server_poll_interval: float = 0.01

        # osc internals
        self.osc_server: Optional[ThreadingOSCUDPServer] = None
        self.osc_client: Optional[SimpleUDPClient] = None
        self.dispatcher = Dispatcher()

        # serialization
        self.default_adapter: BaseOscMessageAdapter = DefaultOscAdapter()
        self.adapters: List[BaseOscMessageAdapter] = [
            EnumOscAdapter()
        ]

    def add_route(self, name: str, model: T):

        # find endpoints
        finder: AnnotationFinder[OscEndpoint] = AnnotationFinder(OscEndpoint)

        for field_name, (data_field, annotation) in finder.find(model).items():
            if annotation.name is not None:
                field_name = annotation.name

            # create address
            field_address = self._create_address(name, field_name)

            self.add_datafield_endpoint(field_address, data_field, annotation)

    def add_datafield_endpoint(self, address: str, field: DataField, annotation: OscEndpoint):
        adapter = self._get_matching_adapter(field)

        if annotation.direction == OscDirection.Send or annotation.direction == OscDirection.Both:
            self._add_send_handler(address, field, annotation, adapter)

        if annotation.direction == OscDirection.Receive or annotation.direction == OscDirection.Both:
            self._add_receive_handler(address, field, annotation, adapter)

    def _add_send_handler(self, address: str, field: DataField,
                          annotation: OscEndpoint, adapter: BaseOscMessageAdapter):

        def _send_handler(f: DataField, _: Any):
            if self.osc_client is None:
                return

            msg = adapter.create_message(address, f.value)
            self.osc_client.send(msg.build())

        field.on_changed += partial(_send_handler, field)

    def _add_receive_handler(self, address: str, field: DataField,
                             annotation: OscEndpoint, adapter: BaseOscMessageAdapter):
        data_type = type(field.value)

        def _receive_handler(f: DataField, t: Type, adr: str, *values: Any):
            data = adapter.parse_message(t, *values)
            f.value = data

        self.dispatcher.map(address, partial(_receive_handler, field, data_type))

    def run(self, blocking: bool = True):
        if self.out_port is not None:
            self.osc_client = SimpleUDPClient(self.host, self.out_port, allow_broadcast=self.allow_broadcast)

        if self.in_port is not None:
            self.osc_server = ThreadingOSCUDPServer((self.host, self.in_port), self.dispatcher)

            if blocking:
                self.osc_server.serve_forever(poll_interval=self.server_poll_interval)

    def stop(self):
        if self.osc_server is not None:
            self.osc_server.shutdown()

    def _get_matching_adapter(self, field: DataField) -> BaseOscMessageAdapter:
        for adapter in self.adapters:
            if adapter.handles_type(field.value):
                return adapter
        return self.default_adapter

    @staticmethod
    def _create_address(*segments: str) -> str:
        url = "/".join(s.strip("/") for s in segments)
        return f"/{url}"
