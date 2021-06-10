CarnaPy
========

The aim of this package is to provide real-time 3D visualization in Python for specifically, but not limited to, biomedical data. The library is based on [Carna](https://github.com/kostrykin/Carna).

See [examples/kalinin2018.ipynb](examples/kalinin2018.ipynb) for an example.

[![Anaconda-Server Badge](https://anaconda.org/kostrykin/carnapy/badges/version.svg)](https://anaconda.org/kostrykin/carnapy)
[![Anaconda-Server Badge](https://anaconda.org/kostrykin/carnapy/badges/platforms.svg)](https://anaconda.org/kostrykin/carnapy)
[![Anaconda-Server Badge](https://anaconda.org/kostrykin/carnapy/badges/installer/conda.svg)](https://conda.anaconda.org/kostrykin)

---
## Contents

* [Limitations](#1-limitations)
* [Dependencies](#2-dependencies)
* [Installation](#3-installation)
* [Build instructions](#4-build-instructions)
 
---
## 1. Limitations

* Only 8bit and 16bit volume data are supported at the moment.
* DRR renderings are not exposed to Python yet.
* Build process is currently limited to Linux-based systems.

---
## 2. Dependencies

Using the library requires the following dependencies:
* [numpy](https://numpy.org/) ≥ 1.16
* EGL driver support
* OpenGL 3.3
* Python ≥ 3.7

The following dependencies must be satisfied for the build process:
* [Carna](https://github.com/kostrykin/Carna) ≥ 3.1
* [Eigen](http://eigen.tuxfamily.org/) ≥ 3.0.5
* [libboost-iostreams](https://www.boost.org/doc/libs/1_76_0/libs/iostreams/doc/index.html)
* [pybind11](https://github.com/pybind/pybind11)
* EGL development files

In addition, the following dependencies are required to run the test suite:
* [matplotlib](https://matplotlib.org/)
* [scipy](https://www.scipy.org/)

---
## 3. Installation

The easiest way to install and use the library is to use one of the binary [Conda](https://docs.anaconda.com/anaconda/install/) packages:

```bash
conda install -c kostrykin carnapy
```

Conda packages are available for Python 3.7–3.9.

---
## 4. Build instructions

Assuming you are using a recent version of Ubuntu:

```bash
sudo apt-get -qq install libegl1-mesa-dev libboost-iostreams-dev
```

Create and activate a Conda environment to work in, then:

```bash
conda install -c conda-forge pybind11
```

Grab a recent version of [Eigen](http://eigen.tuxfamily.org), unpack it, and tell CMake where it is located:

```bash
wget https://gitlab.com/libeigen/eigen/-/archive/3.2.10/eigen-3.2.10.tar.gz
tar -vzxf eigen-3.2.10.tar.gz -C /tmp/
export CMAKE_PREFIX_PATH="/tmp/eigen-3.2.10:$CMAKE_PREFIX_PATH"
```

If you have not already, download, build, and install Carna:

```bash
git clone git@github.com:kostrykin/Carna.git build_carna
cd build_carna
sh linux_build.sh
```

Now it is time to build, package, and install CarnaPy:
```
cd ..
python setup.py build
python setup.py install
```

