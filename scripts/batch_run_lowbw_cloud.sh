#!/bin/bash

for bw in 500Kbit 250Kbit 100Kbit 50Kbit 25Kbit 10Kbit 5Kbit; do
    sudo python3 -m pipelines.experiments.edge_only.cloud --port 8891 --bwconstraint $bw
    sudo python3 -m pipelines.experiments.hybrid.cloud --port 8892 --bwconstraint $bw
done

sudo tc qdisc del dev eth0 root
sudo tc qdisc del dev ifb0 root