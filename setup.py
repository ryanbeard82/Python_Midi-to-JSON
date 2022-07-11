from setuptools import setup, find_packages
from src.playdate_midi_converter.__version__ import __VERSION__ as PKG_VERSION
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
  name='playdate-midi-converter',
  version=PKG_VERSION,
  packages=find_packages(where='src'),
  package_dir={
    '': 'src'
  },
  url='https://github.com/ryanbeard82/Python-Midi-to-JSON',
  license='MIT',
  author='Ryan Beard',
  author_email='ryan_o_beard@me.com',
  description='Library to convert MIDI files to the PlayDate Pulp IDE\'s JSON format.',
  long_description=long_description,
  long_description_content_type='text/markdown',
  entry_points={
    'console_scripts': [
      'playdate-pulp-midi = playdate_midi_converter.entry_points.console_scripts.playdate_pulp_midi:run',
    ],
  },
  install_requires=[
    'mido',
    'pathlib',
    'pick',
  ],
  python_requires='>=3.9.*',
)
