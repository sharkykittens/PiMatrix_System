from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

import numpy

_music = Extension(
    name="_music",
    sources=["cmusic.c", "_music.pyx"],
    include_dirs=[
        'blas', 'm', 'C:/Users/owner/Desktop/Programming/vcpkg/packages/openblas_x86-windows/include', 'C:/Users/owner/Desktop/Programming/openblas/openblas', numpy.get_include()],
    libraries=["m", "blas"],
    extra_compile_args=["-std=c99", "-fopenmp"],
    extra_link_args=["-fopenmp"])

setup(ext_modules=[_music],
      cmdclass={'build_ext': build_ext})
