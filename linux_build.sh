#!/bin/bash
set -e

mkdir -p build/make_debug
mkdir -p build/make_release

export CMAKE_OPTIONS="-DBOOST_ROOT=$BOOST_ROOT -DBOOST_INCLUDEDIR=$BOOST_ROOT/include -DBOOST_LIBRARYDIR=$BOOST_ROOT/lib -DBoost_NO_SYSTEM_PATHS=TRUE -DBoost_NO_BOOST_CMAKE=TRUE -DPYTHON_VERSION=$PYTHON_VERSION -DCMAKE_SKIP_RPATH=ON -DCMAKE_POSITION_INDEPENDENT_CODE=ON"

cd build/make_debug
cmake -DCMAKE_BUILD_TYPE=Debug -DBUILD_TEST=ON -DBUILD_DOC=ON $CMAKE_OPTIONS -DCMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX/debug ../..
make
make RUN_TESTSUITE

cd ../make_release
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TEST=ON -DBUILD_DOC=OFF $CMAKE_OPTIONS -DCMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX/release ../..
make
make RUN_TESTSUITE

echo
echo "** Ready to install."

sudo make install
cd ../make_debug
sudo make install
