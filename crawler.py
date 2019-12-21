# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse
import re
import sys
from unidecode import unidecode

# Function For Extracting Html Link
def link(html_data):
    # Filtering Url links

    # Anchor to the ad link
    pattern = re.compile(r'(<a class=\"highlight\".*?>)')    
    a_tag_captured = pattern.findall(html_data)
    for i in a_tag_captured:
        href_raw=i[str(i).find('href'):]
        href=href_raw[:href_raw.find(' ')]
        yield href[6:-1]
    return

# Function For Downloading Html
def retrieve_html(url):
    try:
        # print("[*] Downloading Html Codes ... ")
        header={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0 Iceweasel/31.8.0'}
        req=urllib.request.Request(url, headers=header)
        page = urllib.request.urlopen(req).read()
    except Exception as e:
        print(e)
        page='None'
    if type(page) is not str:
        page = page.decode('utf-8')    
    return page


def crawl(ads_checked):
	# Search params
    params = urllib.parse.urlencode({"Item.category__hierarchy":"139082",
                                    "Item.master_type":"139097",
                                    "System.item_type":"xe_stelexos",
                                    "Publication.freetext":"YOUR SEARCH TEXT", # Change this
                                    "Transaction.type_channel":"117538",
                                    "sort_by":"Publication.effective_date_start",
                                    "sort_direction":"desc",
                                    "per_page":"15"})
    page_link = "http://www.xe.gr/search?%s" % params
    # print(page_link)
    html_dumps = list()
    for sub_url in link(retrieve_html(page_link)):
        sub_url = "http://www.xe.gr" + sub_url
        if sub_url not in ads_checked:
            html = retrieve_html(sub_url)

            # Ignore ads with these words
            words_to_avoid = ["word1", "word2", "word3", "word4", "word5"]
            if any(unidecode(word).lower() in unidecode(html) for word in words_to_avoid):
                continue  
            html_dumps.append((sub_url, html))

    return html_dumps
