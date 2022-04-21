import subprocess, uuid
from scapy.all import *
from .constants import *
from config import *


class NetworkMonitor:
    def __init__(self, interface, experiment_id=None):
        self.experiment_id = experiment_id or str(uuid.uuid4())
        self.interface = interface
        self.ifb = "ifb0"

        self.process = None
        self.captures = {}

        self.delay = None
        self.rate = None

        # For scapy
        self.packets = None

    @property
    def result_location(self): return f"{TSHARK_RESULTS_LOCATION}{self.experiment_id}.{self.interface}.pcap"

    def implement_delay(self, delay):
        if self.delay:
            raise NetworkMonitorException("Tried to implement a delay when there is already an existing one.")
        
        args = [
            "tc", "qdisc", "add", "dev", self.interface,
            "root", "netem", "delay", delay
        ]
        _p = subprocess.call(args)
        
        self.delay = delay
    
    def release_delay(self):
        if not self.delay:
            raise NetworkMonitorException("Attempted to release a delay that was never implemented.")

        args = [
            "tc", "qdisc", "del", "dev", self.interface, "root"
        ]
        _p = subprocess.call(args)

        self.delay = None

    def implement_rate(self, rate):
        if self.rate:
            raise NetworkMonitorException("Tried to implement a rate constraint when there is already an existing one.")
        
        # For outgoing
        args = [
            "tc", "qdisc", "add", "dev", self.interface,
            "root", "netem", "rate", rate
        ]
        _p = subprocess.call(args)
        
        # For incoming
        args = [
            "tc", "qdisc", "add", "dev", self.ifb,
            "root", "netem", "rate", rate
        ]
        _p = subprocess.call(args)
        
        self.rate = rate
    
    def release_rate(self):
        if not self.rate:
            raise NetworkMonitorException("Attempted to release a rate constraint that was never implemented.")

        # For outgoing
        args = [
            "tc", "qdisc", "del", "dev", self.interface, "root"
        ]
        _p = subprocess.call(args)

        # For incoming
        args = [
            "tc", "qdisc", "del", "dev", self.ifb, "root"
        ]
        _p = subprocess.call(args)

        self.rate = None

    def start_capturing(self):
        if self.process:
            raise NetworkMonitorException("Capturing already in progress.")

        args = [
            "tshark", "-i", self.interface,
            "-w", self.result_location,
            "-F", TSHARK_RESULTS_FORMAT,
        ]

        self.process = subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop_capturing(self):
        if not self.process:
            raise NetworkMonitorException("Trying to end a capture that has not started yet.")
        
        self.process.terminate()

    def load_pcap_if_not_loaded(self):
        if not self.packets:
            logging.info(f"Loading .pcap file [{self.result_location}]")
            self.packets = rdpcap(self.result_location)

    def get_all_packet_size_tcp(self, tcp_port):
        self.load_pcap_if_not_loaded()
        logging.info(f"Getting total size of packets with src and dest port {tcp_port}")

        filtered_pkts = (
            pkt for pkt in self.packets if TCP in pkt and (
                pkt[TCP].sport == tcp_port or pkt[TCP].dport == tcp_port
            )
        )

        total_size = sum(len(pkt) for pkt in filtered_pkts)
        return total_size


class NetworkMonitorException(Exception): pass