#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup

PLUGIN_DIR = 'Extensions.BackUpFlash'

setup(name='enigma2-plugin-extensions-BackUpFlash',
       version='1.0',
       author='RAED',
       author_email='rrrr53@hotmail.com',
       description='plugin by (RAED & mfaraj57) to Create Backup and flash. Also to download Some Team images.',
       packages=[PLUGIN_DIR],
       package_dir={PLUGIN_DIR: 'usr'},
       package_data={PLUGIN_DIR: ['plugin.png', '*/*.png']},
       package_data={PLUGIN_DIR: ['*.png', 'buttons/*.png', 'locale/*/LC_MESSAGES/*.mo']},
      )
