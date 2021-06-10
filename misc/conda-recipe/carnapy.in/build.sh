export ROOT_DIR="$$PWD"

wget "https://github.com/kostrykin/Carna/archive/refs/tags/$VERSION_CARNA.tar.gz" -O carna.tgz
tar -vzxf carna.tgz
cd "Carna-$VERSION_CARNA"
mkdir -p build/make_release
cd "$$ROOT_DIR/Carna-$VERSION_CARNA/build/make_release"
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_DOC=OFF -DBUILD_TEST=OFF -DBUILD_DEMO=OFF -DCMAKE_INSTALL_PREFIX=$$PREFIX -DCMAKE_PREFIX_PATH=$$PREFIX -DBUILD_EGL=ON ../..
make VERBOSE=1
make install

cd "$$ROOT_DIR"
$$PYTHON setup.py build
$$PYTHON setup.py install --single-version-externally-managed --root=/
