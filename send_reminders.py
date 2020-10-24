# coding: utf8
import argparse
import datetime
from secrets import site_url, smtp_user, smtp_pwd, smtp_server, smtp_from, smtp_user, smtp_port
from email_utils import EmailConnection, Email
import csv


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
        name = row.get('User')
        email = row.get('Email')
        course = row.get('Course')
        updated_at = datetime.datetime.strptime(row.get('Updated at'),
        "%Y-%m-%dT%H:%M:%SZ")
        completed = int(row.get('Completed (%)'))
        firstname = name.split()[0]
        if updated_at < week_ago and completed > 0:
            message ='''Hey {firstname},

it seems like it's been at least a week since you haven't logged in to the {course} course.

According to our records you have completed the last lesson on {date}.

Please make sure to reserve some time to go through the training next week ;)

You can access the course from the school page at {url}

Happy learning!
--
{name_from}'''.format(firstname=firstname, course=course, date=updated_at, url=site_url, name_from=smtp_from)
            subject ='Don\'t forget the {course} course'.format(course=course)
            print('Preparing the email to {name} <{email}>...'.format(name=name, email=email))
            mail = Email(from_='"%s" <%s>' % (smtp_from, smtp_user), #you can pass only email
              to='"%s" <%s>' % (name, email), #you can pass only email
              cc='"%s" <%s>' % (smtp_from, smtp_user),
              subject=subject, message=message)
            print('Sending...')
            server.send(mail)
            #print(message)
        elif completed == 0:
            message ='''Hey {firstname},

it seems like you have never taken any lesson of the {course} course.

Please make sure to reserve some time to go through the training next week ;)

You can access the course from the school page at {url}

Happy learning!
--
{name_from}'''.format(firstname=firstname, course=course, url=site_url, name_from=smtp_from)
            subject ='Don\'t forget the {course} course'.format(course=course)
            print('Preparing the email to {name} <{email}>...'.format(name=name, email=email))
            mail = Email(from_='"%s" <%s>' % (smtp_from, smtp_user), #you can pass only email
              to='"%s" <%s>' % (name, email), #you can pass only email
              cc='"%s" <%s>' % (smtp_from, smtp_user),
              subject=subject, message=message)
            print('Sending...')
            server.send(mail)
            #print(message)

server.close()
