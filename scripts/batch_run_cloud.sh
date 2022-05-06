#!/bin/bash

sudo python3 -m pipelines.experiments.cloud_only.cloud --port 8890
sudo python3 -m pipelines.experiments.edge_only.cloud --port 8891
sudo python3 -m pipelines.experiments.hybrid.cloud --port 8892
