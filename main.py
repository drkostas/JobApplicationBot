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
        description='A bot that automatically sends emails to new ads posted in the specified xe.gr search page.',
        add_help=False)
    # Required Args
    required_arguments = parser.add_argument_group('required arguments')
    config_file_params = {
        'type': argparse.FileType('r'),
        'required': True,
        'help': "The configuration yml file"
    }
    required_arguments.add_argument('-m', '--run-mode',
                                    choices=['crawl_and_send', 'list_emails', 'remove_email', 'upload_files',
                                             'create_table'],
                                    required=True,
                                    default='crawl_and_send')
    required_arguments.add_argument('-c', '--config-file', **config_file_params)
    required_arguments.add_argument('-l', '--log', help="Name of the output log file")
    # Optional args
    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('--email-id', help='The id of the email you want to be deleted')
    optional.add_argument('-d', '--debug', action='store_true', help='Enables the debug log messages')
    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    # Parse args
    parsed_args = parser.parse_args()
    if parsed_args.email_id is None and parsed_args.run_mode == 'remove_email':
        raise argparse.ArgumentTypeError('--run-mode = remove_email requires --email-id to be set!')
    return parsed_args


def init_main() -> Tuple[argparse.Namespace, Configuration]:
    args = _argparser()
    _setup_log(args.log, args.debug)
    logger.info("Starting in run mode: {0}".format(args.run_mode))
    # Load the configuration
    configuration = Configuration(config_src=args.config_file)

    return args, configuration


def show_ads_checked(ads: List[Tuple]) -> None:
    """
    Pretty prints the list of emails sent.

    :params ads:
    """

    print("{}".format("_" * 146))
    print("|{:-^6}|{:-^80}|{:-^40}|{:-^15}|".format('ID', 'Link', 'Email', 'Sent On'))
    for ad in ads:
        print("|{:^6}|{:^80}|{:^40}|{:^15}|".format(ad[0], ad[1], str(ad[2]), arrow.get(ad[3]).humanize()))
    print("|{}|".format("_" * 144))


def upload_files_to_cloudstore(cloud_store: JobBotDropboxCloudstore):
    cloud_store.update_stop_words_data()
    cloud_store.update_application_to_send_email_data()
    cloud_store.update_inform_should_call_email_data()
    cloud_store.update_inform_success_email_data()
    cloud_store.upload_attachments()


def crawl_and_send_loop(lookup_url: str, check_interval: int, crawl_interval: int, anchor_class_name: str,
                        data_store: JobBotMySqlDatastore,
                        cloud_store: JobBotDropboxCloudstore,
                        email_app: GmailEmailApp) -> None:
    """
    The main loop.
    Crawls the ad site for new ads and sends emails where applicable and informs the applicant.

    :params lookup_url:
    :params check_interval:
    :params data_store:
    :params cloud_store:
    :params gmail_app:
    """

    ad_site_crawler = XeGrAdSiteCrawler(stop_words=cloud_store.get_stop_words_data(),
                                        anchor_class_name=anchor_class_name)
    attachments_local_paths = [os.path.join(cloud_store.local_files_folder, attachment_name)
                               for attachment_name in cloud_store.attachments_names]
    # Get the email_data, the attachments and the stop_words list from the cloudstore
    # cloud_store.download_attachments()
    application_to_send_subject, application_to_send_html = cloud_store.get_application_to_send_email_data()
    inform_should_call_subject, inform_should_call_html = cloud_store.get_inform_should_call_email_data()
    inform_success_subject, inform_success_html = cloud_store.get_inform_success_email_data()

    links_checked = [row[0] for row in data_store.get_applications_sent(columns='link')]
    logger.info("Waiting for new ads..")
    while True:
        new_ads = list(ad_site_crawler.get_new_ads(lookup_url=lookup_url, ads_checked=links_checked,
                                                   crawl_interval=crawl_interval))

        if len(new_ads) > 0:
            links_checked = [row[0] for row in data_store.get_applications_sent(columns='link')]
            emails_checked = [row[0] for row in data_store.get_applications_sent(columns='email')]
            for link, email in new_ads:
                if link not in links_checked and (email not in emails_checked or email is None):
                    if email is None:
                        # Email applicant to inform him that he should call manually
                        logger.info("Link ({}) has no email. Inform the applicant.".format(link))
                        email_app.send_email(subject=inform_should_call_subject,
                                             html=inform_should_call_html.format(link=link),
                                             to=[email_app.get_self_email()])
                    else:
                        # Send application after 1 minute (don't be too cocky)
                        time.sleep(60)
                        logger.info("Sending email to: {}. Ad Link: {}".format(email, link))
                        email_app.send_email(subject=application_to_send_subject,
                                             html=application_to_send_html.format(link),
                                             to=[email],
                                             attachments=attachments_local_paths)

                        # Inform applicant that an application has been sent successfully
                        email_app.send_email(subject=inform_success_subject,
                                             html=inform_success_html.format(email=email, link=link),
                                             to=[email_app.get_self_email()])

                    email_info = {"link": link, "email": email, "sent_on": datetime.datetime.utcnow().isoformat()}
                    data_store.save_sent_application(email_info)
                    logger.info("Waiting for new ads..")

        # Look for new ads every 2 minutes
        logger.debug("Sleeping for {check_interval} seconds..".format(check_interval=check_interval))
        time.sleep(check_interval)


def main():
    """
    :Example:
    python main.py [-m crawl_and_send]
                   -c confs/template_conf.yml
                   -l logs/output.log
    """

    # Initializing
    args, configuration = init_main()

    # Start in the specified mode
    if args.run_mode == 'list_emails':
        data_store = JobBotMySqlDatastore(config=configuration.get_datastores()[0])
        show_ads_checked(ads=data_store.get_applications_sent())
    elif args.run_mode == 'remove_email':
        data_store = JobBotMySqlDatastore(config=configuration.get_datastores()[0])
        data_store.remove_ad(email_id=args.email_id)
    elif args.run_mode == 'upload_files':
        upload_files_to_cloudstore(cloud_store=JobBotDropboxCloudstore(config=configuration.get_cloudstores()[0]))
    elif args.run_mode == 'create_table':
        data_store = JobBotMySqlDatastore(config=configuration.get_datastores()[0])
        data_store.create_applications_sent_table()
    elif args.run_mode == 'crawl_and_send':
        crawl_and_send_loop(lookup_url=configuration.lookup_url,
                            check_interval=configuration.check_interval,
                            crawl_interval=configuration.crawl_interval,
                            anchor_class_name=configuration.anchor_class_name,
                            data_store=JobBotMySqlDatastore(config=configuration.get_datastores()[0]),
                            cloud_store=JobBotDropboxCloudstore(config=configuration.get_cloudstores()[0]),
                            email_app=GmailEmailApp(config=configuration.get_email_apps()[0],
                                                    test_mode=configuration.test_mode))
    else:
        logger.error('Incorrect run_mode specified!')
        raise argparse.ArgumentTypeError('Incorrect run_mode specified!')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(str(e) + '\n' + str(traceback.format_exc()))
        raise e
