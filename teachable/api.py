import requests
import json
import sys
import shelve
import os.path
import time
import configparser as cfgp
import logging
from teachable.school import School
from teachable.user import User
import re


class TeachableAPI:
    siteUrl = None
    session = None
    cachedData = None
    URL_COURSES = '/api/v1/courses'
    URL_GET_ALL_USERS = '/api/v1/users'
    URL_SCHOOL_INFO = '/api/v1/school'
    URL_FIND_USER = '/api/v1/users?name_or_email_cont='
    URL_REPORT_CARD = '/api/v1/users/USER_ID/report_card'
    URL_COURSE_REPORT = '/api/v1/users/USER_ID/course_report'
    URL_CURRICULUM = '/api/v1/courses/COURSE_ID/curriculum'
    URL_FIND_COURSE = '/api/v1/courses?name_cont='
    URL_COURSE_PRODUCTS = '/api/v1/courses/COURSE_ID/products'
    URL_IMPORT_USERS = '/api/v1/import/users'
    URL_ENROLLMENTS_USER = '/api/v1/users/USER_ID/enrollments'
    URL_LEADERBOARD = '/api/v1/courses/COURSE_ID/leaderboard.csv?page=1&per=PER_PAGE'
    URL_COURSE_PROGRESS = '/api/v1/course_progresses?user_id=USER_ID' # no idea what does it do
    URL_PAGES_CERTIFICATE = '/api/v1/pages?feature=certificate' # no idea what does it do
    URL_ENROLL_USER = '/api/v1/users/USER_ID/enrollments/COURSE_ID' #
#    -data-binary '{"course_id":int,"user_id":int}' \
    URL_ENROLLED_USER = '/admin/users/USER_ID/enrolled'
    URL_UNENROLL_USER = '/api/v1/enrollments/unenroll'

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.logger = logging.getLogger('TeachableAPI')
        self.prepareSession()
        self.expire_cache(os.path.join(dir_path, self.cache_file))
        self.prepareCache(os.path.join(dir_path, self.cache_file))
        self.usecache = True
        self._school = None
        self._courses = None

    def __del__(self):
        if self.cachedData:
            self.cachedData.sync()
            self.cachedData.close()
        if self.notif_status:
            self.notif_status.sync()
            self.notif_status.close()


    def get_config(self, configfile):
        """Gets config options"""
        if os.path.exists(configfile):
            config = cfgp.ConfigParser()
            config.read(configfile)
        else:
            self.logger.error('Missing config.ini file with login data (tried to find {})'.format(configfile))
            config = None
        return config

    def check_email(self, email):
        check = self.email_regex.fullmatch(email)
        if not check:
            self.logger.error('{} is not a valid email'.format(email))
        return check

    def prepareSession(self):
        conf_file = os.path.join(sys.prefix, 'etc', 'config.ini')
        self.config = self.get_config(conf_file)
        if self.config:
            defaults = self.config['DEFAULT']
            username = defaults['username']
            password = defaults['password']
            site_url = defaults['site_url']
            notifications_db = defaults['notifications_db']
            self.siteUrl = site_url
            self.email_regex = re.compile(defaults['email_regex'])
            self.session = requests.Session()
            self.session.auth = (username, password)
            self.cache_expire = defaults['cache_expire']
            self.cache_file = defaults['cache_file']
            # self.session.headers.update({'x-test': 'true'})
            self.session.headers.update({'Origin': site_url})
            self._school = None
            self.notif_status = shelve.open(notifications_db)
        else:
            sys.exit(1)


    def prepareCache(self, CACHE_PATH):
        self.logger.debug('Using cache {}'.format(CACHE_PATH))
        self.cachedData = shelve.open(CACHE_PATH)


    def expire_cache(self,CACHE_PATH):
        if os.path.isfile(CACHE_PATH):
            cache_antiquity = time.time() - os.path.getctime(CACHE_PATH)
            MAXIMUM_CACHE_DURATION = 60 * 60 * 24 * int(self.cache_expire)  # One day (rate limits
            #                                            are not that
            #                                            aggressive I hope)
            if cache_antiquity > MAXIMUM_CACHE_DURATION:
                os.remove(CACHE_PATH)
                self.logger.warning('Cache file dumped!')
    @property
    def school(self):
        if not self._school:
            self._school = School.School(self)
        return self._school

    @property
    def courses(self):
        if not self._courses:
            self._courses = self.school.courses
        return self._courses

    def getLeaderboardCSV(self, course, filename):
        '''Gets a course JSON dict as input'''
        PER_PAGE = '100000' # includes in the leaderboard CSV as many as PER_PAGE users
        courseId = course.get('id')
        course_name = course.get('name')
        path = self.URL_LEADERBOARD.replace('COURSE_ID',str(courseId)).replace('PER_PAGE',str(PER_PAGE))
        fullUrl = self.siteUrl + path
        r = self.session.get(fullUrl, allow_redirects=True)
        if filename == '':
            filename = 'leaderboard_{course}.csv'.format(course=course_name)
        open(filename, 'wb').write(r.content)

    def getUserCoursesReport(self,userId):
        path = self.URL_COURSE_REPORT.replace('USER_ID',str(userId))
        return self._getJsonAt(path, True).get('report')

    def getCourseSections(self, courseId):
        url_course_curriculum = self.URL_CURRICULUM.replace('COURSE_ID', str(courseId))
        return self._getJsonAt(url_course_curriculum).get('lecture_sections')

    def getCourseList(self):
        course_info = self._getJsonAt(self.URL_COURSES)
        return course_info.get('courses')

    def getSchoolInfo(self):
        school_info = self._getJsonAt(self.URL_SCHOOL_INFO)
        return school_info

    def findUser(self, email):
        '''Searches for a specific user, the API uses the same endpoint, for
        one or many'''
        userList = self._getJsonAt(self.URL_FIND_USER + email).get('users')
        if len(userList) == 0:
            return None
        else:
            return userList[0]

    def findMultiUser(self, email):
        '''Searches for multiple users, the API uses the same endpoint for one
        or many'''
        userList = self._getJsonAt(self.URL_FIND_USER + email).get('users')
        if len(userList) == 0:
            return None
        else:
            return userList

    def getAllUsers(self):
        userList = self._getJsonAt(self.URL_GET_ALL_USERS).get('users')
        if len(userList) == 0:
            return None
        else:
            return userList

    def _getAllUsers(self):
        userList = self._getJsonAt(self.URL_GET_ALL_USERS).get('users')
        if len(userList) == 0:
            return None
        else:
            return [User.User(self, user['email']) for user in userList]

    def _get_last_notif(self, email):
        """Returns the notification status dict"""
        try:
            notified = self.notif_status[email]
            logger.debug('{} was sent a notification last time on {}'.format(user_mail, notified))
        except KeyError:
            logger.debug('{} was never sent a notification'.format(user_mail))
            notified = datetime.date(1970, 1, 1)
        return notified

    def findCourses(self, course):
        '''Searches for courses containing the specific text'''
        courseList = self._getJsonAt(self.URL_FIND_COURSE +
                     course).get('courses')
        if len(courseList) == 0:
            return None
        else:
            return courseList

    def getCoursePrice(self,courseId):
        products = self.getCourseProducts(courseId)
        if len(products) > 0:
            return products[0].get('price')
        else:
            return 0

    def getCourseProducts(self, courseId):
        path = self.URL_COURSE_PRODUCTS.replace('COURSE_ID', str(courseId))
        result = self._getJsonAt(path)
        return result.get('products')

    def getUserReportCard(self,userId):
        '''Gets the full report card fot userId, returning the full list of
        lessons the user has completed'''
        path = self.URL_REPORT_CARD.replace('USER_ID',str(userId))
        return self._getJsonAt(path)

    def addUsersToSchool(self, usersArray, courseId):
        usersJsonArray = []
        for userRow in usersArray:
            if self.check_email(userRow['email']):
                userJson = {
                    "email":userRow['email'],
                    "name":userRow['fullname'],
                    "password":None,
                    "role":"student",
                    "course_id":courseId,
                    "unsubscribe_from_marketing_emails":'false'
                }
                usersJsonArray.append(userJson)
        payload = {
            "user_list" :usersJsonArray,
            "course_id": courseId,
            "coupon_code": None,
            "users_role": "student",
            "author_bio_data": {}
        }
        resp = self._postJsonAt(self.URL_IMPORT_USERS, json.dumps(payload))
        return json.loads(resp)

    def addUserToSchool(self, userdict, courseId):
        usersJsonArray =[]
        if self.check_email(userdict['email']):
            userJson = {
                "email":userdict['email'],
                "name":userdict['fullname'],
                "password":None,
                "role":"student",
                "course_id":courseId,
                "unsubscribe_from_marketing_emails":'false'
            }
            usersJsonArray.append(userJson)
        payload = {
            "user_list" :usersJsonArray,
            "course_id": courseId,
            "coupon_code": None,
            "users_role": "student",
            "author_bio_data": {}
        }
        resp = self._postJsonAt(self.URL_IMPORT_USERS, json.dumps(payload))
        return json.loads(resp)

    def _addUserToSchool(self, user, courseId=None):
        usersJsonArray =[]
        if self.check_email(user.email):
            userJson = {
                "email":user.email,
                "name":user.name,
                "password":None,
                "role":"student",
                "unsubscribe_from_marketing_emails":'false'
            }
            if courseId:
                userJson["course_id"] = courseId
            usersJsonArray.append(userJson)
        payload = {
            "user_list" :usersJsonArray,
            "coupon_code": None,
            "users_role": "student",
            "author_bio_data": {}
        }
        if courseId:
           payload["course_id"] = courseId
        resp = self._postJsonAt(self.URL_IMPORT_USERS, json.dumps(payload))
        return json.loads(resp)

    def enrollUsersToCourse(self, userIdArray, courseId):
        responses = []
        for userRow in userIdArray:
            response = self.enrollUserToCourse(str(userRow[0]))
            responses.append(response)
        return responses

    def enrollUserToCourse(self, userId, courseId):
        path = self.URL_ENROLLMENTS_USER.replace('USER_ID', str(userId))
        jsonBody = json.dumps({"course_id": int(courseId)})
        response = self._postJsonAt(path, jsonBody)
        # Now refreshing the status in the cache
        self.usecache = False
        self.getEnrolledCourses(userId)
        self.usecache = True
        if response:
            return json.loads(response)
        else:
            return response

    def unenrollUserFromCourse(self, userId, courseId):
        path = self.URL_UNENROLL_USER
        jsonBody = json.dumps({"course_id":int(courseId),"user_id":int(userId)})
        response = self._putJsonAt(path,jsonBody)
        # updating also the cache for the enrolled courses
        self.usecache = False
        self.getEnrolledCourses(userId)
        self.usecache = True
        if response:
            return json.loads(response)
        else:
            return response

    def getEnrolledCourses(self, userId):
        "Gets the courses the user is enrolled in"
        path = self.URL_ENROLLMENTS_USER.replace('USER_ID', str(userId))
        return self._getJsonAt(path).get('enrollments')
        #return [p['course_id'] for p in response if 'course_id' in p
        #        and p['is_active'] == True]


    def checkEnrollmentToCourse(self, userId, courseId):
        "Check is a user is enrolled in a specific course"
        courses = self.getEnrolledCourses(userId)
        return int(courseId) in [p['course_id'] for p in courses if 'course_id' in p and p['is_active'] == True]

    def _getJsonAt(self, path):
        if self.usecache and path in self.cachedData:
            self.logger.info(("Found cached data for " + path))
            return self.cachedData[path]
        else:
            fullUrl = self.siteUrl + path
            self.logger.debug(("Downloading data from " + fullUrl))
            jsonData = self.session.get(fullUrl).json()
            if jsonData.get('error'):
                self.logger.error('Check Teachable credentials')
                sys.exit(1)
            self.logger.debug('Updating cache data for ' + path)
            self.cachedData[path] = jsonData
            return jsonData

    def _postJsonAt(self, path, jsonBody):
        fullUrl = self.siteUrl + path
        self.logger.debug(("Uploading POST data to " + fullUrl))
        self.logger.debug("JSON Body : " + jsonBody)
        jsonTxt = json.loads(jsonBody)
        self.session.headers.update({'Content-Type': 'application/json;charset=UTF-8'})
        self.logger.debug((json.dumps(jsonTxt, sort_keys=True, indent=4, separators=(',', ': '))))
        jsonResponseBody = self.session.post(fullUrl, data=jsonBody)
        return jsonResponseBody.text

    def _putJsonAt(self, path, jsonBody):
        fullUrl = self.siteUrl + path
        self.logger.debug(("Uploading PUT data to " + fullUrl))
        self.logger.debug("JSON Body : " + jsonBody)
        jsonTxt = json.loads(jsonBody)
        self.session.headers.update({'Content-Type': 'application/json;charset=UTF-8'})
        self.logger.debug((json.dumps(jsonTxt, sort_keys=True, indent=4, separators=(',', ': '))))
        jsonResponseBody = self.session.put(fullUrl, data=jsonBody)
        return jsonResponseBody.text
