# EdgeNet

EdgeNet **(working title)** is an implementation of an edge computing pipeline built using Python.

## Installation
### Dependencies
Ensure that you are running **Python 3.8.10**.

Set up and activate the `virtualenv` scripts as per [your operating system's instructions.](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments)

For Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

Then, install the dependencies through `pip`:
```
pip3 install -r requirements.txt
```
### Setting up `config.py`
You need to create your own `config.py` before starting the application. An example is included in `config-local.py`.

## Usage

### Testing
Before running the application,run the automated tests to ensure that everything is working:
```bash
python3 test.py
```
Make sure that port `9000` is usable.
#### Testing does not terminate
If testing does not terminate (gets stuck on a `.` or something), that most likely means that `EdgeNetJob.wait_until_finished` or functions that use it are failing. 

Currently, these tests make use of that function:
- `tests.TestNetwork.test_server_client_command_finishes`
- `tests.TestNetwork.test_server_client_command_polling_finishes`

Make sure that those tests are working properly, and testing should proceed as usual.

### Examples
To run sample pipelines locally, run two terminals (or if running practically, two terminals on different machines) and run the following command to run the sample pipelines:

(`.cloud`) On the cloud/server (make sure you run this locally, or in a machine with a public IP properly set in `config.py`):
```
python3 -m pipelines.experiments.edge_only.cloud
```

(`.edge`)On the edge:
```
python3 -m pipelines.experiments.edge_only.edge
```

A grace period of five seconds is given once the cloud script is run to allow for the edge to connect. You could also run the edge script first, as it will try to connect to the cloud as soon as it's up.

#### Available pipelines:
- **`pipelines.experiments.edge_only`: The main LPR experiment scripts for edge-only processing.**
- `pipelines.examples.simple`: The cloud calls a simple "add three numbers" function to the edge.

