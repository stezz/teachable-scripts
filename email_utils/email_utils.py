#!/usr/bin/env python
# coding: utf-8

# This little project is hosted at: <https://gist.github.com/1455741>
# Copyright 2011-2020 Álvaro Justen [alvarojusten at gmail dot com]
# License: GPL <http://www.gnu.org/copyleft/gpl.html>

import os
import sys
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from mimetypes import guess_type
from smtplib import SMTP


def render_template(template, vardict):
    """ renders a Jinja template into HTML """
    # check if template exists
    if not os.path.exists(template):
        print('No template file present: %s' % template)
        sys.exit()

    import jinja2
    template_loader = jinja2.FileSystemLoader(searchpath='/')
    template_env = jinja2.Environment(loader=template_loader)
    templ = template_env.get_template(template)
    return templ.render(vardict)


def get_email(email):
    if '<' in email:
        data = email.split('<')
        email = data[1].split('>')[0].strip()
    return email.strip()


class Email(object):
    def __init__(self, from_, to, subject, message, message_type='plain',
                 attachments=None, cc=None, bcc=None, message_encoding='us-ascii'):
        self.email = MIMEMultipart()
        self.email['From'] = from_
        self.email['To'] = to
        self.email['Subject'] = subject
        self.bcc = bcc
        if cc is not None:
            self.email['Cc'] = cc
        text = MIMEText(message, message_type, message_encoding)
        self.email.attach(text)
        if attachments is not None:
            for filename in attachments:
                mimetype, encoding = guess_type(filename)
                mimetype = mimetype.split('/', 1)
                fp = open(filename, 'rb')
                attachment = MIMEBase(mimetype[0], mimetype[1])
                attachment.set_payload(fp.read())
                fp.close()
                encode_base64(attachment)
                attachment.add_header('Content-Disposition', 'attachment',
                                      filename=os.path.basename(filename))
                self.email.attach(attachment)

    def __str__(self):
        return self.email.as_string()


class EmailConnection(object):
    def __init__(self, server, username, password):
        if ':' in server:
            data = server.split(':')
            self.server = data[0]
            self.port = int(data[1])
        else:
            self.server = server
            self.port = 25
        self.username = username
        self.password = password
        self.connection = SMTP(self.server, self.port)
        self.connect()

    def connect(self):
        self.connection.ehlo()
        self.connection.starttls()
        self.connection.ehlo()
        self.connection.login(self.username, self.password)

    def send(self, message, from_=None, to=None, bcc=None):
        if type(message) == str:
            if from_ is None or to is None:
                raise ValueError('You need to specify `from_` and `to`')
            else:
                from_ = get_email(from_)
                to = get_email(to)
        else:
            from_ = message.email['From']
            if 'Cc' not in message.email:
                message.email['Cc'] = ''
            to_emails = [message.email['To']] + message.email['Cc'].split(',') + [bcc]
            to = [get_email(complete_email) for complete_email in to_emails]
            message = str(message)
        return self.connection.sendmail(from_, to, message)

    def close(self):
        self.connection.close()
