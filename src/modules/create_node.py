import yaml
from modules.command_interface import Command
from libs.colors import Colors

class CreateNodeCommand(Command):  # Renamed to reflect its broader functionality
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    def read_tosca_file(self, filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def write_tosca_file(self, data, filename):
        with open(filename, 'w') as file:
            yaml.dump(data, file, sort_keys=False)

    def execute(self, target='', node_name='', filename=''):
        print(f"Creating a new TOSCA node in file: {filename}")
        node_types = self.tosca_data.get('node_types', {}).keys()
        topology_nodes = self.tosca_data.get('topology_template', {}).get('node_templates', {})

        # Check for existing node types required for creating specific nodes
        has_compute = any(node['type'] == 'pts_compute' for node in topology_nodes.values())
        has_webapp_or_compute = has_compute or any(node['type'] == 'pts_webapp' for node in topology_nodes.values())

        # Filter out node types based on existing nodes
        filtered_node_types = []
        for node_type in node_types:
            if node_type == 'pts_webapp' and not has_compute:
                continue
            if node_type == 'pts_port' and not has_compute:
                continue
            elif node_type == 'pts_vulnerability' and not has_webapp_or_compute:
                continue
            filtered_node_types.append(node_type)

        if not filtered_node_types:
            print("No valid node types available for creation.")
            return

        # Display available node types
        print("Available node types:")
        for i, node_type in enumerate(filtered_node_types, 1):
            print(f"{i}. {node_type}")

         # User selects the node type by number
        while True:
            try:
                type_choice = int(input("Select the node type (number): "))
                if 1 <= type_choice <= len(node_types):
                    selected_type = filtered_node_types[type_choice - 1]
                    break
                else:
                    print("Invalid selection. Please enter a number corresponding to the node types.")
            except ValueError:
                print("Please enter a valid integer.")

        # Get node details from user
        node_name = input("Enter the node name: ")
        properties = self.tosca_data['node_types'][selected_type].get('properties', {})

        # Prompt for each property
        node_properties = {}
        for prop in properties.keys():
            value = input(f"Enter value for {prop}: ")
            if prop == "open_ports":
                #port list
                plist = [value]
                while True:
                    #op stands for other port
                    op = input("Enter another port or press return to terminate: ")
                    if op == "":
                        break
                    else:
                        plist.append(op)
                node_properties[prop] = plist
            else:
                node_properties[prop] = value

        # Create the node
        new_node = {
            'type': selected_type,
            'properties': node_properties
        }

        # Add the node to the TOSCA template
        if 'topology_template' not in self.tosca_data:
            self.tosca_data['topology_template'] = {'node_templates': {}}
        
        self.tosca_data['topology_template']['node_templates'][node_name] = new_node

        # Save the updated TOSCA data
        print(f"Filename : {filename}")
        self.write_tosca_file(self.tosca_data, filename)
        print(f"Node '{node_name}' of type '{selected_type}' added to TOSCA template.")
        print("\n")
        print("#" * 10 + ' Closing Module Create Node ')
        print("\n")

# Additional functions as needed...
