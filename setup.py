#!/usr/bin/env python2

from setuptools import setup

setup(name='or-applet',
      version='0.0.1',
      description='A Gtk+ Tor System Tray applet',
      author='Yawning Angel',
      author_email='yawning@schwanenlied.me',
      url='https://www.github.com/yawning/or-applet',
      license = "GPL",
      packages=['orapplet'],
      include_package_data = True,
      package_data = {
        'orapplet': ['assets/*'],
      },
      entry_points={
          'console_scripts': [
            'or-applet = orapplet.main:main',
        ]
      },
     )
