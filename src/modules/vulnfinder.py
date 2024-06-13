from modules.command_interface import Command
import requests
import yaml
from libs.colors import Colors

class VulnFinderCommand(Command):
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    def parse_version(self, version_str):
        # Function to parse version string into a numeric tuple for comparison
        try:
            return tuple(map(int, version_str.split('.')))
        except ValueError:
            return (0,)

    def fetch_vulnerabilities(self, app_name, app_version=None, min_cvss="0.0", attack_type=None, min_app_version=None):
        url = f"https://cve.penterep.com/api/v1/product/{app_name}"
        #if app_version:
        #    url += f"/version/{app_version}"

        response = requests.get(url)
        print(response)
        if response.status_code == 200:
            vulnerabilities = response.json()
            # Filter vulnerabilities based on provided criteria
            filtered_vulns = []
            for vuln in vulnerabilities:
                cvss_score = vuln.get('cvss')
                summary = vuln.get('summary', '').lower()
                vuln_version = vuln.get('version', '0')

                # Check if vulnerability meets all criteria
                cvss_check = True if not cvss_score else cvss_score >= min_cvss
                attack_check = True if not attack_type else attack_type.lower() in summary
                version_check = True if not min_app_version else self.parse_version(vuln_version) >= self.parse_version(min_app_version)

                if cvss_check and attack_check and version_check:
                    filtered_vulns.append(vuln)

            return filtered_vulns
        else:
            print("Error fetching vulnerabilities.")
            return []

    def add_vulnerability_to_tosca(self, host, app_name, vulnerability, filename):
        print(vulnerability)

        host = {
                'node' : host,
                'relationship': 'hosted_on'
        }
          
        properties = {
            'CVE' : vulnerability['id'],
            'description' : vulnerability['summary'],
            'cvss' : vulnerability['cvss'],
            'version' : vulnerability['version'],
            'confirmed' : 'false',
            'host' : host
        }

        vuln_node = {
            'type': 'pts_vulnerability',
            'properties': properties,
            'requirements': host
        }

        tosca_template = self.read_tosca_file(filename)
        vuln_key = f"{app_name}_vulnerability_{vulnerability['id']}"
        tosca_template['topology_template']['node_templates'][vuln_key] = vuln_node

        with open(filename, 'w') as file:
            yaml.dump(tosca_template, file, sort_keys=False)
        print(f"Vulnerability '{vuln_key}' added to TOSCA template.")

    @staticmethod
    def read_tosca_file(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def execute(self, node_name, node, filename):

        print(node_name)
        if node and node.get('type') == 'pts_webapp':
            app_name = node['properties'].get('app_name')
            app_version = node['properties'].get('app_version')
            print(f"Checking vulnerabilities for App: {app_name}")
            
                # Get user inputs for filtering criteria
            min_cvss = str(input("Enter minimum CVSS severity score or leave blank: "))
            attack_type = input("Enter a specific attack type to filter or leave blank: ")
            min_app_version = input("Enter minimum app version to filter or leave blank: ")

            # Convert min_cvss to float, handle invalid input
            #try:
                #min_cvss = float(min_cvss) if min_cvss else 0.0
            #except ValueError:
                #print("Invalid CVSS score. Defaulting to 0.0")
                #min_cvss = 0.0
            
            vulnerabilities = self.fetch_vulnerabilities(
                app_name, app_version, min_cvss, attack_type, min_app_version
            )

            if vulnerabilities:
                print("Select a vulnerability to add to the TOSCA file:")
                for i, vuln in enumerate(vulnerabilities, 1):
                    print("\n")
                    print(f"{i}. {vuln['id']} | CVSS: {vuln['cvss']}")
                    print(f"Product: {vuln['product_name']} {vuln['version']}")
                    print(f"{vuln['summary']}")

                choice = int(input("Enter your choice: "))
                if 0 < choice <= len(vulnerabilities):
                    selected_vuln = vulnerabilities[choice - 1]
                    self.add_vulnerability_to_tosca(node_name, app_name, selected_vuln, filename)
                else:
                    print("Invalid selection.")
            else:
                print("No vulnerabilities found.")
        else:
            print("Invalid node type. CVEFinderCommand only supports nodes of type 'pts_webapp'.")
