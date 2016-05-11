#!/bin/bash

# You probably need to update only this link
ELECTRUM_GIT_URL=git://github.com/FairCoinTeam/electrum-fair.git
BRANCH=2.6.4
NAME_ROOT=electrum-fair


# These settings probably don't need any change
export WINEPREFIX=/opt/wine64

PYHOME=c:/python27
PYTHON="wine $PYHOME/python.exe -OO -B"


# Let's begin!
cd `dirname $0`
set -e

cd tmp

if [ -d "electrum-git" ]; then
    # GIT repository found, update it
    echo "Pull"
    cd electrum-fair-git
    git checkout master
    git pull
    cd ..
else
    # GIT repository not found, clone it
    echo "Clone"
    git clone -b $BRANCH $ELECTRUM_GIT_URL electrum-fair-git
fi

cd electrum-fair-git
VERSION=`git describe --tags`
echo "Last commit: $VERSION"

cd ..

rm -rf $WINEPREFIX/drive_c/electrum-fair
cp -r electrum-fair-git $WINEPREFIX/drive_c/electrum-fair
cp electrum-fair-git/LICENCE .

# add python packages (built with make_packages)
cp -r ../../../packages $WINEPREFIX/drive_c/electrum-fair/

# add locale dir
cp -r ../../../lib/locale $WINEPREFIX/drive_c/electrum-fair/lib/

# Build Qt resources
wine $WINEPREFIX/drive_c/Python27/Lib/site-packages/PyQt4/pyrcc4.exe C:/electrum-fair/icons.qrc -o C:/electrum-fair/lib/icons_rc.py
wine $WINEPREFIX/drive_c/Python27/Lib/site-packages/PyQt4/pyrcc4.exe C:/electrum-fair/icons.qrc -o C:/electrum-fair/gui/qt/icons_rc.py

cd ..

rm -rf dist/

# build standalone version
$PYTHON "C:/pyinstaller/pyinstaller.py" --noconfirm --ascii -w deterministic.spec

# build NSIS installer
# $VERSION could be passed to the electrum.nsi script, but this would require some rewriting in the script iself.
wine "$WINEPREFIX/drive_c/Program Files (x86)/NSIS/makensis.exe" /DPRODUCT_VERSION=$VERSION electrum.nsi

cd dist
mv electrum-fair.exe $NAME_ROOT-$VERSION.exe
mv electrum-fair-setup.exe $NAME_ROOT-$VERSION-setup.exe
mv electrum-fair $NAME_ROOT-$VERSION
zip -r $NAME_ROOT-$VERSION.zip $NAME_ROOT-$VERSION
cd ..

# build portable version
cp portable.patch $WINEPREFIX/drive_c/electrum-fair
pushd $WINEPREFIX/drive_c/electrum-fair
patch < portable.patch 
popd
$PYTHON "C:/pyinstaller/pyinstaller.py" --noconfirm --ascii -w deterministic.spec
cd dist
mv electrum-fair.exe $NAME_ROOT-$VERSION-portable.exe
cd ..

echo "Done."
