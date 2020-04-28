import traceback
import logging
import logging.handlers
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
                            logging.handlers.TimedRotatingFileHandler(log_filename, when='midnight', interval=1),
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
    optional.add_argument('--test-mode', action='store_true',
                          help='enables the test mode which sends all emails to self')
    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    # Parse args
    parsed_args = parser.parse_args()
    if parsed_args.email_id is None and parsed_args.run_mode == 'remove_email':
        raise argparse.ArgumentTypeError('--run-mode = parsed_args requires --email-id to be set!')
    return parsed_args


def init_main() -> Tuple[argparse.Namespace, JobBotMySqlDatastore, JobBotDropboxCloudstore, GmailEmailApp, List]:
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
    email_app = GmailEmailApp(email_address=gmail_configuration['email_address'],
                              api_key=gmail_configuration['api_key'],
                              test_mode=args.test_mode)
    return args, data_store, cloud_store, email_app, ['cv.pdf', 'cover_letter.pdf']


def show_ads_checked(ads: List[Dict]) -> None:
    """
    Pretty prints the list of emails sent.

    :params ads:
    """

    print("{}".format("_" * 146))
    print("|{:-^6}|{:-^80}|{:-^40}|{:-^15}|".format('ID', 'Link', 'Email', 'Sent On'))
    for ad in ads:
        print("|{:^6}|{:^80}|{:^40}|{:^15}|".format(ad[0], ad[1], str(ad[2]), arrow.get(ad[3]).humanize()))
    print("|{}|".format("_" * 144))


def crawl_and_send_loop(data_store: JobBotMySqlDatastore,
                        cloud_store: JobBotDropboxCloudstore,
                        email_app: GmailEmailApp,
                        attachment_names: List) -> None:
    """
    The main loop.
    Crawls the ad site for new ads and sends emails where applicable and informs the applicant.

    :params data_store:
    :params cloud_store:
    :params gmail_app:
    """

    attachments_paths = [os.path.join('attachments', attachment_name) for attachment_name in attachment_names]
    # Get the email_data, the attachments and the stop_words list from the cloudstore
    ad_site_crawler = XeGrAdSiteCrawler(stop_words=cloud_store.get_stop_words())
    application_sent_subject, application_sent_html = cloud_store.get_application_sent_email_data()
    inform_should_call_subject, inform_should_call_html = cloud_store.get_inform_should_call_email_data()
    inform_success_subject, inform_success_html = cloud_store.get_inform_success_email_data()
    cloud_store.download_attachments(attachment_names=attachment_names, to_path='attachments')
    url_search_params = cloud_store.get_url_search_params()

    links_checked = [row["link"] for row in data_store.get_applications_sent()]
    logger.info("Waiting for new ads..")
    while True:
        new_ads = ad_site_crawler.get_new_ads(url_search_params=url_search_params, ads_checked=links_checked)

        if len(new_ads) > 0:
            links_checked = [row["link"] for row in data_store.get_applications_sent()]
            emails_checked = [row["address"] for row in data_store.get_applications_sent()]
            for link, email in new_ads.items():
                if link not in links_checked and (email not in emails_checked or email is None):
                    if email is None:
                        # Email applicant that he/should call manually
                        logger.info("Link ({}) has no email. Inform Maria.".format(link))
                        email_app.send_email(subject=inform_should_call_subject,
                                             html=inform_should_call_html.format(link),
                                             to=email_app.get_self_email())
                    else:
                        # Send application after 1 minute (don't be too cocky)
                        time.sleep(60)
                        logger.info("Sending email to: {}. Ad Link: {}".format(email, link))
                        email_app.send_email(subject=application_sent_subject,
                                             html=application_sent_html.format(link),
                                             to=email,
                                             attachments=attachments_paths)

                        # Inform applicant that an application has been sent successfully
                        email_app.send_email(subject=inform_success_subject,
                                             html=inform_success_html.format(email, link),
                                             to=email_app.get_self_email())

                    email_info = {"link": link, "address": email, "sent_on": datetime.datetime.utcnow().isoformat()}
                    data_store.save_sent_application(email_info)
                    logger.info("Waiting for new ads..")


def main():
    """
    :Example:
    python main.py [-m crawl_and_send]
                   -c confs/template_conf.yml
                   -l logs/output.log
    """

    # Initializing
    args, data_store, cloud_store, email_app, attachment_names = init_main()

    # Start in the specified mode
    if args.run_mode == 'list_emails':
        show_ads_checked(ads=data_store.get_applications_sent())
    elif args.run_mode == 'remove_email':
        data_store.remove_ad(email_id=args.email_id)
    elif args.run_mode == 'crawl_and_send':
        crawl_and_send_loop(data_store=data_store, cloud_store=cloud_store, email_app=email_app,
                            attachment_names=attachment_names)
    else:
        logger.error('Incorrect run_mode specified!')
        raise argparse.ArgumentTypeError('Incorrect run_mode specified!')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(str(e) + '\n' + str(traceback.format_exc()))
        raise e
