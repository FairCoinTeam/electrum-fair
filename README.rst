Electrum - lightweight Bitcoin client
=====================================

::

  Licence: GNU GPL v3
  Author: Thomas Voegtlin
  Ported by: Thomas König
  Language: Python
  Homepage: https://electrum.fair-coin.org/



1. GETTING STARTED
------------------

To run Electrum from this directory, just do::

    ./electrum-fair

If you install Electrum on your system, you can run it from any
directory.

If you have pip, you can do::

    python setup.py sdist
    sudo pip install --pre dist/ElectrumFair-2.4.tar.gz


If you don't have pip, install with::

    python setup.py sdist
    sudo python setup.py install



To start Electrum from your web browser, see
http://electrum.org/bitcoin_URIs.html



2. HOW OFFICIAL PACKAGES ARE CREATED
------------------------------------

On Linux/Windows::

    pyrcc4 icons.qrc -o gui/qt/icons_rc.py
    python setup.py sdist --format=zip,gztar

On Mac OS X::

    # On port based installs
    sudo python setup-release.py py2app

    # On brew installs
    ARCHFLAGS="-arch i386 -arch x86_64" sudo python setup-release.py py2app --includes sip

    sudo hdiutil create -fs HFS+ -volname "Electrum" -srcfolder dist/Electrum.app dist/electrum-VERSION-macosx.dmg
