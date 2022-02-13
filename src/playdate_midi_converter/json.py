from dataclasses import is_dataclass, asdict
from json import JSONEncoder, dumps
from typing import Any


def song_to_json(song, pretty: bool = False):
    if pretty:
        seps = (', ', ': ')
        indent = 4
    else:
        seps = (',', ':')
        indent = None
    return dumps(song, cls=SongEncoder, separators=seps, indent=indent)


class SongEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, JsonEncodable):
            return o.json_default()
        return super().default(o)


class JsonEncodable(object):
    def json_default(self):
        if is_dataclass(self):
            # noinspection PyDataclass
            return asdict(self)
        raise NotImplementedError()
