import math

import numpy as np

import networkx as nx
from networkx.algorithms.shortest_paths.generic import shortest_path, shortest_path_length


SHORT_LINK_LEN = 5
SHORT_LINK_THRESHOLD = 25



def euclidean_distance_45deg(a, b):
    """
    Return the euclidean distance between two points if they are on one of the 45 degree
    compass points. For any other angles return None.
    """
    xd, yd = (a[0]-b[0]), (a[1]-b[1])
    if (
        abs(xd) == abs(yd) or xd == 0 or yd == 0
    ):
        return math.sqrt( (xd)**2 + (yd)**2 )


def build_graph(image):
    """
    Iterate over the provided image, building a networkx graph by adding edges for 
    adjacent pixels. Isolated pixels will be ignored.
    """
    
    data = np.array(image).T
    width, height = data.shape

    # Build a network adjacency graph for black pixels in the image.
    G = nx.Graph()


    for x in range(0, width):
        for y in range(0, height):
            curr = (x, y)
            if data[curr]: # white = 255
                continue
            
            if x < width - 1:
                right = (x + 1, y)
                if not data[right]:
                    G.add_edge(curr, right)

                if y > 0:
                    rup = (x + 1, y - 1)
                    if not data[rup]:
                        G.add_edge(curr, rup)
                                
                if y < height - 1:
                    rdown = (x + 1, y + 1)
                    if not data[rdown]:
                        G.add_edge(curr, rdown)

            if y < height - 1:
                down  = (x, y + 1)
                if not data[down]:
                    G.add_edge(curr, down)
                        
    return G
    
    
def connect_graph(G):
    """
    Add additional edges to the provided graph until all edges are connected.
    Performed iteratively, connecting each subsequent graph to the the largest
    """

    def graphs_node_iter(graphl):
        for g in graphl:
            for node in g.nodes:
                yield node
    
    graphs = sorted(nx.connected_component_subgraphs(G), key=len, reverse=True)
    if len(graphs) > 1:
    
        giant, rest = graphs[:1], graphs[1:]
        links = []
    
        while rest:
            shortest = None
            
            for g in rest:

                # For each node in the graph, compare vs. all nodes in the giant-list. The
                # difference x,y must be 1:1 (diagonal), then find the shortest + link.
                for ng in graphs_node_iter(giant):
                    for n0 in g.nodes:
                        d = euclidean_distance_45deg(ng, n0)
                        if d:
                            link = d, g, ng, n0
                            
                            if (shortest is None or d < shortest[0]):
                                shortest = link
                            
                            if d < SHORT_LINK_LEN:
                                # Sub-graph link which is short, can be used to shortcut.
                                links.append(link)

            if shortest:
                d, g, ng, n0 = shortest
                G.add_edge(ng, n0, weight=d)
                # Move the linked graph to be part of the 'giant'.
                rest.remove(g)
                giant.append(g)
        
    # Use detected short links to minimise the path lengths, where the path between
    # the connect points is over SHORT_LINK_THRESHOLD.
    for link in sorted(links, key=lambda x: x[0]):
        d, g, ng, n0 = link
        if shortest_path_length(G, ng, n0, weight='weight') >= SHORT_LINK_THRESHOLD:
            G.add_edge(ng, n0, weight=d)
        
    return G


def calculate_moves(G):
    """
    Calculate the moves neccessary to draw the provided graph.
    """
    
    # Take a copy of the input graphs nodes, so we can remove nodes as we go without affecting pathfinding.
    rgiant = list(G.nodes)
        
    n = 0
    start = (0, 0)
    last_node = start
    
    def distance(n):
        # Note: start is modified by the loop.
        return math.sqrt( 
            (n[0]-start[0])**2 + 
            (n[1]-start[1])**2 
        )

    while rgiant:
    
        n += 1    

        dnode = min(rgiant, key=distance)
        rgiant.remove(dnode)
        
        path = shortest_path(G, start, dnode, weight='weight')

        last_node = start
    
        # Traverse the path, yield all the steps required to get there.
        for node in path[1:]:
            # Yield this step to draw it (x & y can be > 1), may require multiple steps.
            yield (node[0] - last_node[0], node[1] - last_node[1])
        
            # Keep reference of where we've been for later, increase weight to discourage re-drawing.
            G.edges[(node, last_node)]['weight'] = G.edges[(node, last_node)].get('weight', 1) * 2
            last_node = node 
            
        # Chop away to avoid redundant paths.
        rgiant = set(rgiant) - set(path)
            
        # Update to our new position
        start = dnode    
        
    # Plot and yield final path to home (0,0).
    path = shortest_path(G, last_node, (0, 0), weight='weight')
    for node in path[1:]:
        # Yield this step to draw it (x & y can be > 1), may require multiple steps.
        yield (node[0] - last_node[0], node[1] - last_node[1])
        last_node = node     


def generate_moves(image):
    
    graph = build_graph(image)
    graph = connect_graph(graph)
    
    # Return a generator, so we can calculate as we draw. Both operations are slow.    
    return calculate_moves(graph)




