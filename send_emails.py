# -*- coding: utf-8 -*-
import sys
import time
import arrow
from datetime import datetime, timezone, timedelta
import urllib.request, urllib.error, urllib.parse
from gmail import *
from crawler import crawl
from email_filter import get_ads_list
from datastore import DataStore

store = DataStore('username', 'passw', 'url', 'dbname') # Your db credentials
gmail = GMail('Name Lastname <youremail@mail.com>','app_specific_pass') # Your gmail credentials

yourname_email = "Name Lastname <youremail@mail.com>" # Your email and display name


def show_ads_checked():
	print("{}".format("_"*146))
	print("|{:-^6}|{:-^80}|{:-^40}|{:-^15}|".format('ID', 'Link', 'Email', 'Sent On'))
	for item in store.get_ads():
		print("|{:^6}|{:^80}|{:^40}|{:^15}|".format(item['id'], item['link'], str(item['address']), arrow.get(item['sent_on']).humanize()))
	print("|{}|".format("_"*144))

def main():
	# Email to send to job ads
	emailSubject_ad = "Subject"
	emailText_ad = """
	Hello,<br>
	<br>
	Your cover letter text
	<br>
	<br>
	Kind Regards, <br>
	Name<br>
				   """

	# Inform user that you applied on a job ad
	emailSubject_yourname_inform = "Μόλις έστειλα Βιογραφικό!"
	emailText_yourname_inform = """
	Γεια σου <i>Name</i>,
	<br><br>   
	Θα ήθελα να σε ενημερώσω ότι μόλις έστειλα το βιογραφικό σου σε μία αγγελία. 
	<br>
	<h2>Λεπτομέρειες Αγγελίας</h2>
	<b>Email:</b> <i>{0}</i>
	<br>
	<b>Link Αγγελίας:</b> <i><a href="{1}" target="_blank">{1}</a></i>    
	<br><br>   
	Καλή Τύχη,
	<br>     
	<b><i>Gmail Bot</i></b>   
	<br><br><br>
	<code>Made By Drkostas</code>
	"""

	# Inform user that there is a new ad with no email. He has to call.
	emailSubject_yourname_noEmailInform = "Νέα Αγγελία! (Πρέπει να πάρεις Τηλέφωνο)"
	emailText_yourname_noEmailInform = """
	Γεια σου <i>Name</i>,
	<br><br>   
	Θα ήθελα να σε ενημερώσω ότι μόλις δημιουργήθηκε μία νέα αγγελία για την οποία δεν υπάρχει διαθέσιμο email. 
	<br>   
	<h2>Πάτα στο παρακάτω Link για να βρείς διαθέσιμους τρόπους επικοινωνίας:</h2>
	<b>Link Αγγελίας:</b> <i><a href="{0}" target="_blank">{0}</a></i>  
	<br><br>   
	Καλή Τύχη,
	<br>     
	<b><i>Gmail Bot</i></b>   
	<br><br><br>
	<code>Made By Drkostas</code>
	"""

	links_checked = [row["link"] for row in store.get_ads()]
	emails_checked = [row["address"] for row in store.get_ads()]
	print("Waiting for new ads..")
	while True:
		html_dumps = crawl(links_checked)
		new_ads = get_ads_list(html_dumps)

		if len(new_ads)>0:
			links_checked = [row["link"] for row in store.get_ads()]
			emails_checked = [row["address"] for row in store.get_ads()]
			# For each ad
			for link, email in new_ads.items():
				# If not already applied on this link or email
				if link not in links_checked and (email not in emails_checked or email=="No_Email"):
					# If there was no email available
					if email=="No_Email":
						# Email User that the ad has no available email
						print("Link ({}) has no email. Inform User.".format(link))
						noEmailInform_msg = Message(emailSubject_yourname_noEmailInform,to=yourname_email,html=emailText_yourname_noEmailInform.format(link))
						gmail.send(noEmailInform_msg)
					# If the ad is a duplicate
					elif email=="Exists":
						# Ignore
						print("Link ({}) has email we already found in the new ads list.".format(link))
					# Apply to the job
					else:
						# Wait a minute before sending the email (otherwise it will be suspicious)
						time.sleep(60)
						# Email to the ad
						print("Sending email to: {}. Ad Link: {}".format(email, link))					
						ad_msg = Message(emailSubject_ad,to=email,html=emailText_ad, attachments=['attachments/Your-CV.pdf'])
						gmail.send(ad_msg)

						# Inform User
						inform_msg = Message(emailSubject_yourname_inform,to=yourname_email,html=emailText_yourname_inform.format(email, link))
						gmail.send(inform_msg)

					email_info = {"link":link, "address":email, "sent_on": datetime.utcnow().isoformat()}
					store.store_ads(email_info)
					print("Waiting for new ads..")

		# Look for new ads every 2 minutes
		time.sleep(120)


if __name__ == '__main__':
	if len(sys.argv)==1:
		sys.exit(main())
	elif len(sys.argv)==2 and sys.argv[1]=="list":
		show_ads_checked()
	elif len(sys.argv)==3 and sys.argv[1]=="remove":
		store.remove_ad({"id":sys.argv[2]})
	else:
		sys.exit("Wrong argument give. Use `list`, `remove ID_NUMBER` or nothing")