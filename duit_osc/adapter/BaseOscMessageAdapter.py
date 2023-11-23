from abc import ABC, abstractmethod
from typing import Any, Type

from pythonosc.osc_message_builder import OscMessageBuilder


class BaseOscMessageAdapter(ABC):

    @abstractmethod
    def handles_type(self, obj: Any) -> bool:
        pass

    @abstractmethod
    def create_message(self, address: str, value: Any) -> OscMessageBuilder:
        pass

    @abstractmethod
    def parse_message(self, data_type: Type, *values: Any) -> Any:
        pass
