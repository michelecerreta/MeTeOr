import yaml
import matplotlib.pyplot as plt
import networkx as nx
import argparse
from ipaddress import ip_address

def parse_tosca_file(filename):
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data

def sort_ip_addresses(host_order):
    return sorted(host_order, key=lambda ip: int(ip_address(ip)))

def generate_network_topology(data):
    G = nx.Graph()
    positions = {}
    label_positions = {}
    host_order = sort_ip_addresses(data['topology_template']['node_templates'])

    previous_host = None
    for i, host in enumerate(host_order):
        ports = data['topology_template']['node_templates'][host]['properties']['ports_open'] if 'ports_open' in data['topology_template']['node_templates'][host]['properties'] else []
        G.add_node(host, type='host', label=host)
        positions[host] = (0, -i * 2)  # Spacing hosts vertically
        label_positions[host] = (positions[host][0], positions[host][1] - 0.1)

        for j, port in enumerate(ports):
            port_node = f"{host}_Port_{port}"
            G.add_node(port_node, type='port', label=str(port))
            G.add_edge(host, port_node)
            positions[port_node] = (0.5 * (j + 1), -i * 2)
            label_positions[port_node] = (positions[port_node][0], positions[port_node][1] + 0.1)

        # Connect hosts in a bus-style (line) topology
        if previous_host:
            G.add_edge(previous_host, host, style='solid', color='black')
        previous_host = host

    colors = ['red' if G.nodes[n]['type'] == 'host' and len(list(G.neighbors(n))) == 0 else 'lightblue' if G.nodes[n]['type'] == 'host' else 'lightgreen' for n in G.nodes]
    nx.draw_networkx_nodes(G, positions, node_color=colors)
    nx.draw_networkx_edges(G, positions, edge_color='gray', style='dashed')

    # Highlight subnet connections
    bus_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('style') == 'solid']
    nx.draw_networkx_edges(G, positions, edgelist=bus_edges, edge_color='black', style='solid')

    nx.draw_networkx_labels(G, label_positions, labels={node: G.nodes[node]['label'] for node in G.nodes}, font_size=8)

    plt.title('Compact Vertical Network Topology')
    plt.axis('off')
    plt.show()

def main():
    parser = argparse.ArgumentParser(description='Generate a compact vertical network topology image from a TOSCA YAML file.')
    parser.add_argument('tosca_file', type=str, help='Path to the TOSCA YAML file')
    args = parser.parse_args()

    tosca_data = parse_tosca_file(args.tosca_file)
    generate_network_topology(tosca_data)

if __name__ == "__main__":
    main()
