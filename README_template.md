# Template Python Project
[![CircleCI](https://circleci.com/gh/drkostas/template_python_project/tree/master.svg?style=svg)](https://circleci.com/gh/drkostas/template_python_project/tree/master)
[![GitHub license](https://img.shields.io/badge/license-GNU-blue.svg)](https://raw.githubusercontent.com/drkostas/template_python_project/master/LICENSE)

## Table of Contents
+ [About](#about)
+ [Getting Started](#getting_started)
    + [Prerequisites](#prerequisites)
    + [Environment Variables](#env_variables)
+ [Installing, Testing, Building](#installing)
    + [Available Make Commands](#check_make_commamnds)
    + [Clean Previous Builds](#clean_previous)
    + [Venv and Requirements](#venv_requirements)
    + [Run the tests](#tests)
    + [Build Locally](#build_locally)
+ [Running locally](#run_locally)
	+ [Configuration](#configuration)
	+ [Execution Options](#execution_options)	
+ [Deployment](#deployment)
+ [Continuous Ιntegration](#ci)
+ [Todo](#todo)
+ [Built With](#built_with)
+ [License](#license)
+ [Acknowledgments](#acknowledgments)

## About <a name = "about"></a>
This is a template repository for python projects.

<i>This README serves as a template too. Feel free to modify it until it describes your project.</i>

## Getting Started <a name = "getting_started"></a>


These instructions will get you a copy of the project up and running on your local machine for development 
and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites <a name = "prerequisites"></a>

You need to have a machine with Python > 3.6 and any Bash based shell (e.g. zsh) installed.


```
$ python3.6 -V
Python 3.6.9

echo $SHELL
/usr/bin/zsh
```

### Set the required environment variables <a name = "env_variables"></a>

In order to run the [main.py](main.py) or the tests you will need to set the following 
environmental variables in your system:

```bash
$ export DROPBOX_API_KEY=<VALUE>
$ export MYSQL_HOST=<VALUE>
$ export MYSQL_USERNAME=<VALUE>
$ export MYSQL_PASSWORD=<VALUE>
$ export MYSQL_DB_NAME=<VALUE>
$ export EMAIL_ADDRESS=<VALUE>
$ export GMAIL_API_KEY=<VALUE>
```

## Installing, Testing, Building <a name = "installing"></a>

All the installation steps are being handled by the [Makefile](Makefile).

<i>If you don't want to go through the setup steps and finish the installation and run the tests,
execute the following command:</i>

```bash
$ make install server=local
```

<i>If you executed the previous command, you can skip through to the [Running locally](#run_locally) section.</i>

### Check the available make commands <a name = "check_make_commamnds"></a>

```bash
$ make help

-----------------------------------------------------------------------------------------------------------
                                              DISPLAYING HELP                                              
-----------------------------------------------------------------------------------------------------------
make delete_venv
       Delete the current venv
make create_venv
       Create a new venv for the specified python version
make requirements
       Upgrade pip and install the requirements
make run_tests
       Run all the tests from the specified folder
make setup
       Call setup.py install
make clean_pyc
       Clean all the pyc files
make clean_build
       Clean all the build folders
make clean
       Call delete_venv clean_pyc clean_build
make install
       Call clean create_venv requirements run_tests setup
make help
       Display this message
-----------------------------------------------------------------------------------------------------------
```

### Clean any previous builds <a name = "clean_previous"></a>

```bash
$ make clean server=local
make delete_venv
make[1]: Entering directory '/home/drkostas/Projects/template_python_project'
Deleting venv..
rm -rf venv
make[1]: Leaving directory '/home/drkostas/Projects/template_python_project'
make clean_pyc
make[1]: Entering directory '/home/drkostas/Projects/template_python_project'
Cleaning pyc files..
find . -name '*.pyc' -delete
find . -name '*.pyo' -delete
find . -name '*~' -delete
make[1]: Leaving directory '/home/drkostas/Projects/template_python_project'
make clean_build
make[1]: Entering directory '/home/drkostas/Projects/template_python_project'
Cleaning build directories..
rm --force --recursive build/
rm --force --recursive dist/
rm --force --recursive *.egg-info
make[1]: Leaving directory '/home/drkostas/Projects/template_python_project'

```

### Create a new venv and install the requirements <a name = "venv_requirements"></a>

```bash
$ make create_venv server=local
Creating venv..
python3.6 -m venv ./venv

$ make requirements server=local
Upgrading pip..
venv/bin/pip install --upgrade pip wheel setuptools
Collecting pip
.................
```



### Run the tests <a name = "tests"></a>

The tests are located in the `tests` folder. To run all of them, execute the following command:

```bash
$ make run_tests server=local
source venv/bin/activate && \
.................
```

### Build the project locally <a name = "build_locally"></a>

To build the project locally using the setup.py command, execute the following command:

```bash
$ make setup server=local
venv/bin/python setup.py install '--local'
running install
.................
```

## Running the code locally <a name = "run_locally"></a>

In order to run the code now, you will only need to change the yml file if you need to 
and run either the main or the created console script.

### Modifying the Configuration <a name = "configuration"></a>

There is an already configured yml file under [confs/template_conf.yml](confs/template_conf.yml) with the following structure:

```yaml
tag: production
cloudstore:
  config:
    api_key: !ENV ${DROPBOX_API_KEY}
  type: dropbox
datastore:
  config:
    hostname: !ENV ${MYSQL_HOST}
    username: !ENV ${MYSQL_USERNAME}
    password: !ENV ${MYSQL_PASSWORD}
    db_name: !ENV ${MYSQL_DB_NAME}
    port: 3306
  type: mysql
email_app:
  config:
    email_address: !ENV ${EMAIL_ADDRESS}
    api_key: !ENV ${GMAIL_API_KEY}
  type: gmail
```

The `!ENV` flag indicates that a envirnonmental value follows. 
You can change the values/environmental var names as you wish.
If a yaml variable name is changed/added/deleted, the corresponding changes should be reflected 
on the [Configuration class](configuration/configuration.py) and the [yml_schema.json](configuration/yml_schema.json) too.

### Execution Options <a name = "execution_options"></a>

First, make sure you are in the created virtual environment:

```bash
$ source venv/bin/activate
(venv) 
OneDrive/Projects/template_python_project  dev 

$ which python
/home/drkostas/Projects/template_python_project/venv/bin/python
(venv) 
```

Now, in order to run the code you can either call the `main.py` direclty, or the `template_python_project` console script.

```bash
$ python main.py --help
usage: main.py -m {run_mode_1,run_mode_2,run_mode_3} -c CONFIG_FILE [-l LOG]
               [-d] [-h]

A template for python projects.

required arguments:
  -m {run_mode_1,run_mode_2,run_mode_3}, --run-mode {run_mode_1,run_mode_2,run_mode_3}
                        Description of the run modes
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The configuration yml file
  -l LOG, --log LOG     Name of the output log file

optional arguments:
  -d, --debug           enables the debug log messages

# Or

$ template_python_project --help
usage: template_python_project -m {run_mode_1,run_mode_2,run_mode_3} -c
                               CONFIG_FILE [-l LOG] [-d] [-h]

A template for python projects.

required arguments:
  -m {run_mode_1,run_mode_2,run_mode_3}, --run-mode {run_mode_1,run_mode_2,run_mode_3}
                        Description of the run modes
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The configuration yml file
  -l LOG, --log LOG     Name of the output log file

optional arguments:
  -d, --debug           enables the debug log messages
  -h, --help            Show this help message and exit
```

## Deployment <a name = "deployment"></a>

The deployment is being done to <b>Heroku</b>. For more information
you can check the [setup guide](https://devcenter.heroku.com/articles/getting-started-with-python). 

Make sure you check the defined [Procfile](Procfile) ([reference](https://devcenter.heroku.com/articles/getting-started-with-python#define-a-procfile)) 
and that you set the [above-mentioned environmental variables](#env_variables) ([reference](https://devcenter.heroku.com/articles/config-vars)).

## Continuous Integration <a name = "ci"></a>

For the continuous integration, the <b>CircleCI</b> service is being used. 
For more information you can check the [setup guide](https://circleci.com/docs/2.0/language-python/). 

Again, you should set the [above-mentioned environmental variables](#env_variables) ([reference](https://circleci.com/docs/2.0/env-vars/#setting-an-environment-variable-in-a-context))
and for any modifications, edit the [circleci config](/.circleci/config.yml).

## TODO <a name = "todo"></a>

Read the [TODO](TODO.md) to see the current task list.

## Built With <a name = "built_with"></a>

* [SQLAlchemy](https://pypi.org/project/SQLAlchemy/) - Used for the Datastore Class
* [Dropbpox Python API](https://www.dropbox.com/developers/documentation/python) - Used for the Cloudstore Class
* [Gmail Sender](https://github.com/paulc/gmail-sender) - Used for the EmailApp Class
* [Heroku](https://www.heroku.com) - The deployment environment
* [CircleCI](https://www.circleci.com/) - Continuous Integration service


## License <a name = "license"></a>

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments <a name = "acknowledgments"></a>

* Thanks το PurpleBooth fort the [README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)

