import yaml

from modules.command_interface import Command
from libs.colors import Colors

class EditNodeCommand(Command):
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    def read_tosca_file(self, filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    def write_tosca_file(self, data, filename):
        with open(filename, 'w') as file:
            yaml.dump(data, file, sort_keys=False)

    def execute(self, node_name, node, filename=''):
        if not node or not node_name:
            print("No node selected for deletion.")
            return
        
        # Check if the node exists in the topology
        topology_nodes = self.tosca_data.get('topology_template', {}).get('node_templates', {})
        if node_name not in topology_nodes:
            print(f"Node '{node_name}' not found in the topology.")
            return

        # Node exists, proceed to edit
        existing_node = topology_nodes[node_name]
        print(f"Found node '{node_name}' of type '{existing_node['type']}'.")

        # Display current properties
        print("Current properties:")
        for prop, value in existing_node.get('properties', {}).items():
            print(f"{prop}: {value}")

        # Prompt user for changes
        properties = existing_node.get('properties', {})
        for prop in properties.keys():
            new_value = input(f"Enter new value for {prop} (press ENTER to keep current): ")
            if new_value:
                properties[prop] = new_value

        # Update the node properties
        self.tosca_data['topology_template']['node_templates'][node_name]['properties'] = properties

        # Save the updated TOSCA data
        self.write_tosca_file(self.tosca_data, filename)
        print(f"Node '{node_name}' has been updated in the TOSCA template.")

        print("\n")
        print("#" * 10 + ' Closing Module Edit Node ')
        print("\n")

# Additional functions as needed...
