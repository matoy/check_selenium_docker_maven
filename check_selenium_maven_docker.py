#!/usr/bin/env python3
"""
    Copyright (C) 2020  Opsdis Consulting AB <https://opsdis.com/>
    This file is part of check_selenium_docker.
    check_selenium_docker is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    check_selenium_docker is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with check_selenium_docker.  If not, see <http://www.gnu.org/licenses/>.
"""

import docker
import os, sys, time, traceback, signal
import json
import argparse
import glob
import re
import xmltodict

# catch-all for exceptions exit codes
# @see https://nagios-plugins.org/doc/guidelines.html#AEN78
def except_hook(exctype, exc, tb):
    print('{}: {}'.format(type(exc).__name__, exc))
    traceback.print_exception(exctype, exc, tb)
    sys.exit(3)
sys.excepthook = except_hook

# Parse commandline arguments
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help="show failed test names and failure messages (-vv)")
parser.add_argument("--debug", type=str, default="false",
                    help="expose 4444 and 7900 ports of the container to the localhost to share screen/browser view, default 'false', other possible options: 'true'")
parser.add_argument("--timeout", type=int, default=300,
                    help="results waiting timeout in sec, default 300")
parser.add_argument("--browser", type=str, default="chrome",
                    help="container version to use, default 'chrome', other possible options: 'firefox' or 'edge', only used to determine which selenium should be executed ; you should also specify the browser to use in your java code")
parser.add_argument("--gridfqdn", type=str, default="localhost",
                    help="selenium grid server to use, default 'localhost', only used to determine if the selenium should be executed in the containers background ; you should also specify the grid hub to use in your java code")
parser.add_argument('--no-newlines', action='store_true',
                    help="print newlines literally on multiline output")
parser.add_argument("--path", type=str, default="/usr/lib/centreon/plugins/selenium/junit-selenium-sample", help="path to selenium/maven resources")
parser.add_argument("--mavenphase", type=str, default="test", help="your maven phase name")
parser.add_argument("--mavenenv", type=str, default="prod", help="your maven env to test: dev, uat, prod, etc.")
parser.add_argument("--mavenscenario", type=str, default="myscenario", help="your maven scenario name")
parser.add_argument("--mavenlocale", type=str, default="fr_fr", help="your maven locale")
parser.add_argument("--mavenreport", type=str, default="surefire-reports/TEST-com.lambdatest.MyClass.xml", help="your target folder related path to xml report")
args = parser.parse_args()
path = args.path
browser = args.browser
gridfqdn = args.gridfqdn
mavenphase = args.mavenphase
mavenenv = args.mavenenv
mavenscenario = args.mavenscenario
mavenlocale = args.mavenlocale
mavenreport = args.mavenreport
timeout = abs(args.timeout)
debug = args.debug
verbose = args.verbose
os.chdir(path)
if browser not in ['chrome', 'firefox', 'edge']:
    print("Error: not allowed browser!")
    sys.exit(3)

# Remove old result xml repotr files
for result in glob.glob(path + '/out/' + mavenenv + '-' + mavenlocale + '-' + mavenscenario + '.xml'):
    os.remove(result)

# Signal trap for container cleaning.
def handler(signum, frame):
    if 'container' in globals():
        container.stop()
    print("Error: execute interrupted!")
    sys.exit(3)
for sig in [signal.SIGTERM, signal.SIGINT]:
    signal.signal(sig, handler)

# Start selenium docker container
ports = {}
if debug == "true":
    ports = {'4444/tcp': 4444, '7900/tcp': 7900}
client = docker.from_env()
container = client.containers.run(
    'selenium-' + browser + '-node-with-maven',
    auto_remove = True,
    shm_size = '2G',
    volumes = {
        path + '/': { 'bind': '/maven', 'mode': 'rw' },
    },
    environment={'GRID_FQDN':gridfqdn, 'MAVEN_phase':mavenphase, 'MAVEN_environment':mavenenv, 'MAVEN_cucumberFilterTags':mavenscenario, 'MAVEN_locale':mavenlocale, 'MAVEN_reportxmlfile':mavenreport},
    ports = ports,
    detach = True
)

# Wait for result file to be written
waitedfor = 0
projectsNb = 1
while len(glob.glob(path + '/out/' + mavenenv + '-' + mavenlocale + '-' + mavenscenario + '.xml')) < projectsNb and waitedfor <= timeout:
    time.sleep(1)
    waitedfor += 1

# Stop and remove container
try:
    container.stop()
except docker.errors.APIError as err:
    pass

# If no result was received after timeout exit with status unknown
if waitedfor >= timeout:
    print("UNKNOWN: Test timed out. Investigate issues.")
    sys.exit(3)

# Parse result files
# format:
# <testsuite tests="1" failures="0" name="com.lambdatest.IntranetchristiandiorcoutureTest" time="6.568" errors="0" skipped="0">
#with open('/usr/lib/centreon/plugins/selenium/java/junit-selenium-sample/out/single-fr_fr-@account_01.xml', 'r') as myfile:
with open(path + '/out/' + mavenenv + '-' + mavenlocale + '-' + mavenscenario + '.xml', 'r') as myfile:
    obj = xmltodict.parse(myfile.read())
testsNb = int(obj['testsuite']['@tests'])
failuresNb = int(obj['testsuite']['@failures'])
errorsNb = int(obj['testsuite']['@errors'])
skippedNb = int(obj['testsuite']['@skipped'])
passedNb = int(testsNb - failuresNb - errorsNb - skippedNb)
from decimal import Decimal
exec_time = Decimal(obj['testsuite']['@time'])
testcaseClassname = obj['testsuite']['testcase']['@classname']
testcaseName = obj['testsuite']['testcase']['@name']

# Performace Data
perfData = ("'passed'={1};;{0}:;0;{0} 'failed'={2};;~:0;0;{0} 'exec_time'={3}s"
    ';;;;').format(testsNb, passedNb, failuresNb, exec_time)

statusCode = 0
exitStatus = ['OK', 'WARNING', 'CRITICAL']

# Exit logic with performance data
if failuresNb == 0 and errorsNb == 0:
    print('OK: Passed {} of {} tests in {}s ({}/{}).'.format(passedNb, testsNb, exec_time, testcaseClassname, testcaseName) + " | " + perfData)
    sys.exit(0)

elif failuresNb > 0 or errorsNb > 0:
    print('CRITICAL: Failed {} and Error {} of {} tests ({}/{}).'.format(failuresNb, errorsNb, testsNb, testcaseClassname, testcaseName) + " | " + perfData)
    sys.exit(2)

else:
    print("CRITICAL: Investigate issues")
    sys.exit(2)
