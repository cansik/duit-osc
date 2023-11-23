import logging
from dataclasses import dataclass
from functools import partial
from typing import TypeVar, Generic, Optional, List, Any, Type, Dict

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
from duit_osc.adapter.PathOscAdapter import PathOscAdapter
from duit_osc.adapter.VectorOscAdapter import VectorOscAdapter

T = TypeVar('T')


@dataclass
class OscRegistration:
    address: str
    field: DataField
    annotation: OscEndpoint
    silent: bool = False

    def __str__(self) -> str:
        return f"{self.address} ({self.annotation.direction.name}): {type(self.field.value).__name__}"

    def __repr__(self) -> str:
        return self.__str__()


class OscService(Generic[T]):
    def __init__(self, host: str = "0.0.0.0",
                 in_port: Optional[int] = 8000,
                 out_port: Optional[int] = 9000,
                 allow_broadcast: bool = True,
                 send_on_receive: bool = False):
        self.host = host
        self.in_port = in_port
        self.out_port = out_port
        self.allow_broadcast = allow_broadcast

        self.send_on_receive = send_on_receive

        self.server_poll_interval: float = 0.01

        self.endpoint_registry: Dict[str, OscRegistration] = dict()

        # osc internals
        self.osc_server: Optional[ThreadingOSCUDPServer] = None
        self.osc_client: Optional[SimpleUDPClient] = None
        self.dispatcher = Dispatcher()

        # serialization
        self.default_adapter: BaseOscMessageAdapter = DefaultOscAdapter()
        self.adapters: List[BaseOscMessageAdapter] = [
            EnumOscAdapter(),
            PathOscAdapter(),
            VectorOscAdapter()
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

        self.endpoint_registry[address] = OscRegistration(address, field, annotation)

    def _add_send_handler(self, address: str, field: DataField,
                          annotation: OscEndpoint, adapter: BaseOscMessageAdapter):

        def _send_handler(f: DataField, _: Any):
            if self.osc_client is None:
                return

            registration = self.endpoint_registry[address]
            if registration.silent:
                return

            msg = adapter.create_message(address, f.value)
            self.osc_client.send(msg.build())

        field.on_changed += partial(_send_handler, field)

    def _add_receive_handler(self, address: str, field: DataField,
                             annotation: OscEndpoint, adapter: BaseOscMessageAdapter):
        data_type = type(field.value)

        def _receive_handler(f: DataField, t: Type, adr: str, *values: Any):
            data = adapter.parse_message(t, *values)

            registration = self.endpoint_registry[address]
            if not self.send_on_receive:
                registration.silent = True
            f.value = data
            registration.silent = False

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

    def api_description(self) -> str:
        logging.warning("This method (api_description) is not meant for production and will change in future releases.")
        text = "\n".join([str(r) for r in self.endpoint_registry.values()])
        return text

    def _get_matching_adapter(self, field: DataField) -> BaseOscMessageAdapter:
        for adapter in self.adapters:
            if adapter.handles_type(field.value):
                return adapter
        return self.default_adapter

    @staticmethod
    def _create_address(*segments: str) -> str:
        url = "/".join(s.strip("/") for s in segments)
        return f"/{url}"
