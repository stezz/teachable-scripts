# coding: utf8
import argparse
import datetime
import logging
import logging.config
import sys
from email.utils import formataddr

from ..utils.email_utils import Email
from ..utils.email_utils import EmailConnection

import pytablewriter as ptw

from ..api import Teachable


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Get the latest earning statement as Excel (default) or CSV. 
                            Optionally send them over email to the school owner''')
    parser.add_argument('--email', '-e',
                        action='store_true',
                        default='False', help='''[Optional] Send the statements to the school owner''')
    parser.add_argument('--all', '-a',
                        action='store_true',
                        default='False', help='''[Optional] Get all the statements, not just the last one''')
    parser.add_argument('--format', '-f', nargs='?', default='excel',
                        help='Output format (excel[default], csv)')
    parser.add_argument('--ofile', '-o', nargs='?', default='earnings_statement', help='[Optional] Output file name')

    args = parser.parse_args()
    return args


def statements_app(args):
    api = Teachable()
    logger = logging.getLogger(__name__)
    send_email = args.email
    get_all = args.all
    data = []
    headers = []
    last_statement = api.get_last_statement_date()
    statements = api.get_earning_statements()

    if statements:
        keys = statements[0].keys()
        # Dropping the 'meta' key since we don't need it
        keys = [x for x in keys if not x == 'meta']
    else:
        logger.error('No earning statements available for your school')
        sys.exit(0)

    if get_all is not True:
        # By default we only get the latest statement, which is first in the list
        statements = statements[0:1]

    for row in statements:
        # search if the user with the given email exists
        row_data = []
        for k in keys:
            if k == 'internal_gateway_amount' or \
                    k == 'teachable_payments_amount' or \
                    k == 'custom_gateway_amount' or \
                    k == 'total_amount':
                # For whatever reason this is an int with USD value*100, rather than a str :/
                row_data.append(row[k] / 100)
            else:
                row_data.append(row[k])

        updated = datetime.datetime.strptime(row['updated_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        # When we want all statements we really want all, disregarding the statements_db
        if updated > last_statement or get_all is True:
            logger.debug('New statement found, updated on {}'.format(updated))
            data.append(row_data)
        else:
            logger.debug('This statement was already retrieved, skipping (last statement date: {}'.
                         format(last_statement))

    # Saving the last statement only if we are running in default mode
    if get_all is not True:
        newest = datetime.datetime.strptime(statements[0]['updated_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        api.set_last_statement_date(newest)

    if data:
        for k in keys:
            if k == 'internal_gateway_amount' or \
                    k == 'teachable_payments_amount' or \
                    k == 'custom_gateway_amount' or \
                    k == 'total_amount':
                # Making it explicit that we are talking about amounts in USD
                headers.append(k + '_usd')
            else:
                headers.append(k)

        if args.format == 'csv':
            writer = ptw.CsvTableWriter()
        else:
            writer = ptw.ExcelXlsxTableWriter()
            # Because honestly MS Gothic sucks as a font
            writer.format_table['cell']['font_name'] = 'Calibri'
            writer.format_table['cell']['font_size'] = 12
            writer.format_table['header']['font_name'] = 'Calibri'
            writer.format_table['header']['font_size'] = 12

        writer.table_name = 'Earning Statements Teachable School'
        writer.headers = headers
        writer.value_matrix = data

        if args.format == 'csv':
            ofile = args.ofile + '.csv'
            logger.info('Saving to {}'.format(ofile))
            with open(ofile, 'w') as f:
                f.write(writer.dumps())
            f.close()
        else:
            ofile = args.ofile + '.xlsx'
            logger.info('Saving to {}'.format(ofile))
            writer.dump(ofile)

        if send_email is True:
            config = api.config
            defaults = config['DEFAULT']
            smtp_pwd = defaults['smtp_pwd']
            smtp_user = defaults['smtp_user']
            smtp_port = defaults['smtp_port']
            smtp_server = defaults['smtp_server']
            smtp_from = defaults['smtp_from']

            logger.debug('Connecting to email server ({})'.format(smtp_server))
            server_str = smtp_server + ':' + str(smtp_port)
            server = EmailConnection(server_str, smtp_user, smtp_pwd)

            to_addr = formataddr((smtp_from, smtp_user))
            from_addr = formataddr((smtp_from, smtp_user))
            subject = 'Teachable earning statements'
            message = 'Here the earning statements report.'
            logger.debug('Preparing the message for ' + to_addr)
            mail = Email(from_=from_addr, to=to_addr,
                         message_type='html', subject=subject, message=message,
                         attachments=[ofile], message_encoding="utf-8")
            logger.info('Sending earning statements to {}'.format(to_addr))
            server.send(mail)
            server.close()
    else:
        logger.info('No new statements were found')


def main():
    args = parse_arguments()
    statements_app(args)


if __name__ == '__main__':
    main()
