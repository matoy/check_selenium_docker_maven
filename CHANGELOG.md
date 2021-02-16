# CHANGELOG

## [2.0.0] - 2021-02-16

### Added
- configurable timeout option
- support for container with alternative browser
- verbose option for more [Nagios Guidelines](https://nagios-plugins.org/doc/guidelines.html#PLUGOUTPUT) compliant error output

### Changed 
- calculate exec_time based on execution all tests in all suites from all side files
- aggregated passed, failed, and total counters for all tests

### Fixed
- process and support more than one side file, issue
  [osdis/check_selenium_docker#6](https://github.com/opsdis/check_selenium_docker/issues/6)
- exec_time calculation error in the absence of tests, issue
  [osdis/check_selenium_docker#5](https://github.com/opsdis/check_selenium_docker/issues/5)
