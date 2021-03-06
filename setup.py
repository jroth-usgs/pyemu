import sys
from distutils.core import setup


long_description = \
"""pyemu is a set of python modules for linear-based model-independent uncertainty analyses.
""" 

setup(name="pyemu",
      description=long_description,
      long_description=long_description,      
      author="Jeremy White",
      author_email='jwhite@usgs.gov',
      url='https://github.com/jtwhite79/pyemu',
      license='GNU GPL',
      platforms='Windows, Mac OS-X',
      packages = ["pyemu","pyemu.pst","pyemu.utils","pyemu.mat"],
      version="0.1")
