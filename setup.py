from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as build_ext_orig
from pathlib import Path
import os
import packaging.version


CARNA_PY_VERSION = '0.0.1'

root_dir = Path(os.path.abspath(os.path.dirname(__file__)))
with open(root_dir / 'README.md', encoding='utf-8') as io:
    long_description = io.read()


class CMakeExtension(Extension):

    def __init__(self):
        super().__init__('CMake', sources=[])


class build_ext(build_ext_orig):

    def run(self):
        for ext in self.extensions:
            self.build_cmake(ext)
        super().run()

    def build_cmake(self, ext):
        cwd = Path().absolute()

        build_dir_debug   = cwd / 'cbuild' / 'make_debug'
        build_dir_release = cwd / 'cbuild' / 'make_release'

        get_cmake_args = lambda debug: [
            f'-DCMAKE_BUILD_TYPE={"Debug" if debug else "Release"}',
            f'-DBUILD_TEST=ON',
            f'-DBUILD_DOC={"OFF" if debug else "ON"}',
            f'../..',
        ]

        if not self.dry_run:

            version = packaging.version.parse(CARNA_PY_VERSION)
            with open(cwd / 'version.cmake', 'w') as io:
                io.write(f'set(MAJOR_VERSION {version.major})\n')
                io.write(f'set(MINOR_VERSION {version.minor})\n')
                io.write(f'set(PATCH_VERSION {version.micro})\n')

            build_dir_debug  .mkdir(parents=True, exist_ok=True)
            build_dir_release.mkdir(parents=True, exist_ok=True)

            os.chdir(str(build_dir_debug))
            self.spawn(['cmake'] + get_cmake_args(debug=True))
            self.spawn(['make'])
            self.spawn(['make', 'RUN_TESTSUITE'])

            os.chdir(str(build_dir_release))
            self.spawn(['cmake'] + get_cmake_args(debug=False))
            self.spawn(['make'])
            self.spawn(['make', 'RUN_TESTSUITE'])

        os.chdir(str(cwd))


setup(
    name = 'CarnaPy',
    version = CARNA_PY_VERSION,
    description = 'General-purpose real-time 3D visualization',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    author = 'Leonid Kostrykin',
    author_email = 'leonid.kostrykin@bioquant.uni-heidelberg.de',
    url = 'http://evoid.de',
    include_package_data = True,
    license = 'MIT',
    package_dir = {
        'carna': 'cbuild/make_release/carna',
        'carna_debug': 'cbuild/make_debug/carna',
    },
    packages = ['carna', 'carna_debug'],
    package_data = {
        'carna': ['*.so'],
        'carna_debug': ['*.so'],
    },
    ext_modules = [CMakeExtension()],
    cmdclass={
        'build_ext': build_ext,
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: GPU',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: C++',
        'Programming Language :: Python',
        'Topic :: Education',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: User Interfaces',
    ],
)

