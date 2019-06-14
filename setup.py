#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import pyspextools

# Set dependencies, we need sphinx to build doc and numpy for arrays
dependencies = ['future>=0.15', 'numpy>=1.11', 'astropy>=1.1', 'sphinx-argparse>=0.1.15', 'sphinx']

# Set up sphinx
try:
    from sphinx.setup_command import BuildDoc

    cmdclass = {'build_sphinx': BuildDoc}

except ImportError:
    print("Cannot generate documentation. Please install sphinx.")
    cmdclass = {}

# Set the version numbers for the Gitlab CI process
name = 'pyspextools'

if os.environ.get('CI_COMMIT_TAG'):
    version = pyspextools.__version__
else:
    if os.environ.get('CI_JOB_ID'):
        version = pyspextools.__version__ + '_' + os.environ['CI_JOB_ID']
    else:
        version = pyspextools.__version__

# Get the long project description from the README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Do the actual setup
setup(name=name,
      version=version,
      description='SPEX Python tools',
      author='SPEX development team',
      author_email='j.de.plaa@sron.nl',
      url='https://github.com/spex-xray/pyspextools',
      license='Apache 2.0',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=find_packages(),
      include_package_data=True,
      scripts=['scripts/ogipgenrsp', 'scripts/ogip2spex', 'scripts/simres', 'scripts/tg2spex'],
      install_requires=dependencies,
      cmdclass=cmdclass,
      command_options={
          'build_sphinx': {
              'project': ('setup.py', name),
              'version': ('setup.py', pyspextools.__version__),
              'release': ('setup.py', ''),
              'source_dir': ('setup.py', './doc/source')}},
      )
