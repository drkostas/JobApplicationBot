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
    name='auto_apply_bot',
    version='0.1',
    packages=['datastore', 'cloudstore', 'configuration', 'email_app', 'ad_site_crawler'],
    py_modules=['main'],
    data_files=[('', ['configuration/yml_schema.json'])],
    entry_points={
        'console_scripts': [
            'auto_apply_bot=main:main',
        ]
    },
    url='https://github.com/drkostas/AutoApplyBot',
    license='GNU General Public License v3.0',
    author='drkostas',
    author_email='georgiou.kostas94@gmail.com',
    description='A bot that automatically sends emails to new ads posted in any desired xe.gr search url.'

)
