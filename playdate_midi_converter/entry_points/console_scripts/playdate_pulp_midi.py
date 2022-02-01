import os
import sys
from argparse import ArgumentParser

from playdate_midi_converter.__version__ import __VERSION__

def run():
  par = ArgumentParser(prog=sys.argv[0], description='Convert Playdate Pulp JSON file to MIDI.')
  par.add_argument('--in', '-i', dest='file_in', nargs=1, required=True)
  par.add_argument('--out', '-o', dest='file_out', nargs=1, required=True)
  par.add_argument('--version', action='version', version=f'%(prog)s {__VERSION__}')
  
  args = par.parse_args(sys.argv[1:])
  with open(args.file_in, 'r') as f_in:
    with open(args.file_out, 'w') as f_out:
      # TODO: Do conversion
      pass
    pass
  sys.exit(0)
  
