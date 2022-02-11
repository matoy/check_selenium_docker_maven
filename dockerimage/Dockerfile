FROM selenium/standalone-chrome:4.1.1-20211217

# selenium container leaves us as user 'seluser', but we need to install more stuff
USER root

# Install nodejs LTS which includes npm
RUN apt-get -qqy update \
  && curl -sL https://deb.nodesource.com/setup_lts.x | sudo -E bash - \
  && apt-get -qqy --no-install-recommends install \
    nodejs \
    maven \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN mkdir /maven && chown -R seluser /maven
VOLUME [ "/maven" ]

RUN mkdir /maven-temp && chown -R seluser /maven-temp
WORKDIR /maven-temp/

# Five seconds after starting container (as deamon) selenium-side-runner will run every /sides/*.side file
ENV GRID_FQDN=localhost
ENV MAVEN_phase="clean verify"
ENV MAVEN_rerunFailingTestsCount=1
ENV MAVEN_locale=fr_fr
ENV MAVEN_environment=myenv
ENV MAVEN_cucumberFilterTags=@mytest
ENV MAVEN_reportxmlfile=reports/mytest.cucumber.RunTest.xml

RUN sed -i "/^\/usr\/bin\/supervisord.*/a \
[ -d /maven/out/maven-repository ] || mkdir /maven/out/maven-repository \n\
ln -s /maven/out/maven-repository /home/seluser/.m2 \n\
cp -R /maven/* ./ \n\
[ \"\$GRID_FQDN\" == \"localhost\" ] && sleep 5 && mvn -B \$MAVEN_phase -f ./pom.xml -Dfailsafe.rerunFailingTestsCount=\$MAVEN_rerunFailingTestsCount -Dlocale=\$MAVEN_locale -Denvironment=\$MAVEN_environment -Dcucumber.filter.tags=\$MAVEN_cucumberFilterTags && cp ./target/\$MAVEN_reportxmlfile /maven/out/\$MAVEN_environment-\$MAVEN_locale-\$MAVEN_cucumberFilterTags.xml \n\
[ \"\$GRID_FQDN\" == \"localhost\" ] ||  mvn -B \$MAVEN_phase -f ./pom.xml -Dfailsafe.rerunFailingTestsCount=\$MAVEN_rerunFailingTestsCount -Dlocale=\$MAVEN_locale -Denvironment=\$MAVEN_environment -Dcucumber.filter.tags=\$MAVEN_cucumberFilterTags && cp ./target/\$MAVEN_reportxmlfile /maven/out/\$MAVEN_environment-\$MAVEN_locale-\$MAVEN_cucumberFilterTags.xml" \
/opt/bin/entry_point.sh
RUN sed -i "s/^\/usr\/bin\/supervisord/\[ \"\$GRID_FQDN\" == \"localhost\" ] \&\& \/usr\/bin\/supervisord/" /opt/bin/entry_point.sh

USER seluser
