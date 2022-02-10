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


### Examples
To run sample pipelines locally, run two terminals (or if running practically, two terminals on different machines) and run the following command to run the sample pipelines:

On the cloud/server (make sure you run this locally, or in a machine with a public IP properly set in `config.py`):
```
python3 -m pipelines.examples.simple.cloud
```

On the edge:
```
python3 -m pipelines.examples.simple.edge
```

A grace period of five seconds is given once the cloud script is run to allow for the edge to connect. You could also run the edge script first, as it will try to connect to the cloud as soon as it's up.

#### Available examples:
- `pipelines.examples.simple`: The cloud calls a simple "add three numbers" function to the edge.

