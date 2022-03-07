
# Changelog
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

### Added
- New `metrics.network.NetworkMonitor` class that handles `tshark` and packet analysis for bandwidth usage monitoring.
- New default named parameter `job_id` in `EdgeNetServer.send_command` and `EdgeNetServer.send_command_external` to specify a named Job.

## [1.3.0] - 2021-02-14
### Added
- New termination procedure that can be called out through the async coroutine `EdgeNetServer.send_teriminate` and its partner function `EdgeNetServer.send_terminate_external` that can kill the client process running on the edge.
- New entry in configuration file `TERMINATE_CLIENTS_ON_RECEIVE` that dictates if the client process is killed through `os.kill` if a termination message is received.
- New `Job.register_metrics` command that properly adds a new `Timer` object to its `.metrics` dictionary and modifies its current.
- New `Job.elapsed`, `Job.job_started`, and `Job.job_ended` property functions that now consolidate data from all of its Timer objects under `.metrics`.
- New functions in `Timer` that can help pickle and unpickle its instances to ease transmission of metrics.

### Changed
- `Job.metrics` is now a dictionary of function call IDs and their `Timer` objects, instead of the original one-to-one correspondence of the previous implementation.

## [1.2.0] - 2021-02-12
### Added
- New `callback` keyword argument for `EdgeNetServer.send_command` and `EdgeNetServer.send_command_external` that is called when a job result is received. The `EdgeNetJobResult` object associated with the result is passed to the function.
- Full edge-only implementation of the LPR pipeline is now at `pipelines.experiments.edge_only`.
- New function `EdgeNetJob.wait_until_finished` that will wait until a `MSG_FINISH` is received for the current job using a spin lock that checks a new attribute `EdgeNetJob.finished`.
- New `Timer` and `TimerSection` classes can now record times taken to execute specific code blocks.
- New `Experiment` class can process `Job` and associated `Timer` metrics to record to a CSV file.
- `EdgeNetJob` now has a `.metrics` attribute that stores said `Timer` object.
- `EdgeNetJob` now has a `.wait_for_metrics` function that will wait until the `.metrics` attribute is not `None`, using a spin lock.
### Changed
- `is_polling` argument for `EdgeNetServer.send_command` and `EdgeNetServer.send_command_external` is now passable only as a *keyword*.
- `sent_dttm` and `recv_dttm` for `EdgeNetJobResult` should now be all in ISO format.
- `@EdgeNetServer.uses_sender` now sends an object with a collection of sending functions instead of a regular `send_result` function.

## [1.1.0] - 2021-02-10
### Added
- Initial edge/client and cloud/server modules
- Rudimentary job and session handling with their wrappers in `edgenet.job` and `edgenet.session`, respectively.
- Simple "single-return" edge functions that are callable by the server.
- More complex, asynchronous "polling" edge functions that send out a result during the function's call, through a function decorator `EdgeNetClient.uses_sender`.
- Registering of functions in the edge, which can be externally called through `@EdgeNetClient.register_function`. Note that `@EdgeNetClient` here should be an *instantiated class object*.
- GPX parsing and syncing through the `gpx` module.
- Handling of GPX tracks and their collections through `gpx.wrappers.GPXCollection` and `gpx.wrappers.GPXEntry`, respectively.
- Letting a function access a parsed and synced `GPXCollection` of a given GPX file through a function decorator `@gpx.uses_gpx(gpx_filepath)`

## [1.0.0] - 2021-02-08

Initial version, added `CHANGELOG.md`, `README.md`, and Python `virtualenv` scripts.