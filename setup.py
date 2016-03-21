#!/usr/bin/python

# python setup.py sdist --format=zip,gztar

from setuptools import setup
import os
import sys
import platform
import imp


version = imp.load_source('version', 'lib/version.py')

if sys.version_info[:3] < (2, 7, 0):
    sys.exit("Error: Electrum requires Python version >= 2.7.0...")



data_files = []
if platform.system() in [ 'Linux', 'FreeBSD', 'DragonFly']:
    usr_share = os.path.join(sys.prefix, "share")
    data_files += [
        (os.path.join(usr_share, 'applications/'), ['electrum-fair.desktop']),
        (os.path.join(usr_share, 'pixmaps/'), ['icons/electrum-fair.png'])
    ]


setup(
    name="Electrum-fair",
    version=version.ELECTRUM_VERSION,
    install_requires=[
        'slowaes>=0.1a1',
        'ecdsa>=0.9',
        'pbkdf2',
        'requests',
        'qrcode',
        'protobuf',
        'tlslite',
        'dnspython',
    ],
    package_dir={
        'electrum_fair': 'lib',
        'electrum_fair_gui': 'gui',
        'electrum_fair_plugins': 'plugins',
    },
    packages=['electrum_fair','electrum_fair_gui','electrum_fair_gui.qt','electrum_fair_plugins'],
    package_data={
        'electrum_fair': [
            'www/index.html',
            'wordlist/*.txt',
            'locale/*/LC_MESSAGES/electrum-fair.mo',
        ],
        'electrum_fair_gui': [
            "qt/themes/cleanlook/name.cfg",
            "qt/themes/cleanlook/style.css",
            "qt/themes/sahara/name.cfg",
            "qt/themes/sahara/style.css",
            "qt/themes/dark/name.cfg",
            "qt/themes/dark/style.css",
        ]
    },
    scripts=['electrum-fair'],
    data_files=data_files,
    description="Lightweight FairCoin Wallet",
    author="Thomas Koenig (original development by Thomas Voegtlin)",
    author_email="tom@fair-coin.org",
    license="GNU GPLv3",
    url="https://electrum.fair-coin.org",
    long_description="""Lightweight FairCoin Wallet"""
)
