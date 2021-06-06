CarnaPy
========

The aim of this package is to provide general-purpose real-time 3D visualization based on [Carna](https://github.com/RWTHmediTEC/Carna) specifically for, but not limited to, biomedical data.

---
## Contents

* [Dependencies](#1-dependencies)
* [Build instructions](#2-build-instructions)
 
---
## 1. Dependencies

* [Eigen](http://eigen.tuxfamily.org/) ≥ 3.0.5
* [Carna](https://github.com/RWTHmediTEC/Carna)
* [libboost-iostreams](https://www.boost.org/doc/libs/1_76_0/libs/iostreams/doc/index.html)
* OpenGL 3.3
* GLEW ≥ 1.7
* Python 3
* pybind11
* Linux environment and Conda

Compilation process has been tested with following tools and versions:

* **Eigen 3.2.10** is known to be fully supported.
* **GCC 7.5** is known to be fully supported.
* **Python 3.8.5** is known to be fully supported.
* **Ubuntu 18.04** is known to be fully supported.
* **pybind11 2.5.0** is known to be fully supported.

---
## 2. Build instructions

Assuming you are using a recent version of Ubuntu:

```bash
sudo apt-get -qq install libglew-dev libboost-iostreams-dev
```

Create and activate a Conda environment to work in, then:

```bash
conda install -c conda-forge pybind11
```

Download a recent version of [Eigen](http://eigen.tuxfamily.org), unpack it, and tell CMake where it is located:

```bash
wget https://gitlab.com/libeigen/eigen/-/archive/3.2.10/eigen-3.2.10.tar.gz
tar -vzxf eigen-3.2.10.tar.gz -C /tmp/
export CMAKE_PREFIX_PATH="/tmp/eigen-3.2.10:$CMAKE_PREFIX_PATH"
```

If you have not already, download, build, and install Carna:

```bash
cd /tmp
git clone git@github.com:RWTHmediTEC/Carna.git
cd Carna
sh linux_build.sh
```

Now it is time to build, package, and install CarnaPy:
```
cd /tmp/CarnaPy
python setup.py bdist_wheel
python -m pip install CarnaPy/dist/CarnaPy-*.whl
```

