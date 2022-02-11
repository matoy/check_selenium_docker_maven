check_selenium_maven_docker
-----------------------

- [Overview](#overview)
  * [Highlights](#highlights)
- [Workflow](#metrics-naming)
- [System requirements](#system-requirements)
- [Docker image](#docker-image)
- [Plugin](#plugin)
- [Add new test scenarios](#add-new-test-scenarios)
- [Execute the plugin](#execute-the-plugin)
- [Performance metrics](#performance-metrics)
- [License](#license)

# Overview #
Synthetic website monitoring with Selenium and Docker.

check_selenium_maven_docker is a Nagios based plugin that spins up a Docker container, executes the test and, once the test is finished and the result has been reported back to the monitoring solution, removes the Docker container.

### Highlights ###

* Works with any Nagios compatible system such as Centreon. Centreon specific integration will be take in all examples below.
* Every test is executed in a fresh environment. (https://www.selenium.dev/documentation/en/guidelines_and_recommendations/fresh_browser_per_test/)
* Will remove the Docker container as soon as the test is complete. Requires no manual cleanup of stopped containers.
* Any custom performance metrics is allowed.

# System requirements #
The following prerequisites must be installed on the server that will execute the plugin.

* Python 3 with the docker module
* docker-ce

```
# Install docker-ce
yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2

yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

yum install docker-ce

yum install python-pip3

# Add user 'centreon-engine' to group 'docker'
usermod -aG docker centreon-engine

# Start and enable docker
systemctl start docker && systemctl enable docker
service centreon restart

# Install the docker Python 3 module
pip-3 install docker xmltodict

# (Optional) Add versionlock to docker-ce
yum install yum-plugin-versionlock
yum versionlock docker-ce

# (Optional) Remove versionlock from docker-ce
yum versionlock clear
```


# Docker image #

Build the Docker image:

```
git clone https://github.com/matoy/check_selenium_maven_docker
cd check_selenium_maven_docker/dockerimage/

# eventually add --build-arg http_proxy=http://yourproxyfqdn:port/ if required
docker build . --tag selenium-chrome-node-with-maven --no-cache

cd ..
```

Image for an alternative supported browser:

```
# eventually add --build-arg http_proxy=http://yourproxyfqdn:port/ if required
sed 's/chrome/firefox/' Dockerfile | docker build --tag selenium-firefox-node-with-maven -
sed 's/chrome/edge/' Dockerfile | docker build --tag selenium-edge-node-with-maven -
```

# Plugin #

Copy the plugin to the plugin directory and make it executable:

```
cp check_selenium_maven_docker.py /usr/lib/centreon/plugins/
chmod +x /usr/lib/centreon/plugins/check_selenium_maven_docker.py
```

Add a new check_command to Monitor:

```
check_selenium_maven_docker
$CENTREONPLUGINS$/check_selenium_maven_docker.py --path $_SERVICECHECKFOLDER$ --browser $_SERVICEBROWSER$ --timeout $_SERVICETIMEOUT$ --gridfqdn $_SERVICEGRIDFQDN$ --mavenphase '$_SERVICEMAVENPHASE$' --mavenenv '$_SERVICEMAVENENV$' --mavenscenario '$_SERVICEMAVENSCENARIO$' --mavenlocale '$_SERVICEMAVENLOCALE$' --mavenreport '$_SERVICEMAVENREPORT$' -vv $_SERVICEOPTIONS$ $_HOSTOPTIONS$
```


# Add new test scenarios #

Create a new main directory (/usr/lib/centreon/plugins/selenium) in the main directory create a new folder 
preferably named as the URL used in the test (/usr/lib/centreon/plugins/selenium/mysite.com):

```
mkdir /usr/lib/centreon/plugins/selenium
mkdir /usr/lib/centreon/plugins/selenium/mysite.com
```

Inside this folder, put what is expected by maven.
Make sure to create a "out" folder and chmod it to 777.
You can find a sample here: https://github.com/matoy/junit-selenium-sample
the pom.xml file and other resources should be placed in your /usr/lib/centreon/plugins/selenium/mysite.com folder:

```
cd /usr/lib/centreon/plugins/selenium/
git clone https://github.com/matoy/junit-selenium-sample
mkdir junit-selenium-sample/out
chmod 777 junit-selenium-sample/out
```

# Execute the plugin #

```
/usr/lib/centreon/plugins/check_selenium_maven_docker.py --path /usr/lib/centreon/plugins/selenium/junit-selenium-sample/ --mavenphase test --mavenenv single --mavenscenario "mytest" --mavenlocale fr_fr --mavenreport "surefire-reports/TEST-com.lambdatest.MySiteTest.xml" --browser chrome --timeout 30

# other examples:
# with Edge browser instead of Chrome
use: --browser edge

# with another existing grid server, for example located geographically elsewhere
use: --gridfqdn mygridserver
```

# Debug 
You can execute the script with the --debug true parameter ; this will result the docker container to be executing with exposing its 4444 & 7900 ports:
```
/usr/lib/centreon/plugins/check_selenium_maven_docker.py --path /usr/lib/centreon/plugins/selenium/mysite.com/ --mavenphase test --mavenenv single --mavenscenario "mytest" --mavenlocale fr_fr --mavenreport "surefire-reports/TEST-com.lambdatest.MySiteTest.xml" --browser chrome --timeout 30 --debug true
```
Then connect to the 7900 port of your host running the script with a browser, you'll get the VNC interface (password is secret by default) and see what is being made in the browser.

You can go further by getting output inside the container itself:
```
export testfolder=/usr/lib/centreon/plugins/selenium/mysite.com
export image=selenium-chrome-node-with-maven
docker run -it --rm -p 4444:4444 -p 7900:7900 --shm-size="2g" -e MAVEN_phase="test" -e MAVEN_environment="single" -e MAVEN_cucumberFilterTags="mytest" -e MAVEN_locale="fr_fr" -e MAVEN_reportxmlfile="surefire-reports/TEST-com.lambdatest.MySiteTest.xml" -v $testfolder/:/maven $image /opt/bin/entry_point.sh
```

# License 
check_selenium_maven_docker is licensed under GPL version 3.
