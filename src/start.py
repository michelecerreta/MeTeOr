import nmap
import yaml
import argparse

def run_nmap_scan(target):
    scanner = nmap.PortScanner()
    
    print(f"Starting basic SYN Scan on {target}")
    scanner.scan(target, arguments='-sS -T4')
    print("SYN Scan completed.")

    #print("Starting Service Version Detection.")
    #scanner.scan(target, arguments='-sV')
    #print("Service Version Detection completed.")

    #print("Starting OS Detection.")
    #scanner.scan(target, arguments='-O')
    #print("OS Detection completed.")

    print("Starting Vulnerability Detection.")
    scanner.scan(target, arguments='--script=vuln')
    print("Vulnerability Detection completed.")

    return scanner

def create_tosca_yaml(scan_data, filename="scan_results.yml"):
    tosca_template = {
        'tosca_definitions_version': 'tosca_simple_yaml_1_3',
        'description': 'Comprehensive Nmap Scan Results',
        'topology_template': {
            'node_templates': {}
        }
    }

    for host in scan_data.all_hosts():
        host_data = scan_data[host]
        tcp_ports = list(host_data['tcp'].keys()) if 'tcp' in host_data else []

        host_entry = {
            host: {
                'type': 'tosca.nodes.Network.Port',
                'properties': {
                    'ports_open': tcp_ports,
                    'status': host_data['status']['state'],
                    'os': host_data['osmatch'][0]['name'] if 'osmatch' in host_data and host_data['osmatch'] else 'Unknown',
                    'services': [{port: host_data['tcp'][port]['name']} for port in tcp_ports]
                }
            }
        }
        tosca_template['topology_template']['node_templates'].update(host_entry)

    with open(filename, 'w') as file:
        yaml.dump(tosca_template, file, sort_keys=False)
    print(f"Scan results saved to '{filename}'")

def main():
    parser = argparse.ArgumentParser(description='Run a comprehensive Nmap scan and save results in a TOSCA YAML file.')
    parser.add_argument('target', type=str, help='Target IP or hostname to scan')
    args = parser.parse_args()

    scan_results = run_nmap_scan(args.target)
    create_tosca_yaml(scan_results)

if __name__ == "__main__":
    main()
