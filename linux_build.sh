#!/bin/bash
set -e

mkdir -p build/make_debug
mkdir -p build/make_release

cd build/make_debug
cmake -DCMAKE_BUILD_TYPE=Debug -DBUILD_TEST=ON -DBUILD_DOC=ON -DCMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX/debug ../..
make
make RUN_TESTSUITE

cd ../make_release
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_TEST=ON -DBUILD_DOC=OFF -DCMAKE_INSTALL_PREFIX=$CMAKE_INSTALL_PREFIX/release ../..
make
make RUN_TESTSUITE

echo
echo "** Ready to install."

sudo make install
cd ../make_debug
sudo make install
