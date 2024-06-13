import yaml
import requests
import webbrowser
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup
from modules.command_interface import Command
from libs.colors import Colors

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DetectWebAppCommand(Command):
    
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    def is_web_app(self, ip, port=80):
        try:
            response = requests.get(f"http://{ip}:{port}", timeout=15)
            if response.status_code == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                return True
            return False
        except (ConnectionError, Timeout):
            return False
            
    @staticmethod
    def read_tosca_file(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def extract_app_info(self, ip, port):
        # Implement logic to extract app name, version etc. from the response
        return {'app_name': 'Unknown', 'app_version': 'Unknown'}

    def execute(self, node_name, node, filename):
    
        #Color for output
        OKGREEN = '\033[92m'
        
        if node['type'] != 'pts_compute':
            print(f"Unsupported node type: {node['type']}")
            return

        try:
            tosca_template = self.read_tosca_file(filename)
            if tosca_template is None:
                raise FileNotFoundError

            if 'topology_template' not in tosca_template:
                tosca_template['topology_template'] = {}
            if 'node_templates' not in tosca_template['topology_template']:
                tosca_template['topology_template']['node_templates'] = {}
        except FileNotFoundError:
            # Initialize tosca_template from scratch if file doesn't exist
            tosca_template = {
                'tosca_definitions_version': 'tosca_simple_yaml_1_3',
                'description': 'TOSCA Pentest scenario template...',
                'topology_template': {
                    'node_templates': {}
                }
            }

        
        host = node['properties']['ip']
        ports = node['properties']['open_ports']
        print(f"host: {host}:{ports}")
        webapp_n = 0

        for port in ports:
            if self.is_web_app(host, port):
                webapp_n += 1
                print(f'{Colors.OKGREEN} WebApp found')
                app_info = self.extract_app_info(host, port)
                webapp_node = {
                    'type': 'pts_webapp',
                    'properties': {
                        'ip': host,
                        'port_number': port,
                        **app_info
                    },
                    'requirements': [{
                        'host': {
                            'node': f"{node_name}",
                            'relationship': 'hosted_on'
                        }
                    }]
                }
                # Add the webapp_node to the TOSCA template
                tosca_template['topology_template']['node_templates'][f"wa{host}:{port}"] = webapp_node

                with open(filename, 'w') as file:
                    yaml.dump(tosca_template, file, sort_keys=False)
                print(f"{Colors.ENDC}Scan results saved to '{filename}'")
                
                 # Prompt user to open the webapp in a browser
                open_in_browser = input(f"{Colors.WARNING} Webapp detected on {webapp_node['properties']['ip']}:{webapp_node['properties']['port_number']}. Do you want to launch it in a browser? (yes/no): ").strip().lower()
                if open_in_browser == 'yes':
                    webbrowser.open(f"http://{webapp_node['properties']['ip']}:{webapp_node['properties']['port_number']}", new=2)
        print("\n")
        print("#" * 10 + ' Closing Module DetectWebApp ')
        print("\n")