# Job Applying bot for xe.gr

A bot that automatically applies to new job posts in xe.gr using your gmail address.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

You will need to setup an application-specific password rather than using your account-password - see:
          
    https://support.google.com/mail/?p=InvalidSecondFactor
    https://security.google.com/settings/security/apppasswords

### Installing

Installing the requirements

```
pip install -r requirements.txt
```

Create a database named email with the following structure (I suggest using the free-tier Amazon RDS):

	+---------+--------------+----------------+
	| Field   | Type         | Extra          |
	+---------+--------------+----------------+
	| id      | int(11)      | auto_increment |
	| link    | varchar(100) |                |
	| email   | varchar(100) |                |
	| sent_on | varchar(100) |                |
	+---------+--------------+----------------+

You will also need to add your information as follows:

send_emails.py

	store = DataStore('username', 'passw', 'url', 'dbname') # Your db credentials
	gmail = GMail('Name Lastname <youremail@mail.com>','app_specific_pass') # Your gmail credentials
	yourname_email = "Name Lastname <youremail@mail.com>" # Your email and display name
	# Also edit the email subjects and bodies at the lines 27-72
	# Place your attachments in the attachments folder and edit line 104

crawler.py

	# Go to xe.gr and find the the appropriate keywords
	# Then insert them in the line 40
	# Add any words you want to avoid at the line 54

And your are good to go!

Run `send_emails list` to see the emails sent, `send_emails remove ID_NUMBER` to remove an entry from the table or `send_emails` to run continuesly the script.

## Deployment

You can easily deploy it to heroku.com (Procfile will automatically run the script). 

## License

This project is licensed under the GNU General Public License v3.0 License
