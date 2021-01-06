# coding: utf8
import argparse
import logging

from ..api import Teachable
from ..school import School


def parse_arguments():
    parser = argparse.ArgumentParser(description='''Get a Leaderboard CSV in just
    one command. 
    
    It will save as many leaderboards CSV as you have courses.''')
    parser.add_argument('--search', '-s', nargs='?', default='',
                        help='''Searches specific text in the name of the course''')
    parser.add_argument('--output-file', '-o', nargs='?', default='',
                        dest='filename', help='''Specify the output file''')

    args = parser.parse_args()
    return args


def leaderboard_app(args):
    api = Teachable()
    logger = logging.getLogger(__name__)
    if args.search:
        courses = api.find_courses(args.search)
    else:
        courses = api.find_courses('')

    if courses:
        for course in courses:
            api.get_leaderboard_csv(course, args.filename)
    else:
        logger.info('Sorry no courses found with the term \'{search}\''.format(search=args.search))


def main():
    args = parse_arguments()
    leaderboard_app(args)


if __name__ == '__main__':
    main()
