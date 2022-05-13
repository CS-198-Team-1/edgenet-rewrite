#!/bin/bash

python3 -m pipelines.experiments.edge_only.edge --port 8891
python3 -m pipelines.experiments.hybrid.edge --port 8892
