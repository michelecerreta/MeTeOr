from modules.command_interface import Command
from .wig.wig import wig
import argparse
import yaml
from libs.colors import Colors

class WigScanCommand(Command):
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data


    def run_wig(self, url):
        w = wig(url=url, verbosity='-vvv')
        w.run()
        results = w.get_results()
        return results
    
    @staticmethod
    def read_tosca_file(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def extract_app_info(self, ip, port):
        # Implement logic to extract app name, version etc. from the response
        return {'app_name': 'Unknown', 'app_version': 'Unknown'}
        
    def execute(self, node_name, node, filename=''):
        print(f"node name: {node_name}")
        if node and node.get('type') in ['pts_webapp']:
            host_ip = node['properties'].get('ip')
            port = node['properties'].get('port_number')
            url = f"http://{host_ip}:{port}"

            print(f"Running Wig on {url}")
            results = self.run_wig(url)
            #print('\033[95m')

            if results:

                tosca_template = self.read_tosca_file(filename)

                 # Ensure that the results are in the expected format
                if isinstance(results, tuple) and len(results) >= 2:
                    site_info = results[0]
                    platforms = results[1]

                    if 'title' in site_info:
                        title = site_info['title'].split()[0]
                        print(f"Title: {title}")

                    if platforms and isinstance(platforms, list):
                        for platform in platforms:
                            if hasattr(platform, 'name'):
                                platform_name = platform.name
                                #print(f"Platform Name: {platform_name}")
                            if hasattr(platform, 'version'):
                                platform_version = platform.version
                                #print(f"Platform Version: {platform_version}")

                     # Update the existing node
                    if node_name in tosca_template['topology_template']['node_templates']:
                        print(f"trovato: {node_name} : {title} ")
                        tosca_template['topology_template']['node_templates'][f'{node_name}']['properties'].update({
                            'app_name': title,
                            'app_version': platform_version
                        })

                    with open(filename, 'w') as file:
                        yaml.dump(tosca_template, file, sort_keys=False)
                    print(f"Scan results saved to '{filename}'")
                    

                    print(Colors.GREEN+'Wig Results:')
                    # Print extracted data
                    print(f"Title: {title}")
                    print(f"Platform Name: {platform_name}")
                    print(f"Platform Version: {platform_version}")
            else:
                print("No results found by Wig.")
                
            print('\n'+Colors.ENDC)
        else:
            print("Invalid node type. WigCommand supports nodes of type 'pts_compute' or 'pts_webapp'.")
