import sys
from argparse import ArgumentParser, FileType
from logging import DEBUG

from playdate_midi_converter.__version__ import __VERSION__

from playdate_midi_converter.midi import Midi
from playdate_midi_converter.config import Config, Context
from playdate_midi_converter.json import song_to_json
from playdate_midi_converter.ui.cli.channel_mapping import CliChannelMapper
from playdate_midi_converter.song import Channel, Track


def run():
  par = ArgumentParser(prog=sys.argv[0], description='Convert Playdate Pulp JSON file to MIDI.')
  par.add_argument('--in', '-i', dest='file_in', type=FileType('rb'), default=sys.stdin)
  par.add_argument('--out', '-o', dest='file_out', type=FileType('wt'), default=sys.stdout)
  par.add_argument('--pretty', '-p', action='store_true')
  par.add_argument('--max-notes', '-m', dest='max_notes', default=512, type=int)
  par.add_argument('--version', action='version', version=f'%(prog)s {__VERSION__}')
  
  args = par.parse_args(sys.argv[1:])
  
  # TODO: Get config data from config file.
  cfg = Config()
  ctx = Context(cfg, log_level=DEBUG)
  try:
    midi = Midi(ctx, args.file_in, clip=True)
  except Exception as e:
    ctx.log_manager.root.error(f"Midi file read error: {e!s}")
    sys.exit(1)
  
  try:
    song = midi.convert()
  except KeyboardInterrupt as e:
    raise e
  except Exception as e:
    ctx.log_manager.root.error(f"Song conversion error: {e!s}")
    sys.exit(1)
  
  mapper = CliChannelMapper()
  
  keep_name = False
  while not keep_name:
    song_name = mapper.read_line(f"Song name? ").strip()
    keep_name = mapper.yes_no(f"Song name \"{song_name}\". Continue?")
  
  channels = list(Channel)
  tracks = list(song.tracks)
  track_mappings = mapper.tracks_to_channels(tracks, channels)
  for track, channel in track_mappings.items():
    track.channel = channel
    channels.remove(channel)
  for channel in channels:
    empty_track = Track(0, '', [], channel=channel)
    tracks.append(empty_track)
  tracks.sort(key=lambda t: t.channel)
  song.tracks = tracks
  
  try:
    song_json = song_to_json(song, args.pretty)
  except Exception as e:
    ctx.log_manager.root.error(f"Song conversion error: {e!s}")
    sys.exit(1)
  
  try:
    args.file_out.write(song_json)
  except Exception as e:
    ctx.log_manager.root.error(f"JSON file write error: {e!s}")
    sys.exit(1)
  
  ctx.log_manager.root.info(f"SUCCESS!")
  sys.exit(0)
  
