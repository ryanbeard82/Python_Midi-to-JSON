import io
import os
import sys
from argparse import ArgumentParser, FileType
from logging import DEBUG

from playdate_midi_converter.__version__ import __VERSION__

from playdate_midi_converter.midi import Midi
from playdate_midi_converter.config import Config, Context
from playdate_midi_converter.json import song_to_json
from playdate_midi_converter.ui.cli.channel_mapping import CliChannelMapper
from playdate_midi_converter.ui.input import open_file, choose_save_dir
from playdate_midi_converter.song import Channel, Song, Track


def run():
  par = ArgumentParser(prog=sys.argv[0], description='Convert Playdate Pulp JSON file to MIDI.')
  par.add_argument('--in', '-i', dest='file_in', default=None)
  par.add_argument('--out', '-o', dest='file_out', default=None)
  par.add_argument('--pretty', '-p', action='store_true')
  par.add_argument('--max-notes', '-m', dest='max_notes', default=512, type=int)
  par.add_argument('--version', action='version', version=f'%(prog)s {__VERSION__}')
  
  args = par.parse_args(sys.argv[1:])
  
  # TODO: Get config data from config file.
  cfg = Config()
  ctx = Context(cfg, log_level=DEBUG)

  if args.file_in == "-":
    if sys.stdin.isatty():
      ctx.log_manager.root.error("STDIN not available.")
      sys.exit(1)
    
    file_in = sys.stdin

  elif args.file_in is not None and len(args.file_in) > 0:
    if not os.path.isfile(args.file_in):
      ctx.log_manager.root.error(f"'{args.file_in}' is not a file or does not exist.")
      sys.exit(1)
    
    file_in = open(args.file_in, mode='rb')

  else:
    ctx.log_manager.root.info("Input file not specified. Asking user to provide one.")
    try:
      file_in = _choose_file_in(ctx)
    except Exception as e:
      ctx.log_manager.root.error(f"File select error: {e!s}")
      sys.exit(1)

  try:
    if file_in == sys.stdin:
      midi = Midi(ctx, io.BytesIO(sys.stdin.buffer.read()), clip=True)
      # TODO: Reading from stdin this way causes the user input later to error and infinitely loop. Find a way to fix this.
    else:
      midi = Midi(ctx, file_in, clip=True)
  except Exception as e:
    ctx.log_manager.root.error(f"MIDI read error: {e!s}")
    sys.exit(1)
  
  mapper = CliChannelMapper()

  if args.file_out == "-":
    file_out = sys.stdout
  elif args.file_out is not None:
    try:
      file_out = open(args.file_out, mode='w')
    except Exception as e:
      ctx.log_manager.root.error(f"Output file write error: {e!s}")
      sys.exit(1)
  elif not mapper.yes_no("Save to file?"):
    file_out = sys.stdout
  else:
    file_dir = None
    out_filename = "song.json"
    if file_in != sys.stdin:
      file_dir = os.path.dirname(file_in.name)
      out_filename = os.path.basename(file_in.name) + '.json'
    
    try:
      file_out = _choose_file_out(ctx, mapper, out_filename, file_dir)
    except Exception as e:
      ctx.log_manager.root.error(f"Output file selection error: {e!s}")
      sys.exit(1)
  
  try:
    song = _midi_to_song(ctx, mapper, midi)
    song_json = song_to_json([song], args.pretty)
  except KeyboardInterrupt as e:
    raise e
  except Exception as e:
    ctx.log_manager.root.error(f"Song conversion error: {e!s}")
    sys.exit(1)
  
  try:
    file_out.write(song_json)
    #file_out.flush()
    #file_out.close()
  except Exception as e:
    ctx.log_manager.root.error(f"JSON file write error: {e!s}")
    sys.exit(1)
  
  ctx.log_manager.root.info(f"SUCCESS!")
  sys.exit(0)


def _choose_file_in(ctx: Context):
  filename = open_file(ctx)
  return open(filename, mode='rb')


def _choose_file_out(ctx: Context, mapper: CliChannelMapper, file_name, save_dir=None):
  # TODO: Remove dependency on CliChannelMapper. Currently only used for convenient access to its 'yes_no' method.
  out_file_name_is_valid = False
  while not out_file_name_is_valid:
    save_dir = choose_save_dir(ctx, initial_dir=save_dir)
    
    out_file_name = os.path.join(save_dir, file_name)

    if os.path.exists(out_file_name):
      out_file_name_is_valid = mapper.yes_no(f"File '{out_file_name}' exists. Overwrite?", default_yes=False)
    else:
      out_file_name_is_valid = True

  return open(out_file_name, mode='w')

def _midi_to_song(ctx: Context, mapper: CliChannelMapper, midi: Midi) -> Song:
  song = midi.convert()
  keep_name = False
  while not keep_name:
    song.name = mapper.read_line(f"Song name? ").strip()
    keep_name = mapper.yes_no(f"Song name \"{song.name}\". Continue?")
  
  channels = list(Channel)
  tracks = list()
  track_mappings = mapper.tracks_to_channels(song.tracks, channels)
  for track, channel in track_mappings.items():
    if channel is None: # Ignored
      continue
    tracks.append(track)
    track.channel = channel
    channels.remove(channel)
  for channel in channels:
    empty_track = Track(0, '', [], channel=channel)
    tracks.append(empty_track)
  tracks.sort(key=lambda t: t.channel)
  song.tracks = tracks

  return song
