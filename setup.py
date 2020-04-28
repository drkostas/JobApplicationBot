from setuptools import setup
import sys

# import subprocess

LOCAL_ARG = '--local'

# Required Version: Python3.6
if sys.version_info < (3, 6):
    print('Python >= 3.6 required')

# Configure Requirements
with open('requirements.txt') as f:
    requirements = f.readlines()

# For the cases you want a different package to be installed on local and prod environments
if LOCAL_ARG in sys.argv:
    index = sys.argv.index(LOCAL_ARG)  # Index of the local argument
    sys.argv.pop(index)  # Removes the local argument in order to prevent the setup() error
    # subprocess.check_call([sys.executable, "-m", "pip", "install", 'A package that works locally'])
else:
    # subprocess.check_call([sys.executable, "-m", "pip", "install", 'A package that works on production'])
    pass

# Run the Setup
setup(
    name='template_python_project',
    version='0.1',
    # package_dir={'': '.'},
    packages=['datastore', 'cloudstore', 'configuration'],
    py_modules=['main'],
    data_files=[('', ['configuration/yml_schema.json'])],
    entry_points={
        'console_scripts': [
            'template_python_project=main:main',
        ]
    },
    url='https://github.com/drkostas/template_python_project',
    license='GNU General Public License v3.0',
    author='drkostas',
    author_email='georgiou.kostas94@gmail.com',
    description='A template for python projects.'

)
