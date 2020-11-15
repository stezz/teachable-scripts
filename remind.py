# coding: utf8
import logging
import logging.config
logging.config.fileConfig(fname='logconf.ini', disable_existing_loggers=False)
logger = logging.getLogger(__name__)
import argparse
import datetime
import configparser as cfgp
from email_utils import EmailConnection, Email, render_template
from email.header import Header
from email.utils import formataddr
import os.path
from User import User
from TeachableAPI import TeachableAPI
from School import School
import pytablewriter as ptw


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Polls Teachable and sends
    reminders to those that haven't started a course or haven't done a lesson
    in a week.''')

    parser.add_argument('--dryrun', '-d', action='store_true',
    default='False', help='''Don't send the messages for real, just do a dry
    run''')

    args = parser.parse_args()
    return args

def get_config(configfile):
    if os.path.exists(configfile):
        config = cfgp.ConfigParser()
        config.read(configfile)
        return config
    else:
        logger.error('Missing config.ini file with login data')
        sys.exit(1)

def main():
    config = get_config('./config.ini')
    defaults = config['DEFAULT']
    username = defaults['username']
    password = defaults['password']
    site_url = defaults['site_url']
    smtp_pwd = defaults['smtp_pwd']
    smtp_user = defaults['smtp_user']
    smtp_port = defaults['smtp_port']
    smtp_server = defaults['smtp_server']
    smtp_from = defaults['smtp_from']

    now = datetime.datetime.now()
    alert_days_int = int(defaults['alert_days'])
    logger.info('Connecting to server...')
    server_str = smtp_server+':'+str(smtp_port)
    server = EmailConnection(server_str, smtp_user, smtp_pwd)
    api = TeachableAPI()
    school = School(api)
    logging.debug('This is just for checking the log levels')

    for section in config.keys():
        if section != 'DEFAULT':
            data = []
            warn_students = []
            users_mails = [x.get('email') for x in api.findMultiUser(config[section]['emailsearch'])]
            # First send a reminder to all that need it
            for user_mail in users_mails:
                user = User(api, user_mail)
                summary_stats = user.getSummaryStats(school, int(config[section]['course_id']))
                # Saves the overall stats separately
                data += summary_stats
                if summary_stats:
                    name, email_addr, course, updated_at, completed, days_since = summary_stats[0]
                    if completed == 0 or days_since > int(config[section]['warning']):
                        warn_students += summary_stats
                    message = ''
                    updated_at = datetime.datetime.strptime(updated_at,"%Y-%m-%d %H:%M:%S")
                    completed = int(completed)
                    firstname = name.split()[0]
                    from_addr = formataddr((smtp_from, smtp_user))
                    to_addr = formataddr((name, email_addr))
                    cc_addr = None
                    msg_dict = {'firstname':firstname, 'days_since':days_since, 'course':course,
                                'date':updated_at, 'url':site_url, 'name_from':smtp_from}
                    if days_since > alert_days_int and completed > 0 and completed < 99:
                        subject ='Don\'t forget the {course} course'.format(course=course)
                        message = render_template('email_inactive.txt', msg_dict)
                    elif completed == 0 and days_since > alert_days_int:
                        subject ='Don\'t forget the {course} course'.format(course=course)
                        message = render_template('email_notstarted.txt', msg_dict)
                    if message:
                        logger.info('Preparing the message for '+to_addr)
                        #print(message)
                        mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
                          subject=subject, message=message)
                        if args.dryrun != True:
                            logger.info('Sending...')
                            server.send(mail, bcc=smtp_user)
                    else:
                        logger.info('No reminder for '+to_addr)
            if data:
                # Now send the overall stats to the specified contact person
                headers = ['User', 'Email', 'Course', 'Updated at', 'Completed (%)', 'Days since last lesson']
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
                    #print(warn_text)
                else:
                    warn_text = ''
                msg_dict = {'firstname':firstname, 'course':course,
                'name_from':smtp_from, 'warn_text':warn_text}
                subject ='Weekly report for {course} course'.format(course=course)
                message = render_template('weekly_report.html', msg_dict)
                logger.info('Preparing the message for '+to_addr)
                #print(message)
                mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
                  message_type='html', subject=subject, message=message,
                  attachments=[ofile])
                if args.dryrun != True:
                    logger.info('Sending...')
                    server.send(mail, bcc=smtp_user)

    server.close()

if __name__ == '__main__':
    args = parse_arguments()
    main()
