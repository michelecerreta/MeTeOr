import yaml
import requests
from requests.exceptions import ConnectionError, Timeout
import argparse
from bs4 import BeautifulSoup  # For parsing HTML

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def read_tosca_topology(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data

def is_web_app(ip, port):
    print(bcolors.OKBLUE + f"\ntesting {ip} : {port} ")
    try:
        response = requests.get(f"http://{ip}:{port}", timeout=5)
        if response.status_code != 200:
            print(bcolors.WARNING + f"error reponse")
            return 0

        # Check for HTML content type
        if 'text/html' not in response.headers.get('Content-Type', ''):
            print(bcolors.WARNING +f"content type not html")
            return 1

        # Check for minimum content length or specific HTML elements
        #content_length = int(response.headers.get('Content-Length', 0))
        #if content_length < 1:  # Arbitrary minimum size for a full-featured web page
        #    print(bcolors.WARNING +f"content type less than 1")
        #    return 2

        soup = BeautifulSoup(response.content, 'html.parser')
        if not soup.find('html') or not soup.find('head'):
            print(bcolors.WARNING +f"soup not find html")
            return 3
        
        print(bcolors.OKGREEN +f"its a web app!")
        return 4
    except (ConnectionError, Timeout):
        print(bcolors.FAIL +f"connection error")
        return -1

def identify_web_apps_in_topology(tosca_data):
    web_apps = {}
    for host, info in tosca_data['topology_template']['node_templates'].items():
        ports = info['properties']['ports_open'] if 'ports_open' in info['properties'] else []
        for port in ports:
            if is_web_app(host, port) > 3:
                if host in web_apps:
                    web_apps[host].append(port)
                else:
                    web_apps[host] = [port]
    return web_apps

def main():
    parser = argparse.ArgumentParser(description='Identify Web Applications in TOSCA Topology')
    parser.add_argument('tosca_file', type=str, help='Path to the TOSCA YAML file')
    args = parser.parse_args()

    tosca_data = read_tosca_topology(args.tosca_file)
    web_apps = identify_web_apps_in_topology(tosca_data)
    for host, info in tosca_data['topology_template']['node_templates'].items():
        if host in web_apps:
            print(bcolors.OKGREEN + f"\n\nHost {host} has web applications on ports: {web_apps[host]}")
       


if __name__ == "__main__":
    main()