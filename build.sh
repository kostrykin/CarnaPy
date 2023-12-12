#!/bin/bash
set -e

# Install dependencies:
sudo apt-get install -y libegl1-mesa-dev libglu1-mesa-dev libglew-dev libboost-iostreams-dev
conda install -y -c conda-forge pybind11

# Setup and check dependencies:
export PYBIND11_PREFIX="$CONDA_PREFIX/share/cmake/pybind11"
cat "$PYBIND11_PREFIX/pybind11Config.cmake" >/dev/null

# Get Eigen sources:
wget https://gitlab.com/libeigen/eigen/-/archive/3.2.10/eigen-3.2.10.tar.gz
tar -zxf eigen-3.2.10.tar.gz -C /tmp/
export CMAKE_PREFIX_PATH="/tmp/eigen-3.2.10:$CMAKE_PREFIX_PATH"

# Build and install Carna:
git clone https://github.com/kostrykin/Carna.git build_carna
cd build_carna
sh linux_build-egl.sh

# Build and install CarnaPy:
cd ..
export CARNAPY_BUILD_TEST="OFF"
python setup.py build
sudo python setup.py install
