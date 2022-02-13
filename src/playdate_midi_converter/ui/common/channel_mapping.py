from abc import ABC, abstractmethod
from typing import List, Mapping


class ChannelMappingException(Exception): pass
class ChannelMappingCanceled(ChannelMappingException): pass


class ChannelMapper(ABC):
    @abstractmethod
    def tracks_to_channels(self, tracks: List, channels: List) -> Mapping:
        raise NotImplementedError()
