#!/bin/bash

sudo python3 -m pipelines.experiments.cloud_only.cloud
sudo python3 -m pipelines.experiments.edge_only.cloud
sudo python3 -m pipelines.experiments.hybrid.cloud