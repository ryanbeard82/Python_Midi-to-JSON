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
    file_in = args.file_in

    if file_in == sys.stdin and file_in.isatty():
      file_name = open_file(ctx)

      if file_name is None:
        ctx.log_manager.root.error(f"Input file not specified.")
        par.print_help()
        sys.exit(1)

      ctx.log_manager.root.info(f"User chose file: {file_name}")

      file_in = open(file_name, mode='rb')
    
    midi = Midi(ctx, file_in, clip=True)
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
  
  try:
    file_out = args.file_out

    if file_out == sys.stdout:
      # Output file was not specified. Ask whether to save.

      if mapper.yes_no("Save to file?"):
        save_dir = None
        if file_name is not None:
          save_dir = os.path.dirname(file_name)
        
        out_file_name_is_valid = False
        while not out_file_name_is_valid:
          save_dir = choose_save_dir(ctx, initial_dir=save_dir)
          
          out_file_name = os.path.join(save_dir, os.path.basename(file_name)) + ".json"

          if os.path.exists(out_file_name):
            out_file_name_is_valid = mapper.yes_no(f"File exists. Overwrite?", default_yes=False)
          else:
            out_file_name_is_valid = True

        file_out = open(out_file_name, mode='w')
  except Exception as e:
    ctx.log_manager.root.error(f"Error choosing save directory: {e!s}")
    sys.exit(1)
  
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
  
  try:
    song_json = song_to_json([song], args.pretty)
  except Exception as e:
    ctx.log_manager.root.error(f"Song conversion error: {e!s}")
    sys.exit(1)
  
  try:
    file_out.write(song_json)
  except Exception as e:
    ctx.log_manager.root.error(f"JSON file write error: {e!s}")
    sys.exit(1)
  
  ctx.log_manager.root.info(f"SUCCESS!")
  sys.exit(0)
