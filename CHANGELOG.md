# CHANGELOG

## [2.2.0] - 2021-08-11

### Added

- parse runner console output (SeleniumIDE `echo` command) for additional perfdata
  marked with `PERFDATA: ` prefix and guidelines compliant for
  [Performance data](https://nagios-plugins.org/doc/guidelines.html#AEN200),
  i.e., `PERFDATA: First Response Time = ${calculatedTime}s;${warningThreshold}`
- catch-all for exceptions exit codes, as by the guidelines
  [Plugin Return Codes](https://nagios-plugins.org/doc/guidelines.html#AEN78)

## [2.1.0] - 2021-07-02

### Added
- `no-newlines` option that prints newlines literally on multiline output,
   useful for passive check
   [Passive Check](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/3/en/passivechecks.html)
- failed and passed perfdata thresholds for consistency with result status

## [2.0.0] - 2021-02-16

### Added
- configurable timeout option
- support for container with alternative browser
- verbose option for more [Nagios Guidelines](https://nagios-plugins.org/doc/guidelines.html#PLUGOUTPUT)
  compliant error output

### Changed
- calculate exec_time based on execution all tests in all suites from all side files
- aggregated passed, failed, and total counters for all tests

### Fixed
- process and support more than one side file, issue
  [osdis/check_selenium_docker#6](https://github.com/opsdis/check_selenium_docker/issues/6)
- exec_time calculation error in the absence of tests, issue
  [osdis/check_selenium_docker#5](https://github.com/opsdis/check_selenium_docker/issues/5)
