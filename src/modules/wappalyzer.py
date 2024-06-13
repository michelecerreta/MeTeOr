# webapp_analysis.py
import yaml
from Wappalyzer import Wappalyzer, WebPage
import requests
from modules.command_interface import Command
from libs.colors import Colors

class WappalyzerCommand(Command):
    supported_node_types = ['pts_webapp']
    def __init__(self, tosca_data):
        self.tosca_data = tosca_data

    def execute(self, node):
        if node:
            if node['type'] not in self.supported_node_types:
                print(f"NmapScanCommand does not support nodes of type: {node['type']}")
                return
            else:
                print("\nAnalyzing Web Application...")
                technologies = self.analyze_webapp(node)
                if technologies:
                    print("Detected Technologies:")
                    for tech in technologies:
                        print(f"- {tech}")
                else:
                    print("No technologies detected or unable to analyze the web application.")
        else:
            print("Invalid selection or no pts_webapp node found.")
        print("\n")
        print("#" * 10 + ' Closing Module Wappalyzer ')
        print("\n")


    def analyze_webapp(self, node):
        ip = node['properties']['host_ip']
        port = node['properties']['port_number']
        url = f"http://{ip}:{port}"

        try:
            page = WebPage.new_from_url(url)
            wappalyzer = Wappalyzer.latest()
            technologies = wappalyzer.analyze(page)
            return technologies
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {url}: {e}")
            return None
