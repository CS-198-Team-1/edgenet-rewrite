#!/bin/bash

python3.8 -m pipelines.experiments.cloud_only.edge
python3.8 -m pipelines.experiments.edge_only.edge
python3.8 -m pipelines.experiments.hybrid.edge
