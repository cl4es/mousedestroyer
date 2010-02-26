#!/usr/bin/env python

from distutils.core import setup

import sys
import os

print sys.path

# The main entry point of the program
script_file = 'bubbledefender.py'


image_files = []
for file in os.listdir('images'):
    file = os.path.join('images', file)
    if os.path.isfile(file):
        image_files.append(file)

mydata_files = [('images', image_files)]

# Setup args that apply to all setups, including ordinary distutils.
setup_args = dict(
    data_files=mydata_files)
    
# py2exe options
try:
    import py2exe
    setup_args.update(dict(
        windows=[script_file],
        zipfile=None,
        options={"py2exe": {'bundle_files':1}}))
except ImportError:
    pass


setup(**setup_args)
"""
setup(name='MouseDestroyer',
      version='0.1',
      description='Not really a game, yet. Just testing pyglet',
      author='Claes Redestad',
      author_email='claes.redestad@gmail.com',
      url='http://www.genara.se/',
      windows=["higame.py"])"""
