# -*- coding: utf-8 -*-
import re
import sys

def find_emails(data):
    # Get email addresses from Url
    pattern = re.compile('[\w\-][\w\-\.]+@[\w\-][\w\-\.]+(?:com|gr)', re.MULTILINE)
    captured = pattern.findall(data)
    return captured

def get_ads_list(html_dumps):
    # Collecting Emails
    email_dict = dict()
    for link, data in html_dumps:
        emails_set = set(find_emails(data))
        if bool(emails_set):
            email = emails_set.pop()
            if email in email_dict.values():
                email = "Exists"
        else:
            email = "No_Email"
        email_dict[link] = email 	
    return email_dict
