
# Changelog
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

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