#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import re
import pyspextools

# Set dependencies, we need sphinx to build doc and numpy for arrays
dependencies = ['sphinx','numpy','future','astropy','sphinx-argparse']

# Add doc directory to install-prefix directory
datafiles=[]
for d, folders, files in os.walk('doc/build/html'):
    dir_inst='doc/'+re.sub('doc/build/','',d)
    datafiles.append((dir_inst, [os.path.join(d,f) for f in files]))

# Set up sphinx
try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}

except ImportError:
    print("Unable to generate documentation. Install sphinx")
    sys.exit(0)

name = 'pyspextools'

# Do the actual setup
setup(name=name,
      version=pyspextools.__version__,
      description='SPEX Python tools',
      author='SPEX development team',
      author_email='j.de.plaa@sron.nl',
      url='https://www.sron.nl/spex',
      packages=find_packages(),
      include_package_data = True,
      package_data={'':['*.rst']},
      scripts=['scripts/ogipgenrsp','scripts/ogip2spex','scripts/simres','scripts/tg2spex'],
      data_files=datafiles,
      install_requires=dependencies,
      cmdclass=cmdclass,
      command_options={
            'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', pyspextools.__version__),
            'release': ('setup.py', ''),
            'source_dir': ('setup.py', './doc/source')}},
      )
