# Build and install:
# > python setup.py bdist_wheel
# > python -m pip install --force-reinstall CarnaPy/dist/*.whl
# 
# Distribute to PyPI:
# > python setup.py sdist
# > python -m twine upload dist/*.tar.gz

import yaml
with open('misc/VERSIONS.yaml', 'r') as io:
    versions = yaml.safe_load(io)

VERSION_CARNA_PY = versions['build']['carnapy']
VERSION_CARNA    = versions['build']['carna'  ]

import sys
import os

from pathlib import Path

root_dir = Path(os.path.abspath(os.path.dirname(__file__)))

build_dir_debug   = root_dir / 'build' / 'make_debug'
build_dir_release = root_dir / 'build' / 'make_release'

if __name__ == '__main__':

    (build_dir_debug   / 'carna').mkdir(parents=True, exist_ok=True)
    (build_dir_release / 'carna').mkdir(parents=True, exist_ok=True)

    from setuptools import setup, Extension, find_packages
    from setuptools.command.build_ext import build_ext as build_ext_orig

    with open(root_dir / 'README.md', encoding='utf-8') as io:
        long_description = io.read()

    class CMakeExtension(Extension):

        def __init__(self):
            super().__init__('CMake', sources=[])

    class build_ext(build_ext_orig):

        def run(self):
            for ext in self.extensions:
                self.build_cmake(ext)

        def build_cmake(self, ext):
            version_major, version_minor, version_patch = [int(val) for val in VERSION_CARNA_PY.split('.')]
            get_cmake_args = lambda debug: [
                f'-DCMAKE_BUILD_TYPE={"Debug" if debug else "Release"}',
                f'-DBUILD_TEST=ON',
                f'-DBUILD_DOC={"OFF" if debug else "ON"}',
                f'-DMAJOR_VERSION={version_major}',
                f'-DMINOR_VERSION={version_minor}',
                f'-DPATCH_VERSION={version_patch}',
                f'-DREQUIRED_VERSION_CARNA={VERSION_CARNA}',
                f'-DPYTHON_EXECUTABLE={sys.executable}',
                f'../..',
            ]

            if not self.dry_run:

                os.chdir(str(build_dir_release))
                self.spawn(['cmake'] + get_cmake_args(debug=False))
                self.spawn(['make', 'VERBOSE=1'])
                self.spawn(['make', 'RUN_TESTSUITE'])

            os.chdir(str(root_dir))

    setup(
        name = 'CarnaPy',
        version = VERSION_CARNA_PY,
        description = 'General-purpose real-time 3D visualization',
        long_description = long_description,
        long_description_content_type = 'text/markdown',
        author = 'Leonid Kostrykin',
        author_email = 'leonid.kostrykin@bioquant.uni-heidelberg.de',
        url = 'https://github.com/kostrykin/CarnaPy',
        include_package_data = True,
        license = 'BSD',
        package_dir = {
            'carna': 'build/make_release/carna',
        },
        packages = ['carna'],
        package_data = {
            'carna': ['*.so'],
        },
        ext_modules = [CMakeExtension()],
        cmdclass={
            'build_ext': build_ext,
        },
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: GPU',
            'License :: OSI Approved :: BSD License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Topic :: Education',
            'Topic :: Multimedia :: Graphics :: 3D Rendering',
            'Topic :: Scientific/Engineering :: Visualization',
            'Topic :: Software Development :: User Interfaces',
        ],
        install_requires = [
            'numpy',
        ],
    )

