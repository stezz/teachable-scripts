# coding: utf8
import argparse
import datetime
import logging
import os
import os.path
from email.utils import formataddr

import pytablewriter as ptw

from ..utils.email_utils import Email
from ..utils.email_utils import EmailConnection
from ..utils.email_utils import render_template
from ..api import Teachable
from ..user import User


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Polls Teachable and sends
    reminders to those that haven't started a course or haven't done a lesson
    in a week.''')

    parser.add_argument('--dryrun', '-d', action='store_true',
                        default='False', help='''Don't send the messages for 
                        real, just do a dry run''')

    arguments = parser.parse_args()
    return arguments


def remind_app(args):
    """Main application"""
    api = Teachable()
    logger = logging.getLogger(__name__)
    config = api.config
    #   override_mail = 'stefano.mosconi@britemind.io'
    defaults = config['DEFAULT']
    site_url = defaults['site_url']
    smtp_pwd = defaults['smtp_pwd']
    smtp_user = defaults['smtp_user']
    smtp_port = defaults['smtp_port']
    smtp_server = defaults['smtp_server']
    smtp_from = defaults['smtp_from']
    templates_dir = api.TEACHABLE_TEMPLATES_DIR
    now = datetime.datetime.now()
    logger.info('Connecting to email server ({})'.format(smtp_server))
    server_str = smtp_server + ':' + str(smtp_port)
    server = EmailConnection(server_str, smtp_user, smtp_pwd)
    today = datetime.date.today()

    for section in config.keys():
        if section != 'DEFAULT':
            alert_days_int = int(config[section]['alert_days'])
            warning_days = int(config[section]['warning'])
            notif_freq = int(config[section]['freq'])
            try:
                exclude = config[section]['exclude'].replace(" ","").split(',')
            except KeyError:
                exclude = []
            data = []
            warn_students = []
            users_mails = [x.email for x in api.find_many_users(config[section]['emailsearch']) if x.email not in exclude]
            # First send a reminder to all that need it
            for user_mail in users_mails:
                user = User(api, user_mail)
                since_last_notif = (today - user.notified).days
                summary_stats = user.get_summary_stats(int(config[section]['course_id']))
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
                    # to_addr = formataddr((name, override_mail))
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
                                                  msg_dict)
                    elif not_started:
                        subject = 'Don\'t forget the {course} course'.format(course=course)
                        message = render_template(os.path.join(templates_dir, 'email_notstarted.txt'),
                                                  msg_dict)
                    if message:
                        mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
                                     subject=subject, message=message, message_encoding="utf-8")
                        if since_last_notif >= notif_freq:
                            if args.dryrun is not True:
                                logger.info('Sending mail to {}'.format(to_addr))
                                server.send(mail, bcc=smtp_user)
                                user.notified = today
                            else:
                                logger.info('[DRYRUN] Not sending email to {}'.format(to_addr))
                    else:
                        logger.info('No reminder for ' + to_addr)
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
                # to_addr = formataddr((name, override_mail))
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
                                          msg_dict)
                since_last_notif = (today - api.get_last_notif(email_addr)).days
                logger.info('Preparing the message for ' + to_addr)
                mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
                             message_type='html', subject=subject, message=message,
                             attachments=[ofile], message_encoding="utf-8")
                if args.dryrun is not True:
                    if since_last_notif >= notif_freq:
                        logger.info('Sending report to {}'.format(to_addr))
                        server.send(mail, bcc=smtp_user)
                        api.set_last_notif(email_addr, today)
                else:
                    logger.info('[DRYRUN] Not sending email to {}'.format(to_addr))

    server.close()


def main():
    args = parse_arguments()
    remind_app(args)


if __name__ == '__main__':
    main()
