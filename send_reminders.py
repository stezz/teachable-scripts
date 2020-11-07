# coding: utf8
import argparse
import datetime
import configparser as cfgp
from email_utils import EmailConnection, Email, render_template
import csv
import jinja2
from email.header import Header
from email.utils import formataddr
import os.path

parser = argparse.ArgumentParser(description='''Send reminders to those that
haven't started a course or haven't done a lesson in a week.''')



parser.add_argument('--search', '-s', nargs='?', default='',
help='''Searches specific text in the name of the course''')
parser.add_argument('--csv-file', '-f', default='',
dest='filename', help='''Specify the input CSV file''')
parser.add_argument('--dryrun', '-d', action='store_true', 
default='False', help='''Don't send the messages for real''')

args = parser.parse_args()

def get_config(configfile, section):
    if os.path.exists(configfile):
        config = cfgp.ConfigParser()
        config.read(configfile)
        config_section = config[section]
        return config_section
    else:
        print('Missing config.ini file with login data')
        sys.exit(1)

defaults = get_config('./config.ini', 'DEFAULT')

site_url = defaults['site_url']
smtp_pwd = defaults['smtp_pwd']
smtp_user = defaults['smtp_user']
smtp_port = defaults['smtp_port']
smtp_server = defaults['smtp_server']
smtp_from = defaults['smtp_from']

now = datetime.datetime.now()
week = datetime.timedelta(days=7)
week_ago = now - week
print('Connecting to server...')
server_str = smtp_server+':'+str(smtp_port)
server = EmailConnection(server_str, smtp_user, smtp_pwd)
with open(args.filename) as csvfile:
    csv_reader = csv.DictReader(csvfile, delimiter=',')
    for row in csv_reader:
        message = ''
        name = row.get('User')
        email_addr = row.get('Email')
        course = row.get('Course')
        updated_at = datetime.datetime.strptime(row.get('Updated at'),
        "%Y-%m-%d %H:%M:%S")
        completed = int(row.get('Completed (%)'))
        days_since = (row.get('Days since last lesson'))
        firstname = name.split()[0]
        from_addr = formataddr((smtp_from, smtp_user))
        to_addr = formataddr((name, email_addr))
        cc_addr = None
        #cc_addr = formataddr((smtp_from, smtp_user))
        msg_dict = {'firstname':firstname, 'course':course,
          'date':updated_at, 'url':site_url, 'name_from':smtp_from}
        if updated_at < week_ago and completed > 0 and completed < 99:
            subject ='Don\'t forget the {course} course'.format(course=course)
            message = render_template('email_inactive.txt', msg_dict)
        elif completed == 0:
            subject ='Don\'t forget the {course} course'.format(course=course)
            message = render_template('email_notstarted.txt', msg_dict)
        if message:
            print('Preparing the message for '+to_addr)
            mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
              subject=subject, message=message)
            if args.dryrun != True:
                print('Sending...')
                server.send(mail, bcc=smtp_user)
        else:
            print('No reminder for '+to_addr)

server.close()
