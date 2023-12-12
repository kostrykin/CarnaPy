#!/bin/bash

# Install dependencies:
sudo apt-get -qq install libegl1-mesa-dev libboost-iostreams-dev
conda install -y -c conda-forge pybind11

# Get Eigen sources:
wget https://gitlab.com/libeigen/eigen/-/archive/3.2.10/eigen-3.2.10.tar.gz
tar -vzxf eigen-3.2.10.tar.gz -C /tmp/
export CMAKE_PREFIX_PATH="/tmp/eigen-3.2.10:$CMAKE_PREFIX_PATH"

# Build and install Carna
git clone git@github.com:kostrykin/Carna.git build_carna
cd build_carna
sh linux_build.sh

# Build and install CarnaPy
cd ..
python setup.py build
python setup.py install
