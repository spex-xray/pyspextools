#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import re
import pyspex

# Set dependencies, we need sphinx to build doc and numpy for arrays
dependencies = ['sphinx','numpy','future','astropy','sphinx-argparse']

# Add doc directory to install-prefix directory
datafiles=[]
for d, folders, files in os.walk('doc/build/html'):
    dir_inst='doc/'+re.sub('doc/build/','',d)
    datafiles.append((dir_inst, [os.path.join(d,f) for f in files]))

# Do the actual setup
setup(name='pyspex',
      version=pyspex.__version__,
      description='SPEX Python tools',
      author='SPEX development team',
      author_email='j.de.plaa@sron.nl',
      url='https://www.sron.nl/spex',
      packages=find_packages(),
      include_package_data = True,
      package_data={'':['*.rst']},
      scripts=['scripts/ogip2spex','scripts/tg2spex'],
      data_files=datafiles,
      install_requires=dependencies,
      )

# Auto-generate documentation
try:
    import sphinx

    # Automatically build html documentation
    # For example:
    #   format = 'html'
    #   sphinx-src-dir = './doc'
    #   sphinx-build-dir = './doc/build'
    sphinx.build_main(['setup.py', '-b', 'html', './doc/source', './doc/build/html'])

except ImportError:
    print("Unable to generate documentation. Install sphinx")

