# coding: utf8
import argparse
import datetime
import logging
import logging.config
import os.path
import shelve
import sys
from email.utils import formataddr

import pytablewriter as ptw

from email_utils.email_utils import Email
from email_utils.email_utils import EmailConnection
from email_utils.email_utils import render_template
from teachable.api import TeachableAPI
from teachable.school import School
from teachable.user import User


def setup_logging(logconf):
    if os.path.exists(logconf):
        logging.debug('Found logconf in {}'.format(logconf))
        logging.config.fileConfig(fname=logconf, disable_existing_loggers=False)
        lg = logging.getLogger(__name__)
    else:
        logging.error('Log conf doesn\'t exist [{}]'.format(logconf))
        logging.error('we are in dir {}, sys.prefix={}'.format(os.getcwd(), sys.prefix))
        sys.exit()
    return lg


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Polls Teachable and sends
    reminders to those that haven't started a course or haven't done a lesson
    in a week.''')

    parser.add_argument('--dryrun', '-d', action='store_true',
                        default='False', help='''Don't send the messages for 
                        real, just do a dry run''')

    arguments = parser.parse_args()
    return arguments

def get_last_notif(user_mail, notif_status):
    """Returns the notification status dict"""
    try:
        notified = notif_status[user_mail]
        logger.debug('{} was sent a notification last time on {}'.format(user_mail, notified))
    except KeyError:
        logger.debug('{} was never sent a notification'.format(user_mail))
        notified = datetime.date(1970, 1, 1)
    return notified


logger = setup_logging(os.path.join(sys.prefix, 'etc/logconf.ini'))


def remind_app(args):
    """Main application"""
    api = TeachableAPI()
    school = School(api)
    config = api.config
    defaults = config['DEFAULT']
    site_url = defaults['site_url']
    smtp_pwd = defaults['smtp_pwd']
    smtp_user = defaults['smtp_user']
    smtp_port = defaults['smtp_port']
    smtp_server = defaults['smtp_server']
    smtp_from = defaults['smtp_from']
    notifications_db = defaults['notifications_db']
    templates_dir = os.path.join(sys.prefix, defaults['templates_dir'])

    now = datetime.datetime.now()
    logger.info('Connecting to server...')
    server_str = smtp_server+':'+str(smtp_port)
    server = EmailConnection(server_str, smtp_user, smtp_pwd)
    # notif_status is a dictionary that support several kind of notification
    # types and we store it in a file that is defined in the config
    notif_status = shelve.open(notifications_db)

    today = datetime.date.today()
    logging.debug('This is just for checking the log levels')

    for section in config.keys():
        if section != 'DEFAULT':
            alert_days_int = int(config[section]['alert_days'])
            warning_days = int(config[section]['warning'])
            notif_freq = int(config[section]['freq'])
            data = []
            warn_students = []
            users_mails = [x.get('email') for x in api.findMultiUser(config[section]['emailsearch'])]
            # First send a reminder to all that need it
            for user_mail in users_mails:
                user = User(api, user_mail)
                notified = get_last_notif(user_mail, notif_status)
                since_last_notif = (today - notified).days
                summary_stats = user.getSummaryStats(school, int(config[section]['course_id']))
                # Saves the overall stats separately
                data += summary_stats
                if summary_stats:
                    name, email_addr, course, updated_at, completed, days_since = summary_stats[0]
                    message = ''
                    updated_at = datetime.datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
                    completed = int(completed)
                    firstname = name.split()[0]
                    from_addr = formataddr((smtp_from, smtp_user))
                    to_addr = formataddr((name, email_addr))
                    cc_addr = None
                    msg_dict = {'firstname': firstname, 'days_since': days_since, 'course': course,
                                'date': updated_at, 'url': site_url, 'name_from': smtp_from}
                    not_started = (completed == 0 and days_since > alert_days_int)
                    inactive = (days_since > alert_days_int and completed < 100)
                    flagged = (days_since > warning_days and completed < 100)
                    if not_started or flagged:
                        warn_students += summary_stats
                    if completed > 0 and inactive:
                        subject = 'Don\'t forget the {course} course'.format(course=course)
                        message = render_template(os.path.join(templates_dir, 'email_inactive.txt'),
                                                  msg_dict).encode('utf-8')
                    elif not_started:
                        subject = 'Don\'t forget the {course} course'.format(course=course)
                        message = render_template(os.path.join(templates_dir, 'email_notstarted.txt'),
                                                  msg_dict).encode('utf-8')
                    if message:
                        print(message)
                        mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
                                     subject=subject, message=message)
                        if since_last_notif >= notif_freq:
                            if args.dryrun is not True:
                                logger.info('Sending mail to {}'.format(to_addr))
                                server.send(mail, bcc=smtp_user)
                                notif_status[user_mail] = today
                            else:
                                logger.info('[DRYRUN] Not sending email to {}'.format(to_addr))
                    else:
                        logger.info('No reminder for '+to_addr)
            if data:
                # Now send the overall stats to the specified contact person
                headers = ['User', 'Email', 'Course', 'Updated at',
                           'Completed (%)', 'Days since last lesson']
                writer = ptw.ExcelXlsxTableWriter()
                # Because honestly MS Gothic sucks as a font
                writer.format_table['cell']['font_name'] = 'Calibri'
                writer.format_table['cell']['font_size'] = 12
                writer.format_table['header']['font_name'] = 'Calibri'
                writer.format_table['header']['font_size'] = 12
                writer.table_name = 'Teachable Stats'
                writer.headers = headers
                writer.value_matrix = data
                ofile = section + '_' + str(now.strftime('%d-%m-%y')) + '.xlsx'
                logger.info('Saving report to ' + ofile)
                writer.dump(ofile)
                name = config[section]['contact_name']
                email_addr = config[section]['contact_email']
                firstname = name.split()[0]
                from_addr = formataddr((smtp_from, smtp_user))
                to_addr = formataddr((name, email_addr))
                if warn_students:
                    markup_txt = ptw.HtmlTableWriter()
                    markup_txt.headers = headers
                    markup_txt.value_matrix = warn_students
                    warn_text = markup_txt.dumps()
                else:
                    warn_text = ''
                msg_dict = {'firstname': firstname, 'course': course,
                            'name_from': smtp_from, 'warn_text': warn_text}
                subject = 'Weekly report for {course} course'.format(course=course)
                message = render_template(os.path.join(templates_dir, 'weekly_report.html'),
                                          msg_dict).encode('utf-8')
                notified = get_last_notif(email_addr, notif_status)
                since_last_notif = (today - notified).days
                logger.info('Preparing the message for '+to_addr)
                print(message)
                mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
                             message_type='html', subject=subject, message=message,
                             attachments=[ofile])
                if args.dryrun is not True and since_last_notif >= notif_freq:
                    logger.info('Sending...')
                    server.send(mail, bcc=smtp_user)
                    notif_status[email_addr] = today

    server.close()
    notif_status.sync()
    notif_status.close()

def main():
    args = parse_arguments()
    remind_app(args)


if __name__ == '__main__':
    main()