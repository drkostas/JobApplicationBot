import traceback
import logging
import argparse
import time
import datetime
from typing import List, Dict, Tuple
import os
import arrow

from configuration.configuration import Configuration
from datastore.job_bot_mysql_datastore import JobBotMySqlDatastore
from cloudstore.job_bot_dropbox_cloudstore import JobBotDropboxCloudstore
from email_app.gmail_email_app import GmailEmailApp
from ad_site_crawler.xegr_ad_site_crawler import XeGrAdSiteCrawler

logger = logging.getLogger('Main')


def _setup_log(log_path: str = 'logs/output.log', debug: bool = False) -> None:
    log_path = log_path.split(os.sep)
    if len(log_path) > 1:

        try:
            os.makedirs((os.sep.join(log_path[:-1])))
        except FileExistsError:
            pass
    log_filename = os.sep.join(log_path)
    # noinspection PyArgumentList
    logging.basicConfig(level=logging.INFO if debug is not True else logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        handlers=[
                            logging.FileHandler(log_filename),
                            # logging.handlers.TimedRotatingFileHandler(log_filename, when='midnight', interval=1),
                            logging.StreamHandler()
                        ]
                        )


def _argparser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='A template for python projects.',
        add_help=False)
    # Required Args
    required_arguments = parser.add_argument_group('required arguments')
    config_file_params = {
        'type': argparse.FileType('r'),
        'required': True,
        'help': "The configuration yml file"
    }
    required_arguments.add_argument('-m', '--run-mode', choices=['crawl_and_send', 'list_emails', 'remove_email'],
                                    required=True,
                                    default='crawl_and_send')
    required_arguments.add_argument('-c', '--config-file', **config_file_params)
    required_arguments.add_argument('-l', '--log', help="Name of the output log file")
    # Optional args
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument('--email-id', help='the id of the email you want to be deleted')
    optional.add_argument('-d', '--debug', action='store_true', help='enables the debug log messages')
    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    return parser.parse_args()


def init_main() -> Tuple[argparse.Namespace, JobBotMySqlDatastore, JobBotDropboxCloudstore, GmailEmailApp]:
    args = _argparser()
    _setup_log(args.log, args.debug)
    logger.info("Starting in run mode: {0}".format(args.run_mode))
    # Load the configuration
    configuration = Configuration(config_src=args.config_file)
    # Init the Datastore
    data_store = JobBotMySqlDatastore(**configuration.get_datastores()[0])
    # Init the Cloudstore
    cloud_store = JobBotDropboxCloudstore(api_key=configuration.get_cloudstores()[0]['api_key'])
    # Init the Email App
    gmail_configuration = configuration.get_email_apps()[0]
    gmail_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                              api_key=gmail_configuration['api_key'])
    return args, data_store, cloud_store, gmail_app


def show_ads_checked(ads: List[Dict]) -> None:
    print("{}".format("_" * 146))
    print("|{:-^6}|{:-^80}|{:-^40}|{:-^15}|".format('ID', 'Link', 'Email', 'Sent On'))
    for ad in ads:
        print("|{:^6}|{:^80}|{:^40}|{:^15}|".format(ad['id'], ad['link'], str(ad['address']),
                                                    arrow.get(ad['sent_on']).humanize()))
    print("|{}|".format("_" * 144))


def crawl_and_send_loop(data_store: JobBotMySqlDatastore,
                        cloud_store: JobBotDropboxCloudstore,
                        gmail_app: GmailEmailApp) -> None:
    stop_words = cloud_store.get_stop_words()
    url_search_params = cloud_store.get_url_search_params()
    ad_site_crawler = XeGrAdSiteCrawler(
        stop_words=stop_words,
        url_search_params=url_search_params)
    application_subject, application_html = cloud_store.get_application_email()
    inform_should_call_subject, inform_should_call_html = cloud_store.get_inform_should_call_email()
    inform_success_subject, inform_success_html = cloud_store.get_inform_success_email()

    links_checked = [row["link"] for row in data_store.get_ads()]
    emails_checked = [row["address"] for row in data_store.get_ads()]
    logger.info("Waiting for new ads..")
    while True:
        html_dumps = ad_site_crawler.crawl(links_checked)
        new_ads = ad_site_crawler.get_ads_list(html_dumps)

        if len(new_ads) > 0:
            links_checked = [row["link"] for row in data_store.get_ads()]
            emails_checked = [row["address"] for row in data_store.get_ads()]
            for link, email in new_ads.items():
                if link not in links_checked and (email not in emails_checked or email == "No_Email"):
                    if email == "No_Email":
                        # Email Maria that it has no email
                        logger.info("Link ({}) has no email. Inform Maria.".format(link))
                        gmail_app.send_email(subject=inform_should_call_subject,
                                             html=inform_should_call_html.format(link),
                                             to=gmail_app.get_self_email())
                    elif email == "Exists":
                        # Ignore
                        logger.info("Link ({}) has email we already found in the new ads list.".format(link))
                    else:
                        time.sleep(60)
                        # Email to the ad
                        logger.info("Sending email to: {}. Ad Link: {}".format(email, link))
                        gmail_app.send_email(subject=application_subject,
                                             html=application_html.format(link),
                                             to=email)

                        # Inform Maria
                        gmail_app.send_email(subject=inform_success_subject,
                                             html=inform_success_html.format(email, link),
                                             to=gmail_app.get_self_email())

                    email_info = {"link": link, "address": email, "sent_on": datetime.utcnow().isoformat()}
                    data_store.store_ads(email_info)
                    logger.info("Waiting for new ads..")


def main():
    """
    :Example:
    python main.py [-m crawl_and_send]
                   -c confs/template_conf.yml
                   -l logs/output.log
    """

    # Initializing
    args, data_store, cloud_store, gmail_app = init_main()

    # Start in the specified mode
    if args.run_mode == 'list_emails':
        show_ads_checked(data_store.get_ads())
    elif args.run_mode == 'remove_email':
        data_store.remove_ad(args.email_id)
    elif args.run_mode == 'crawl_and_send':
        crawl_and_send_loop(data_store, cloud_store, gmail_app)
    else:
        logger.error('Incorrect run_mode specified!')
        raise argparse.ArgumentError('Incorrect run_mode specified!')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(str(e) + '\n' + str(traceback.format_exc()))
        raise e
