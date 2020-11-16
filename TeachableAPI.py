import requests
import json
import sys
import shelve
import os.path
import time
import configparser as cfgp
import logging


class TeachableAPI:
    siteUrl = None
    session = None
    cachedData = None
    URL_COURSES = '/api/v1/courses'
    URL_GET_ALL_USERS = '/api/v1/users'
    URL_FIND_USER = '/api/v1/users?name_or_email_cont='
    URL_REPORT_CARD = '/api/v1/users/USER_ID/report_card'
    URL_COURSE_REPORT = '/api/v1/users/USER_ID/course_report'
    URL_CURRICULUM = '/api/v1/courses/COURSE_ID/curriculum'
    URL_FIND_COURSE = '/api/v1/courses?name_cont='
    URL_COURSE_PRODUCTS = '/api/v1/courses/COURSE_ID/products'
    URL_IMPORT_USERS = '/api/v1/import/users'
    URL_ENROLL_USER = '/api/v1/users/USER_ID/enrollments'
    URL_LEADERBOARD = '/api/v1/courses/COURSE_ID/leaderboard.csv?page=1&per=PER_PAGE'
    URL_UNENROLL_USER = '/api/v1/enrollments/unenroll' #
#    -data-binary '{"course_id":int,"user_id":int}' \

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.prepareSession(dir_path + '/config.ini')
        self.expire_cache(dir_path + '/teachable_cache.out')
        self.prepareCache(dir_path + '/teachable_cache.out')
        self.logger = logging.getLogger('TeachableAPI')

    def __del__(self):
        if self.cachedData:
            self.cachedData.close()


    def prepareSession(self, configfile):
        if os.path.exists(configfile):
            config = cfgp.ConfigParser()
            config.read(configfile)
            defaults = config['DEFAULT']
            username = defaults['username']
            password = defaults['password']
            site_url = defaults['site_url']
            self.siteUrl = site_url
            self.session = requests.Session()
            self.session.auth = (username, password)
            self.cache_expire = defaults['cache_expire']
            # self.session.headers.update({'x-test': 'true'})
            self.session.headers.update({'Origin': site_url})
        else:
            self.logger.error('Missing config.ini file with login data')
            sys.exit(1)


    def prepareCache(self, CACHE_PATH):
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

    def findUser(self, email, withcache=True):
        '''Searches for a specific user, the API uses the same endpoint, for
        one or many'''
        userList = self._getJsonAt(self.URL_FIND_USER + email, withcache).get('users')
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
        path = self.URL_REPORT_CARD.replace('USER_ID',str(userId))
        return self._getJsonAt(path, False)

    def addUsersToSchool(self, usersArray, courseId):
        usersJsonArray = []
        for userRow in usersArray:
            userJson = {
                "email":userRow[0],
                "name":userRow[1],
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

    def enrollUsersToCourse(self, userIdArray, courseId):
        responses = []
        for userRow in userIdArray:
            response = self.enrollUserToCourse(str(userRow[0]))
            responses.append(response)
        return responses

    def enrollUserToCourse(self, userId, courseId):
        path = self.URL_ENROLL_USER.replace('USER_ID', str(userId))
        response = self._postJsonAt(path, json.dumps({"course_id": int(courseId)}))
        if response:
            return json.loads(response)
        else:
            return response

    def getEnrolledCourses(self, userId):
        "Gets the courses the user is enrolled in"
        path = self.URL_ENROLL_USER.replace('USER_ID', str(userId))
        response = self._getJsonAt(path).get('enrollments')
        courses = []
        for items in response:
            if 'course_id' in items.keys():
                courses.append(items['course_id'])
        return courses


    def checkEnrollmentToCourse(self, userId, courseId):
        "Check is a user is enrolled in a specific course"
        courses = self.getEnrolledCourses(userId)
        if int(courseId) in courses:
            return True
        else:
            return False

    def _getJsonAt(self, path, withCache=True):
        if withCache and path in self.cachedData:
            self.logger.info(("Found cached data for " + path))
            return self.cachedData[path]
        else:
            fullUrl = self.siteUrl + path
            self.logger.info(("Downloading data from " + fullUrl))
            jsonData = self.session.get(fullUrl).json()
            if jsonData.get('error'):
                self.logger.error('Check Teachable credentials')
                sys.exit(1)
            if withCache:
                self.cachedData[path] = jsonData
            return jsonData

    def _postJsonAt(self, path, jsonBody):
        fullUrl = self.siteUrl + path
        self.logger.debug(("Uploading POST data to " + fullUrl))
        self.logger.debug("JSON Body : ")
        jsonTxt = json.loads(jsonBody)
        self.session.headers.update({'Content-Type': 'application/json;charset=UTF-8'})
        self.logger.debug((json.dumps(jsonTxt, sort_keys=True, indent=4, separators=(',', ': '))))
        jsonResponseBody = self.session.post(fullUrl, data=jsonBody)
        return jsonResponseBody.text
