from setuptools import setup, find_packages
from src.playdate_midi_converter.__version__ import __VERSION__ as PKG_VERSION

setup(
  name='playdate-midi-converter',
  version=PKG_VERSION,
  packages=find_packages(where='src'),
  package_dir={
    '': 'src'
  },
  url='https://github.com/ryanbeard82/Python-Midi-to-JSON',
  license='',
  author='Ryan Beard',
  author_email='ryan_o_beard@me.com',
  description='Library to convert Playdate Pulp IDE\'s JSON files to MIDI.',
  entry_points={
    'console_scripts': [
      'playdate-pulp-midi = playdate_midi_converter.entry_points.console_scripts.playdate_pulp_midi:run'
    ],
  },
)
