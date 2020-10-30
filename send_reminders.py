# coding: utf8
import argparse
import datetime
from secrets import site_url, smtp_user, smtp_pwd, smtp_server, smtp_from, smtp_user, smtp_port
from email_utils import EmailConnection, Email, render_template
import csv
import jinja2
from email.header import Header
from email.utils import formataddr

parser = argparse.ArgumentParser(description='''Send reminders to those that
haven't started a course or haven't done a lesson in a week.''')



parser.add_argument('--search', '-s', nargs='?', default='',
help='''Searches specific text in the name of the course''')
parser.add_argument('--csv-file', '-f', default='',
dest='filename', help='''Specify the input CSV file''')

args = parser.parse_args()



now = datetime.datetime.now()
week = datetime.timedelta(days=7)
week_ago = now - week
print('Connecting to server...')
server_str = smtp_server+':'+str(smtp_port)
server = EmailConnection(server_str, smtp_user, smtp_pwd)
with open(args.filename) as csvfile:
    csv_reader = csv.DictReader(csvfile, delimiter=';')
    for row in csv_reader:
        message = ''
        name = row.get('User')
        email_addr = row.get('Email')
        course = row.get('Course')
        updated_at = datetime.datetime.strptime(row.get('Updated at'),
        "%Y-%m-%dT%H:%M:%SZ")
        completed = int(row.get('Completed (%)'))
        firstname = name.split()[0]
        from_addr = formataddr((smtp_from, smtp_user))
        to_addr = formataddr((name, email_addr))
        cc_addr = None
        #cc_addr = formataddr((smtp_from, smtp_user))
        msg_dict = {'firstname':firstname, 'course':course,
          'date':updated_at, 'url':site_url, 'name_from':smtp_from}
        if updated_at < week_ago and completed > 0:
            subject ='Don\'t forget the {course} course'.format(course=course)
            message = render_template('email_inactive.txt', msg_dict)
        elif completed == 0:
            subject ='Don\'t forget the {course} course'.format(course=course)
            message = render_template('email_notstarted.txt', msg_dict)
        if message:
            print('Preparing the message for '+to_addr)
            mail = Email(from_=from_addr, to=to_addr, cc=cc_addr,
              subject=subject, message=message)
            print('Sending...')
            server.send(mail, bcc=smtp_user)
        else:
            print('No reminder for '+to_addr)

server.close()
