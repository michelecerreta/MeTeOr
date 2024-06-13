from modules.command_interface import Command
import nmap
import yaml
import json
import requests
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup
import argparse
from libs.colors import Colors

class NmapScanCommand(Command):
    supported_node_types = ['','pts_compute', 'pts_webapp']
    
    def get_app_info_from_headers(response):
        app_info = {}
        if response.headers.get('Server'):
            app_info['server'] = response.headers.get('Server')

        if response.headers.get('X-Powered-By'):
            app_info['x_powered_by'] = response.headers.get('X-Powered-By')

        return app_info

    def get_app_info_from_content(response):
        app_info = {}
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_generator = soup.find('meta', attrs={'name': 'generator'})
        if meta_generator and meta_generator.get('content'):
            return meta_generator['content']

        return app_info
    
    def is_web_app(ip, port, verbose=True):

        if verbose:
            print(Colors.CYAN + f"\nTesting {ip}:{port}")

        try:
            response = requests.get(f"http://{ip}:{port}", timeout=50)
            print(response.content)
            print(response.headers)
            if response.status_code != 200:
                if verbose:
                    print(WARNING + "Error response")
                    return False, {}

            app_info = {}
            if 'text/html' in response.headers.get('Content-Type', ''):
                app_info.update(get_app_info_from_headers(response))
                app_info.update(get_app_info_from_content(response))

            if verbose:
                print(Colors.GREEN + f"Detected Web App: {app_info}")
            return True, app_info

            if verbose:
                print(WARNING + "Not a web application (non-HTML content)")
            return False, {}
        except (ConnectionError, Timeout) as e:
            if verbose:
                print(Colors.FAIL + f"Connection error: {e}")
            return False, {}


    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    def read_tosca_file(self, filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def create_tosca_yaml(self, scan_results, filename):
       
        tosca_template = self.read_tosca_file(filename)
        if tosca_template is None:
            print(f"Error: File {filename} does not exist or is empty.")
            return

        # Ensuring the structure is there
        tosca_template.setdefault('topology_template', {}).setdefault('node_templates', {})

        node_templates = tosca_template['topology_template']['node_templates']

        for host in scan_results.all_hosts():
            host_data = scan_results[host]
            tcp_ports = [port for port in host_data.get('tcp', {}) if host_data['tcp'][port].get('state') == 'open']

            os_info = 'Unknown'
            if 'osmatch' in host_data and host_data['osmatch']:
                os_info = host_data['osmatch'][0]['name']

            # Prepare the node data
            compute_node_data = {
                'type': 'pts_compute',
                'properties': {
                    'os': {'name': os_info},
                    'ip': host,
                    'open_ports': tcp_ports
                }
            }

            # Check if the node with the same IP exists
            existing_node_key = None
            for node_key, node_value in node_templates.items():
                if node_value['type'] == 'pts_compute' and node_value['properties']['ip'] == host:
                    existing_node_key = node_key
                    break

            # Update the existing node or add a new node
            if existing_node_key:
                print(f"Updating existing node for IP {host}.")
                node_templates[existing_node_key] = compute_node_data
            else:
                print(f"Adding new node for IP {host}.")
                node_templates[f"host_{host}"] = compute_node_data

        # Write the updated template back to the file
        with open(filename, 'w') as file:
            yaml.dump(tosca_template, file, sort_keys=False)
            print(f"TOSCA template updated and saved to '{filename}'.")

    
    def goscan(self, scanner, tgt, additional_args, filename):
        print(f"{Colors.GREEN}Starting Nmap scan for host: {tgt} and arguments: {additional_args}")
        scanner.scan(tgt, arguments=additional_args)
        scan_results = scanner
        self.create_tosca_yaml(self, scan_results, filename)

    def execute(self, nodename = None, target=None, filename=None):
        scanner = nmap.PortScanner()
        
        if isinstance(target, dict):
            # it's a TOSCA node
            if target['type'] not in self.supported_node_types:
                print(f"NmapScanCommand does not support nodes of type: {target['type']}")
                return
                        
            additional_args = input("Enter any additional Nmap arguments (or press enter to skip): ")
            additional_args 
            self.goscan(scanner, target['properties']['ip'], additional_args, filename)

        elif isinstance(target, str):
            # Add other things later
            additional_args = input("Enter any additional Nmap arguments (or press enter to skip): ")
            self.goscan(scanner, target, additional_args, filename)

        else:
        # No node object passed, ask user for target IP, subnet and optional arguments
            print("No target specified. Please provide target details.")
            ip = input("Enter the IP address to scan: ")
            subnet = input("Enter the subnet (e.g., 24): ")
            additional_args = input("Enter any additional Nmap arguments (or press enter to skip): ")

            # Construct target and arguments
            target = f"{ip}/{subnet}" if subnet else ip
            additional_args = f" {additional_args}".strip()
            self.goscan(scanner, target, additional_args, filename)

        # Process scan results (this part is common for both node and IP address scanning)
        for host in scanner.all_hosts():
            print(f"{Colors.BLUE}\nHost : {host}")
            print("State : %s" % scanner[host].state())
            for proto in scanner[host].all_protocols():
                print('----------')
                print('Protocol : %s' % proto)
                lport = scanner[host][proto].keys()
                for port in lport:
                    print('port : %s\tstate : %s' % (port, scanner[host][proto][port]['state'])+f"{Colors.ENDC}")
        print(f"\nScan results saved to '{filename}'")
    


