import osmnx as ox
import folium
import pickle
G = ox.graph_from_address('Inner Harbor, Baltimore, Maryland, USA', network_type='drive')
pickle.dump(G, open('harbor.pkl', 'wb'))

graph_map = ox.plot_graph_folium(G, popup_attribute='name', edge_width=2)

graph_map.save('harbor.html')