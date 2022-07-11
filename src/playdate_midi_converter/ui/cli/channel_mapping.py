from typing import List, Mapping, Any

from playdate_midi_converter.ui.common.channel_mapping import ChannelMapper, ChannelMappingCanceled
from playdate_midi_converter.ui.cli import UserIO, TextColor
from playdate_midi_converter.song import Track, Channel


class CliChannelMapper(UserIO, ChannelMapper):
    def tracks_to_channels(self, tracks: List[Track], channels: List[Channel]) -> Mapping[Track, Channel]:
        orig_channels = channels
        channels = channels.copy()
        results = {}
        for track in tracks:
            channel = self._map_track(track, channels)
            results[track] = channel
            if channel is not None:
                channels.remove(channel)
        if self._confirm_mappings(results):
            return results
        if self.yes_no(f"Try again?"):
            return self.tracks_to_channels(tracks, orig_channels)
        raise ChannelMappingCanceled()
    
    def _map_track(self, track: Track, channels: List[Channel]) -> Any:
        msg = TextColor.HEADER
        msg += f'Please assign track #{track.number!s} "{TextColor.UNDERLINE}{track.name}{TextColor.UNDERLINE_OFF}" to a channel:\n'
        msg += TextColor.ENDC
        # noinspection PyTypeChecker
        for number, channel in enumerate([None] + channels):
            if number == 0:
                channel_str = "(Ignore)"
            else:
                channel_str = str(channel.name).lower().capitalize()
            msg += '\t['
            msg += TextColor.OKCYAN
            msg += f'{number!s}'
            msg += TextColor.ENDC
            msg += f']\t{channel_str!s}\n'
        msg += '\n'
        self.print(msg)
        while True:
            channel = self.read_line(f"{track.name} => #").rstrip()
            try:
                channel_number = int(channel)
                if channel_number == 0:
                    return None
                return channels[channel_number - 1]
            except (ValueError, IndexError):
                pass
            if channel in channels:
                return channel
            self.print(TextColor.WARNING, f"Choice \"{TextColor.UNDERLINE}{channel}{TextColor.WARNING}\" invalid. Please try again.", TextColor.ENDC)
    
    def _confirm_mappings(self, mappings: Mapping[Track, Channel]) -> bool:
        msg = f"Currently selected mappings:\n"
        track_names = map(lambda t: t.name, mappings.keys())
        max_track_width = max(map(len, track_names))
        for track, channel in mappings.items():
            if channel is None:
                continue
            msg += f"\t{track.name:<{max_track_width}} => {channel.name.lower().capitalize()}\n"
        msg += '\n'
        self.print(msg)
        return self.yes_no(f"Continue with current selection?")
