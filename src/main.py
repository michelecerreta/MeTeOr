import os
import subprocess
import socket
import yaml
import importlib
from modules.command_interface import Command
from shutil import copy
from libs.colors import Colors


import modules

tosca_default_path = './sessions/default/default_tosca.yml'

class Invoker:
    def __init__(self):
        self.commands = {}

    def register_command(self, module_name, command):
        self.commands[module_name] = command

    def execute_command(self, module_name, node, filename, node_name):
        print(f"Executing command for module: {module_name}")
        if module_name in self.commands:
            self.commands[module_name].execute(node_name, node, filename)
        else:
            print(f"No command registered for {module_name}")

def print_ascii_art():
    color1 = Colors.randomColor()
    print (f"{color1}\n")
    print (r"""
⠀⠈⠻⣶⣤⣤⣴⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠈⠙⠻⠿⠿⠿⠿⠂⠀⠀⢦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢰⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢸⣿⣦⡀⠀⠀⣸⣄⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣷⣦⣄⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⢿⣿⣿⣿⣿⣿⣿⣷⣤⣄⣠⣴⣿⣿⣿⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣋⠉⠉⠉⠉⠉⠛⠿⣷⣄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠙⢿⣿⣿⣿⣿⡿⠛⣿⣿⣿⣷⣦⡀⠀⡄⠀⠀⠈⢻⣆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⣿⡟⠀⠀⠈⠛⠛⠿⠿⢿⡀⢻⣦⣄⡀⢈⣿⡆⠀
⠀⠀⠀⠀⠀⢲⣄⡀⠀⠀⢸⣿⠁⠀⠐⢦⣄⡀⠀⢦⣤⣄⡀⠻⣿⣿⣿⣿⣷⠀
⠀⠀⠀⠀⠀⠀⠹⣿⣷⣶⣿⣿⠀⠀⠀⠀⢻⣿⣆⠀⠹⣿⣿⡄⠘⣿⣿⣿⡿⠀
⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣿⣿⣇⠀⠀⠀⠙⠿⠟⠀⠀⢹⣿⡷⢀⣿⣿⣿⠃⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣦⡀⠀⠀⣆⠀⠀⠀⣸⣿⣷⣿⣿⡿⠃⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⣿⣶⣤⣘⣿⣶⣶⣿⣿⣿⠿⠋⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠛⠛⠛⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀""")
    
    color2 = Colors.randomColor()
    print (f"{color2}")
    
    print(r"""
 __    __  ______ ______ ______  ______  ______    
/\ "-./  \/\  ___/\__  _/\  ___\/\  __ \/\  == \   
\ \ \-./\ \ \  __\/_/\ \\ \  __\\ \ \/\ \ \  __<   
 \ \_\ \ \_\ \_____\\ \_\\ \_____\ \_____\ \_\ \_\ 
  \/_/  \/_/\/_____/ \/_/ \/_____/\/_____/\/_/ /_/ 
                                                   
    """)
    print(f"{color1}Welcome to the METEOR - Modular pEnetration TEst ORchestrator{Colors.ENDC}")
    print(f"{Colors.BLUE}SySMA Unit - IMT SCHOOL FOR ADVANCED STUDIES{Colors.ENDC}")
    print(f"{Colors.ENDC}" + "_" * 55+Colors.ENDC+"\n")


def read_tosca_file(filename):
    with open(filename, 'r') as file:
        return yaml.safe_load(file)

def write_tosca_file(data, filename):
    with open(filename, 'w') as file:
        yaml.dump(data, file)
        

def confirm_overwrite(filename):
    if os.path.exists(filename):
        choice = input(f"A file named '{filename}' already exists. Do you want to overwrite it? (y/n): ").lower()
        return choice.lower() == 'y'
    return True
    

def select_node(tosca_data):
    if 'topology_template' not in tosca_data or 'node_templates' not in tosca_data['topology_template']:
        print("No nodes available in TOSCA data.")
        return None

    print("Available nodes in TOSCA data:")
    node_templates = tosca_data['topology_template']['node_templates']

    if not node_templates:
        print("No nodes defined in the TOSCA template.")
        return None

    # Mapping to store node numbers and their corresponding names
    node_map = {}
    counter = 1

    # List nodes by type
    for node_type in ['pts_compute', 'pts_webapp', 'pts_vulnerability', 'pts_exploit']:
        for node_name, node_info in node_templates.items():
            if node_info.get('type') == node_type:
                properties = node_info.get('properties', {})
                color_attr = getattr(Colors, node_type.upper().replace('.', '_'), Colors.ENDC)

                # Display node with a number
                print(f"{counter}. [{color_attr}{node_type}{Colors.ENDC}] {color_attr}{node_name}{Colors.ENDC}")
                print(f"{Colors.PROPERTIES}{properties}{Colors.ENDC}\n")

                # Map the counter to the node name
                node_map[counter] = node_name
                counter += 1

    # Get user input
    while True:
        try:
            user_input = input("Enter the number of the node to select (or '0' proceed without slecting a node): ")
            node_number = int(user_input)

            if node_number == 0:
                return None, None
            if node_number in node_map:
                node_name = node_map[node_number]
                return node_name, node_templates.get(node_name)
            
            print("Invalid selection. Please enter a valid number.")
        except ValueError:
            print("Please enter a valid number.")


def get_available_modules(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return [(module['name'], module.get('requires', [])) for module in config['modules']]

def load_modules(config_path, tosca_data, invoker):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    print("\n")
    for module_info in config['modules']:
        module_name = module_info['name']
        module_path = module_info['path']
        module_description = module_info['description']
        #print(f"Module found: {module_name} from {module_path}")
        try:
            module = importlib.import_module(module_path)
            command_class = getattr(module, f'{module_name}Command')
            invoker.register_command(module_name, command_class(tosca_data))
            print(f"{Colors.GREEN}Registered module: {module_name}{Colors.ENDC}")
            print(f"{module_description}\n")
            #print("\n")
        except AttributeError as e:
            print(f"Error registering command for module {module_name}: {e}")
        except Exception as e:
            print(f"Unexpected error loading module {module_name}: {e}")
    print(f"\n{Colors.ENDC}")

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0
    
def main():

    print_ascii_art()
    tosca_filename, tosca_data = load_or_create_tosca_session()

     #metasploit
    command = f"msfrpcd -P Amd84H294hdJD389d -S -f -a 127.0.0.1 -p 55553"

    port = 55553
    command = f"msfrpcd -P Amd84H294hdJD389d -S -f -a 127.0.0.1 -p {port}"

    if is_port_in_use(port):
        print(f"Metasploit RPC Server is already running on port {port}")
    else:
        try:
            subprocess.Popen(command, shell=True)
            print(f"Metasploit RPC Server started on port {port}")
        except Exception as e:
            print(f"Failed to start Metasploit RPC Server: {e}")

     
    while True:
        invoker = Invoker()
        module_config = get_available_modules('modules.yaml')
        tosca_data = read_tosca_file(tosca_filename)
        selected_node = None  # Initialize selected_node as None
        node_type = ''
        node_name = ''
        load_modules('modules.yaml', tosca_data, invoker)
        # Check if nodes are present in TOSCA data
        if tosca_data.get('topology_template', {}).get('node_templates'):
            node_name, selected_node = select_node(tosca_data)
            if not selected_node:
                if input("Do you want to continue with module selection? (y/n): ").lower() != 'y':
                  
                    continue
                #continue

            # Filter modules based on the type of the selected node
            else:
                node_type = selected_node.get('type')
                print(f"selected name : {node_name}")
                print(f"selected type : {node_type}")
        available_modules = [name for name, requires in module_config if not requires or node_type in requires]
        #else:
            # If no nodes, list all modules without node requirements
        #available_modules = [name for name, requirements in module_config if not requirements]

        if not available_modules:
            print(f"No modules available for node type: {node_type}" if selected_node else "No modules available.")
            continue

        available_modules.sort()
        print(f"\n{Colors.HEADER}Select a module to execute or type '0' to exit:{Colors.ENDC}")
        for i, module_name in enumerate(available_modules, 1):
            print(f"{i}. {module_name}")

        user_choice = int(input("Enter your choice: "))
        if user_choice == 0:
            continue

        if user_choice in range(1, len(available_modules) + 1):
            selected_module_name = available_modules[user_choice - 1]
            load_modules('modules.yaml', tosca_data, invoker)
            print(f"Execute: {selected_module_name} {selected_node} {tosca_filename} {node_name}")
            invoker.execute_command(selected_module_name, selected_node, tosca_filename, node_name)

            # Refresh TOSCA data after module execution
            tosca_data = read_tosca_file(tosca_filename)
        else:
            print("Invalid selection. Please enter a valid number.")

            
        # Refresh TOSCA data after module execution
        tosca_data = read_tosca_file(tosca_filename)

        
def load_or_create_tosca_session():
    
    session_choice = ''
    while session_choice not in ['y','n']:
        session_choice = input("Do you want to load an existing scenario? (y/n): ").lower()

    if session_choice.lower() == 'y':
        session_name = input("Enter the scenario name to load: ")
        tosca_filename = f"./sessions/session_{session_name}.yml"
        if not os.path.exists(tosca_filename):
            print(f"No session found with the name '{session_name}'. Loading default session.")
            tosca_filename = tosca_default_path
    else:
        tosca_filename = tosca_default_path
        
    if tosca_filename == tosca_default_path:
    
        while True:    
            save_session_name = input("Enter a name for this scenario: ")
            save_filename = f"./sessions/session_{save_session_name}.yml"
        
            if confirm_overwrite(save_filename):
                copy(tosca_filename, save_filename)
                print(f"Session saved as '{save_filename}'.")
                print("\n")
                tosca_filename = save_filename
                break
            else:
                print("Session not saved.")
                print("\n")
                
    tosca_data = read_tosca_file(tosca_filename)
    
    return tosca_filename, tosca_data

if __name__ == "__main__":
    main()
