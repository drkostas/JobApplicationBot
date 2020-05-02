# Auto Apply Bot
[![CircleCI](https://circleci.com/gh/drkostas/AutoApplyBot/tree/master.svg?style=svg)](https://circleci.com/gh/drkostas/AutoApplyBot/tree/master)
[![GitHub license](https://img.shields.io/badge/license-GNU-blue.svg)](https://raw.githubusercontent.com/drkostas/AutoApplyBot/master/LICENSE)

## Table of Contents

+ [About](#about)
+ [Getting Started](#getting_started)
    + [Prerequisites](#prerequisites)
    + [Environment Variables](#env_variables)
    + [Data Files](#data_files)
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
+ [Built With](#built_with)
+ [License](#license)
+ [Acknowledgments](#acknowledgments)

## About <a name = "about"></a>

A bot that automatically sends emails to new ads posted in any desired xe.gr search url.

In just a few minutes of configuring until it suits your needs, it can easily be deployed and start sending your 
specified emails to every new ad that gets posted in the search url you select within xe.gr. 

With a little programming, you can also modify the [XeGrAdSiteCrawler class](ad_site_crawler/xegr_ad_site_crawler.py) 
and make it support other advertisement sites too. Feel free to fork.

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

You will also need to setup the following:
- Gmail: An application-specific password for your Google account. 
[Reference 1](https://support.google.com/mail/?p=InvalidSecondFactor), 
[Reference 2](https://security.google.com/settings/security/apppasswords) 
- Dropbox: An Api key for your Dropbox account. 
[Reference 1](http://99rabbits.com/get-dropbox-access-token/), 
[Reference 2](https://dropbox.tech/developers/generate-an-access-token-for-your-own-account) 
- MySql: If you haven't any, you can create a free one on Amazon RDS. 
[Reference 1](https://aws.amazon.com/rds/free/), 
[Reference 2](https://bigdataenthusiast.wordpress.com/2016/03/05/aws-rds-instance-setup-oracle-db-on-cloud-free-tier/) 

### Set the required environment variables <a name = "env_variables"></a>

In order to run the [main.py](main.py) or the tests you will need to set the following 
environmental variables in your system:

```bash
DROPBOX_API_KEY=<VALUE>
MYSQL_HOST=<VALUE>
MYSQL_USERNAME=<VALUE>
MYSQL_PASSWORD=<VALUE>
MYSQL_DB_NAME=<VALUE>
EMAIL_ADDRESS=<VALUE>
GMAIL_API_KEY=<VALUE>
CHECK_INTERVAL=<VALUE>
CRAWL_INTERVAL=<VALUE>
TEST_MODE=<VALUE>
LOOKUP_URL=<VALUE>
```

- LOOKUP_URL (str): The url that matches your desired search results. You can copy it straight from your browser.
- CHECK_INTERVAL (int) : The seconds to wait before each check (for new ads).
- CRAWL_INTERVAL (int) : The seconds to wait before each crawl (for the discovering of sublinks).
- TEST_MODE (bool) : If enabled, every email will be sent to you instead of the discovered email addresses.

### Modify the files in the data folder <a name = "data_files"></a>

Before starting, you should modify the emails that are going to be sent, the stop-words e.t.c.

- [stop_words.txt](data/stop_words.txt): A list of words that you don't want to be present in the ads that the bot
sends emails to.
- [application_sent_subject.txt](data/application_sent_subject.txt): The subject of the email that is going to be sent 
to new ads.
- [application_sent_html.html](data/application_sent_html.html): The html body of the email that is going to be sent 
to new ads.
- [inform_success_subject.txt](data/inform_success_subject.txt): The subject of the email that is going to be sent 
to you when the bot successfully sends an email.
- [inform_success_sent_html.html](data/inform_success_sent_html.html): The html body of the email that is going to be sent 
to you when the bot successfully sends an email. Make sure to use the {link} and {email} vars 
in order to include them in the email.
- [inform_should_call.txt](data/inform_should_calll.txt): The subject of the email that is going to be sent 
to you when the bot couldn't find any email to a new ad, and requires manual action.
- [inform_should_call_html.html](data/inform_should_calll_html.html): The html body of the email that is going to be sent 
to you when the bot couldn't find any email to a new ad, and requires manual action. Make sure to use the {link} var 
in order to include it in the email.
- Attachments: Add any attachments you want to be included in the Ad Email and define 
their names in [xegr_jobs.yml](confs/xegr_jobs.yml)


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
make[1]: Entering directory '/home/drkostas/Projects/AutoApplyBot'
Deleting venv..
rm -rf venv
make[1]: Leaving directory '/home/drkostas/Projects/AutoApplyBot'
make clean_pyc
make[1]: Entering directory '/home/drkostas/Projects/AutoApplyBot'
Cleaning pyc files..
find . -name '*.pyc' -delete
find . -name '*.pyo' -delete
find . -name '*~' -delete
make[1]: Leaving directory '/home/drkostas/Projects/AutoApplyBot'
make clean_build
make[1]: Entering directory '/home/drkostas/Projects/AutoApplyBot'
Cleaning build directories..
rm --force --recursive build/
rm --force --recursive dist/
rm --force --recursive *.egg-info
make[1]: Leaving directory '/home/drkostas/Projects/AutoApplyBot'

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

There is an already configured yml file under [xegr_jobs.yml](confs/xegr_jobs.yml) with the following structure:

```yaml
tag: production
lookup_url: !ENV ${LOOKUP_URL}
check_interval: !ENV ${CHECK_INTERVAL}
crawl_interval: !ENV ${CRAWL_INTERVAL}
test_mode: !ENV ${TEST_MODE}
cloudstore:
  - config:
      api_key: !ENV ${DROPBOX_API_KEY}
      local_files_folder: data
      attachments_names:
        - cv.pdf
        - cover_letter.pdf
      update_attachments: true
      update_stop_words: true
      update_application_sent_email: true
      update_inform_success_email: true
      update_inform_should_call_email: true
    type: dropbox
datastore:
  - config:
      hostname: !ENV ${MYSQL_HOST}
      username: !ENV ${MYSQL_USERNAME}
      password: !ENV ${MYSQL_PASSWORD}
      db_name: !ENV ${MYSQL_DB_NAME}
      port: 3306
    type: mysql
email_app:
  - config:
      email_address: !ENV ${EMAIL_ADDRESS}
      api_key: !ENV ${GMAIL_API_KEY}
    type: gmail

```

The `!ENV` flag indicates that a environmental value follows. 
You can change the values/environmental var names as you wish.
If a yaml variable name is changed/added/deleted, the corresponding changes should be reflected 
on the [Configuration class](configuration/configuration.py) and the [yml_schema.json](configuration/yml_schema.json) too.

You can also modify each class's default options 

### Execution Options <a name = "execution_options"></a>

First, make sure you are in the created virtual environment:

```bash
$ source venv/bin/activate
(venv) 
OneDrive/Projects/auto_apply_bot  dev 

$ which python
/home/drkostas/Projects/auto_apply_bot/venv/bin/python
(venv) 
```

If it's the first time you are running the code you may need to execute those 2 steps:
- To create the required table in the Database run:

    `$ python main.py -m create_table -c confs/conf.yml -l logs/output.log`
    
- To upload the files that are going to be used to Dropbox (after modifying them appropriately)
run:

    `$ python main.py -m upload_files -c confs/conf.yml -l logs/output.log`

Now, in order to run the code you can either call the `main.py` directly, or the `auto_apply_bot` console script.

```bash
$ python main.py --help
usage: main.py -m
               {crawl_and_send,list_emails,remove_email,upload_files,create_table}
               -c CONFIG_FILE [-l LOG] [--email-id EMAIL_ID] [-d] [-h]

A bot that automatically sends emails to new ads posted in the specified xe.gr
search page.

required arguments:
  -m {crawl_and_send,list_emails,remove_email,upload_files,create_table}, --run-mode {crawl_and_send,list_emails,remove_email,upload_files,create_table}
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The configuration yml file
  -l LOG, --log LOG     Name of the output log file

Optional Arguments:
  --email-id EMAIL_ID   The id of the email you want to be deleted
  -d, --debug           Enables the debug log messages
  -h, --help            Show this help message and exit


# Or

$ auto_apply_bot --help
usage: auto_apply_bot -m
               {crawl_and_send,list_emails,remove_email,upload_files,create_table}
               -c CONFIG_FILE [-l LOG] [--email-id EMAIL_ID] [-d] [-h]

A bot that automatically sends emails to new ads posted in the specified xe.gr
search page.

required arguments:
  -m {crawl_and_send,list_emails,remove_email,upload_files,create_table}, --run-mode {crawl_and_send,list_emails,remove_email,upload_files,create_table}
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        The configuration yml file
  -l LOG, --log LOG     Name of the output log file

Optional Arguments:
  --email-id EMAIL_ID   The id of the email you want to be deleted
  -d, --debug           Enables the debug log messages
  -h, --help            Show this help message and exit

```

If you notice that no ad is being discovered, fine-tune the `crawl_interval` and `_anchor_class_name` default values in 
[XeGrAdSiteCrawler class](ad_site_crawler/xegr_ad_site_crawler.py). 

- The `crawl_interval` defines the time between each crawl and should be increased 
if the bot is being flagged as a bot (well..). You can change this from the yaml file.

- The `anchor_class_name` is the css class value that characterizes all the search results anchors (`<a .. class=`) 
and if you this it is wrong, you can change from the top of the class definition.


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

## Built With <a name = "built_with"></a>

* [Dropbox Python API](https://www.dropbox.com/developers/documentation/python) - Used for the Cloudstore Class
* [Gmail Sender](https://github.com/paulc/gmail-sender) - Used for the EmailApp Class
* [Heroku](https://www.heroku.com) - The deployment environment
* [CircleCI](https://www.circleci.com/) - Continuous Integration service


## License <a name = "license"></a>

This project is licensed under the GNU License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments <a name = "acknowledgments"></a>

* Thanks το PurpleBooth for the [README template](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)

