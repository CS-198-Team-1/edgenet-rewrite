#!/bin/bash

for bw in 500Kbit 250Kbit 100Kbit 50Kbit 25Kbit 10Kbit 5Kbit; do
    sudo python3 -m pipelines.experiments.edge_only.edge --port 8891
    sudo python3 -m pipelines.experiments.hybrid.edge --port 8892
done
