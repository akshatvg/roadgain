import osmnx as ox
import networkx as nx
import copy
import os
import pickle
import math
import shlex
import matplotlib.cm as cm
import matplotlib.colors as colors
from random import sample
from subprocess import Popen
from matplotlib import pyplot as plt


def node_str(node_a, node_b):
    return str(node_a) + "," + str(node_b)

def visualize_file(filename, index_to_nodes):
    true_results = {}
    with open(filename) as f:
        all_lines = f.readlines()
        for result in all_lines[1:]:
            (NODE_A, NODE_B, street_car_count, SLOWDOWN) = result.split(" ")
            true_results[node_str(index_to_nodes[int(NODE_A)], index_to_nodes[int(NODE_B)])] = float(SLOWDOWN.split("\\")[0])
    return true_results


def get_removable_streets(address, car_count=1000, streets_to_remove=200):
    # Strip the address to alphanumeric only
    stripped_address = "".join(x for x in str.lower(address) if x.isalnum())

    if not os.path.exists("./texts"):
        os.mkdir("texts")
    # Maps files
    IN_FILE = f'./texts/{stripped_address}.txt'
    IN_PKL = f'./texts/{stripped_address}.pkl'

    # If the map files don't exist, make them
    if os.path.exists(IN_FILE):
        G = pickle.load(open(IN_PKL, 'rb'))
        nodes_to_index = {n : i for i, n in enumerate(G.nodes())}
        index_to_nodes = {i : n for i, n in enumerate(G.nodes())}
    else:
        G = ox.graph_from_address(address, network_type='drive')
        pickle.dump(G, open(IN_PKL, 'wb'))
        with open(IN_FILE, 'w') as f:
            f.write('')

        with open(IN_FILE, 'w+') as f:
            f.write('{}\n'.format(len(G.nodes())))
            nodes_to_index = {n : i for i, n in enumerate(G.nodes())}
            index_to_nodes = {i : n for i, n in enumerate(G.nodes())}

            for a, b in G.edges():
                lanes = 1
                if 'lanes' in G[a][b][0]:
                    lanes = G[a][b][0]['lanes']
                if isinstance(lanes, list):
                    lanes = int(lanes[0])
                f.write('{} {} {} {}\n'.format(nodes_to_index[a], nodes_to_index[b], G[a][b][0]['length'], lanes))

    # Original cost
    OUT_FILE_GEN = f'texts/{stripped_address}_{car_count}_gen.txt'
    overall = Popen(shlex.split(f'./cars {IN_FILE} {OUT_FILE_GEN} {car_count} -1 -1'))
    overall.wait()
    orig_results = visualize_file(OUT_FILE_GEN, index_to_nodes)
    f = open(OUT_FILE_GEN, 'r')
    total_lines = f.readlines()
    total_cost = float(total_lines[0])
    f_lines = [line.split(" ") for line in total_lines[1:]]
    # Given NODE_A, NODE_B, car_count, SLOWDOWN, sort by SLOWDOWN
    def sort_key(line):
        return line[3]
    f_lines.sort(key=sort_key)

    processes = []
    for (NODE_A, NODE_B, street_car_count, SLOWDOWN) in f_lines[:streets_to_remove]:
        OUT_FILE = f'texts/{stripped_address}_{car_count}_{NODE_A}_{NODE_B}_out.txt'
        processes.append(Popen(shlex.split(f'./cars {IN_FILE} {OUT_FILE} {car_count} {NODE_A} {NODE_B}')))

    for p in processes:
        p.wait()

    results = []
    to_remove = []
    for (NODE_A, NODE_B, street_car_count, SLOWDOWN) in f_lines[:streets_to_remove]:
        OUT_FILE = f'texts/{stripped_address}_{car_count}_{NODE_A}_{NODE_B}_out.txt'
        with open(OUT_FILE) as f:
            cost_removed = float(f.readline())
            results.append([round((cost_removed - total_cost) / total_cost, 3), node_str(NODE_A, NODE_B)])
            if cost_removed < total_cost:
                to_remove.append(node_str(index_to_nodes[int(NODE_A)], index_to_nodes[int(NODE_B)]))
    best_node_a, best_node_b = min(results)[1].split(",")
    OUT_FILE = f'texts/{stripped_address}_{car_count}_{best_node_a}_{best_node_b}_out.txt'
    true_results = visualize_file(OUT_FILE, index_to_nodes)
    best_improvement = -min(results)[0]
    #shutil.rmtree("texts") 
    return orig_results, true_results, to_remove, best_improvement, G

def vals_to_colors(vals):
    ev = vals
    norm = colors.Normalize(vmin=min(ev)*0.8, vmax=max(ev))
    cmap = cm.ScalarMappable(norm=norm, cmap=cm.inferno)
    ec = ['#{:02x}{:02x}{:02x}{:02x}'.format(*[int(colo * 255) for colo in cmap.to_rgba(cl)]) for cl in ev]
    return ec


def get_plot(address):
    orig_results, true_results, to_remove, best_improvement, G = get_removable_streets(address)
    cols = vals_to_colors([(orig_results[node_str(node_a, node_b)] if node_str(node_a, node_b) in orig_results else 0) for (node_a, node_b) in G.edges()])
    for i, (node_a, node_b) in enumerate(G.edges()):
        if node_str(node_a, node_b) in to_remove:
            cols[i] = '#73db67ff'
    col2=[]
    for i in cols:
        col2.append(i[:7])
    gdf_nodes, gdf_edges = ox.save_load.graph_to_gdfs(G, nodes=True,edges=True, fill_edge_geometry=True)
    gdf_edges['edge_color'] = col2
    fplot = ox.plot.plot_graph_folium(G)
    print("wertyu")
    gx = ox.save_load.gdfs_to_graph(gdf_nodes,gdf_edges)

    if gx == G:
        print("\n\n\n\n\n\n\n\n NIGGGAAA")
    x=[]
    for i in to_remove:
        x = i.split(',')
    y=[]
    sl=[]
    if x !=[]:
        for i in x:
            y.append(int(i))
        sl.append(y)
    #print('\n\n\n\n\n\n\ngiiwedfghj',ox.plot_graph_routes(gx,sl,route_color='r'))
    #ox.plot_graph_routes(gx,sl,route_color='r')

    if sl!=[]:
        return ox.plot.plot_route_folium(gx,y,route_color='#cc0000',route_map=ox.plot.plot_graph_folium(gx,edge_width=3),route_width=5), best_improvement
    else:
        return ox.plot.plot_graph_folium(gx), best_improvement

