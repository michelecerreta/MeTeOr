import yaml
from modules.command_interface import Command

class DeleteNodeCommand(Command):
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    @staticmethod
    def read_tosca_file(filename):
        with open(filename, 'r') as file:
            return yaml.safe_load(file)

    @staticmethod
    def write_tosca_file(data, filename):
        with open(filename, 'w') as file:
            yaml.dump(data, file, sort_keys=False)

    def execute(self, node_name, node, filename=''):
        if not node or not node_name:
            print("No node selected for deletion.")
            return

        # Double confirmation
        confirm1 = input(f"Are you sure you want to delete node '{node_name}'? (yes/no): ").lower()
        if confirm1 == 'yes':
            confirm2 = input("Please type 'delete' to confirm: ").lower()
            if confirm2 == 'delete':
                # Proceed with deletion
                tosca_data = self.read_tosca_file(filename)
                if 'topology_template' in tosca_data and 'node_templates' in tosca_data['topology_template']:
                    if node_name in tosca_data['topology_template']['node_templates']:
                        del tosca_data['topology_template']['node_templates'][node_name]
                        self.write_tosca_file(tosca_data, filename)
                        print(f"Node '{node_name}' deleted successfully.")
                    else:
                        print(f"Node '{node_name}' not found in TOSCA file.")
            else:
                print("Node deletion cancelled.")
        else:
            print("Node deletion cancelled.")
