
# Change Log
All notable changes to this project will be documented in this file.
 
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).
 
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