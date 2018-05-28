# Teachable Scripts
You'll find here some script to manage your Teachable school using the unofficial Teachable API.

This project was forked from [buzkall's project](https://github.com/buzkall/teachable-reports-export) because of major refactoring and added features which changes the goal of the original project.
Pull requests are accepted if you want to add new features/apis.


   

## Disclaimer
**This project is unofficial and not supported by Teachable. It is published and made open source in order to help other teachers but it comes with no garanty from the author or any contributor.**

Teachable.com doesn't have an official API to manage your school. It has some webhooks to trigger events and use them with services like Zapier, but there is no fast and practical solution to manage your school, especially for large student groups.
The website is done using Angular, and needs some api urls to load the content, so this project uses those api to collect data and perform actions as if you were using the web admin panel.

**This mean that if Teachable changes their APIs, scripts from this project could stop working and potentially do damage to your school data. At any time. 
Please take that into consideration before using this project and don't come to me to ask for repairs afterwards ;)** 

## Install and Config
This script has been tested with python 2.7

It requires the module "request" which can be installed using:

    pip install requests
    
If you don't have pip installed you can do it with

    sudo easy_install pip
    

After that you should copy the file called secrets_example.py, rename it as secrets.py and set your username, password and yout teachable custom domain

    username='YOUR_TEACHABLE_USERNAME'
    password='YOUR_TEACHABLE_PASSWORD'
    site_url='https://YOUR_TEACHABLE_URL'

The first time you run the script, this error could happen.

    raise SSLError(e, request=request) requests.exceptions.SSLError: 
    HTTPSConnectionPool(host='xxxx', port=443): 
    Max retries exceeded with url: xxxxx 
    (Caused by SSLError(SSLError(1, u'[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] 
    sslv3 alert handshake failure (_ssl.c:590)'),)) 

You should install python with brew with this command in order to solve all the openssl nonsense.

    brew install python --with-brewed-openssl
    
After installing it you should probably force the brew link, but in case it doesn't solve the problem
the "brew info python" suggest you add the url to your path

    export PATH="/usr/local/opt/python/libexec/bin:$PATH"

## Usage
### Enroll users to course
If you want to enroll a whole list of users to a new course, you can do it with this script that receives a user list csv file (you can download those from your school admin panel) and a course id.

Typing --help will show the parameters info
    usage: enrollUsers.py [-h] [--csv_delimiter [CSV_DELIMITER]]
                          input_file courseId
    
    Mass enroll users from csv file into a specified course
    
    positional arguments:
      input_file            Input csv file with the first column giving the user
                            id (other columns are not used but can be present).
                            This matches Teachable downloaded csv user lists
      courseId              The id of the course they should be enrolled in
    
    optional arguments:
      -h, --help            show this help message and exit
      --csv_delimiter [CSV_DELIMITER]
                            Input csv file delimiter (default value : ,)
    
    ---

Example, if you already have a user list csv file named userlist.csv and your course id is 1234 you can enroll of users in the file into this couse by typing :

    python enrollUsers.py path/to/file/userlist.csv 1234
    
If some of thoses users are already enrolled in the course, Teachable API currently ignores them.

### Get User Reports

Typing --help will show the parameters info

    usage: getUserReport.py [-h] [--output_file [OUTPUT_FILE]] [--format [FORMAT]]
                            emails
    
    Get your student sessions list in Teachable.
    
    positional arguments:
      emails                list of emails (separated with commas and without
                            spaces)
    
    optional arguments:
      -h, --help            show this help message and exit
      --output_file [OUTPUT_FILE]
                            Output file
      --format [FORMAT]     Output format (txt or csv)
    
    ---
    
It should receive at least one parameter: the student's email or emails (separated by commas)

    python getUserReport.py STUDENT_EMAIL
    python getUserReport.py STUDENT_EMAIL1,STUDENT_EMAIL2
    
It will output something like this

    Utilisateur,Date,Cours,Chapitre,Durée
    Maxime Britto,2017-10-12 15:38:00,Créez une app pour iOS 11,Bilan et suite,53s 
    Maxime Britto,2017-10-12 15:36:22,Créez une app pour iOS 11,Finaliser notre première app,3min 49s 
It has been created for french laws regarding students proof of presence. This is why it lists each session with student name, timestamp, course, and duration of the session. 

Specifying the output file won't output anything to the screen and will save it into a file:

    python getUserReport.py STUDENT_EMAIL --output_file FILENAME.txt
    
You also can choose to export as a csv file (comma separated values):

    python getUserReport.py STUDENT_EMAIL --output_file FILENAME.csv --format csv
    

## Cache and rate limits
To avoid reaching any rate limit, the script caches the courses' data into a file using Shelve.  
The cache path can be changed modifying the variable CACHE_PATH, by default it creates a file called teachable_cache.out in the same folder

The cache file expires in a week, but this time can be changed modifying the constant MAXIMUM_CACHE_DURATION in the TeachableAPI.py file.
