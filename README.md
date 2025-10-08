# Requirements

Some help resources used for this code:

* https://realpython.com/python-web-scraping-practical-introduction/
* https://www.crummy.com/software/BeautifulSoup/bs4/doc/

To be installed in a virtual environment with "pip3 install ...":
* bs4
* click
* dash-ag-grid (automatically installs Dash as well)
* numpy
* pandas
* pip3 install -I gunicorn (on server)

Saved as:

        $ pip3 freeze > requirements.txt 

# Virtual environment

Something like:

        at home: 
        $ python3 -m venv venv-AQAS-app
        then
        $ source ~/tmp/venv-AQAS-app/bin/activate

# Work pipeline

In the following order:

        $ ./scrape.py --command download
        $ ./scrape.py --command parse
        $ HOST=0.0.0.0 PORT=8080 python3 gui.py

# Run test server

Something like:

    $cd tmp-akkreditasyon-webscrape
    $~/venv-AQAS-app/bin/gunicorn  -w 4 -b 127.0.0.1:8080 mainApp:server --daemon #NGINX arkasında kullanılmalı, bkz: https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/
    $pkill gunicorn

# Evidence matching scheme

It is difficult to match OBS grade exports (which are the evidence of learning outcome achievement) with the matrices based on syllbus, for many reasons including the changes in syllabi and detached processes of OBS grade column creation and syllabus entry. Therefore a scheme for matching evidence excel files to assessment activities is proposed as follows (but its activation is controlled by settings. See the 'settings' section below.):

* a list of evidence column no's (counts from 1) match a list of activity IDs (multi-to-multi mapping)
* When the left hand side is multiple evidence columns, their 'weighted' average is taken, using OBS percentages as weights.
* When the right hand side is multiple activities, the above calculated average is used as the assessment value for all of them.
* All grades are assumed to be over 100
* Use of the above scheme should not change the resulting student grade (HBN in OBS, over 100)
* Evidence files must be named as "year-year-semester-sectionno.xlsx" under the folder for the course. There can be multiple files but they all use the matching scheme stored in "_matching.json" in the same folder
* OBS table header names have the structure "activity(%xx)_instructortag"

# Settings

Settings are in the file 'settings.py':

* **route_prefix**: The URL route to attach the application on its server, .e.g. "/ieuaqas"
* **storage**: A directory, local to the program file, where all data are stored and to be found. The directory scheme under the data directory must be as follows (note: some of the following are created automatically by the scrape.py script):
    - **/courselist.json**: Lists of course codes in programs
    - **/pos.json**: Lists of program outcomes
    - **/a-to-lo/department/course code.csv**: Course activity to course learning outcome mapping matrises
    - **/lo-list/<epartment/course code.json**: Learning outcome ist of the course
    - **/lo-to-po/department/course code.csv**: Course learning outcome to program outcome mapping matrices
    - **/pocontrib-in-syllabus/department/course code.json**: Course's contribution level to program outcomes, as found in the syllabus
    - **/evidence/department/course code/_matching.json**: Activity (in syllabus/a-lo matrix) to course grade  (in grade list) matching scheme. If a scheme is not found, the default scheme is used.For example

                > {
                "Proje": {"from":[1],"to":[6]},
                "Quiz": {"from":[2],"to":[1,2,3,4]},
                "Sunum": {"from":[3],"to":[5]},
                "Final": {"from":[4],"to":[7]}
                }

        The above maps assessment activity no 2 in the syllabus to grade columns 1, 2, 3, and 4 in the grade table (using their equal weighted average, regardless of their percentages in OBS). The label "Proje" is informational only.

        If opted, the default (so called 'crude') matching scheme is automatically generated maps all activities to the total column (-1):

                > {"Total":{"from":[1,2,3,4], "to":[-1]}}

    - **/evidence/department/course code/*.xlsx**: Course grade list(s). If multiple files are found they are checked against each other for consistency of structure. Files are also checked against the matching scheme for compatibility.
* **matchschemeSearchStrategy**: Controls how a matching scheme is determined. One of the following:
        - **crude** : Use the total grade column in OBS files.The name or regular expression for the total column name is to be given in the setting 'crudeTotalGradeColumnName'
        - **defaultToCrude**: Search for a file _
* **excel_decimal**: Decimal separator to use when opening excel files
* **evidence_scheme**: The only option now is "singleTotal" which uses a single grade list excel table for all departments and courses, containing only four variables students's department ("log","dba",etc.), course code, grade (over 100), and pass/fail status ("Geçti","Kaldı").
* **evidence_single_filename**: The name of the "singleTotal" scheme excel file, relative to 'storage'.

# IEU specific design issues

* Our syllabus format do not allow to detail multiple activities of the same kind. For example, when using multiple quizzes the weightages may be different, some may be proctered while others are not. This has percussions for LO matrix.
* In addition our OBS
# Issues and feature requests

* (BGÇ) A-to-LO matrix allows antry to non-existent activity rows, must be prevented and warning message should be shown to user.
* (BGÇ) A-LO saving should be button triggered, instead of being automatic.
* (MG) Saving is not safe. Someone else may be editing concurrently. File timestamp check can be a good idea.
* (MG) Logging the update activity is needed
* (MG) Different passwords can be used, to match to user login
* Excel file has ',' instead of '.' in numbers!