# coding: utf8
import argparse
import logging
from ..user import User
from ..api import Teachable
import pytablewriter as ptw


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Get your Teachable students
    report. 
    
    By default it will generate a progress summary report of all the students that
    are enrolled in all your courses. 
    
    This is very similar to using leaderboard.py: while this allows to
    specify a specific set of users, the other one allows to specify a course.
    
    Pay attention if you have a lot of students
    because this will be rate limited at some point''')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--emails', '-e', type=str, nargs='+', default='',
                       help='list of emails (separated by spaces) - cannot be used with -s')
    parser.add_argument('--output_file', '-o', nargs='?', default='teachable_stats', help='Output file')
    group.add_argument('--search', '-s', nargs='?', default='',
                       help='''Searches specific text in name or email. For instance -s @gmail.com or
    -s *@gmail.com will look for all the users that have an email ending in
    @gmail.com. Or -s Jack will look for all the users that have Jack in
    their name (or surname) - cannot be used with -e''')
    parser.add_argument('--format', '-f', nargs='?', default='txt', help='Output format (excel, csv, txt [default])')
    parser.add_argument('--courseid', '-c', nargs='?', default=0, help='''Limit
    search to this course id only (numeric value)''')
    parser.add_argument('--detailed', '-d', action='store_true', default='False',
                        help='Get detailed progress report')

    # parser.add_argument('--hidefree', type=int, default=0, help='0: show/1: hide free courses ')

    args = parser.parse_args()
    return args


def report_app(args):
    # logger.info args

    # HIDE_FREE_COURSES = args.hidefree  # set to 0 to show all

    api = Teachable()
    logger = logging.getLogger(__name__)
    users_mails = []
    if args.emails:
        for email in args.emails:
            users_mails.append(email)

    if args.search:
        users_mails = [x.email for x in api.find_many_users(args.search)]

    if not users_mails:
        users_mails = [x.email for x in api.school.users]

    data = []
    for user_mail in users_mails:
        user = User(api, user_mail)
        if args.detailed is True:
            data += user.get_detailed_stats()
        else:
            data += user.get_summary_stats(int(args.courseid))

    if args.detailed is True:
        headers = ['User', 'Email', 'Date', 'Course', 'Chapter', 'Duration']
    else:
        headers = ['User', 'Email', 'Course', 'Updated at', 'Completed (%)', 'Days since last lesson']

    if args.format == 'csv':
        writer = ptw.CsvTableWriter()
    elif args.format == 'excel':
        writer = ptw.ExcelXlsxTableWriter()
        # Because honestly MS Gothic sucks as a font
        writer.format_table['cell']['font_name'] = 'Calibri'
        writer.format_table['cell']['font_size'] = 12
        writer.format_table['header']['font_name'] = 'Calibri'
        writer.format_table['header']['font_size'] = 12
    else:
        writer = ptw.MarkdownTableWriter()

    writer.table_name = 'Teachable Stats'
    writer.headers = headers
    writer.value_matrix = data

    if args.format == 'csv':
        ofile = args.output_file + '.csv'
        logger.info('Saving to ', ofile)
        with open(ofile, 'w') as f:
            f.write(writer.dumps())
        f.close()
    elif args.format == 'excel':
        ofile = args.output_file + '.xlsx'
        logger.info('Saving to ', ofile)
        writer.dump(ofile)
    else:
        writer.write_table()


def main():
    args = parse_arguments()
    report_app(args)


if __name__ == '__main__':
    main()
