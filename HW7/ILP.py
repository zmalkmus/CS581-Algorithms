import argparse
import networkx as nx
from gurobipy import Model, GRB, quicksum

# ================================================================
# Bron-Kerbosch Algorithm using nx.Graph
# ================================================================
def BK(G):
    best_clique = set()
    # Precompute the neighbor sets for each node
    neighbors = {v: set(G.neighbors(v)) for v in G.nodes()}

    def bron_kerbosch(R, P, X):
        nonlocal best_clique
        if not P and not X:
            if len(R) > len(best_clique):
                best_clique = R.copy()
            return
        for v in list(P):
            bron_kerbosch(R | {v}, 
                          P & neighbors[v], 
                          X & neighbors[v])
            P.remove(v)
            X.add(v)

    bron_kerbosch(set(), set(G.nodes()), set())
    return sorted(best_clique)

# ================================================================
# Maximum Clique with ILP using nx.Graph
# ================================================================
def ILP(G):
    # --- Model Initialization ---
    model = Model("max_clique")
    model.setParam('OutputFlag', 1) # Suppress Gurobi console output
    # model.setParam('TimeLimit', 60) # Set a time limit for the optimization
    model.setParam('Threads', 0)
    # model.setParam('MIPFocus', 1) # Focus on finding feasible solutions quickly
    model.setParam('Presolve', 2) # Aggressive presolve to reduce problem size
    model.setParam('Cuts', 2) # Aggressive cut generation
    # model.setParam('Heuristics', 0.5) # Allow some heuristics to find feasible solutions

    nodes = sorted(G.nodes())
    # Create binary variables for each node
    x = model.addVars(nodes, vtype=GRB.BINARY, name="x")
    
    # For every pair of nodes, add a constraint if they are not adjacent.
    n = len(nodes)
    for i in range(n):
        u = nodes[i]
        for j in range(i+1, n):
            v = nodes[j]
            if not G.has_edge(u, v):
                model.addConstr(x[u] + x[v] <= 1, f"no_edge_{u}_{v}")
    
    # Set objective: maximize the number of selected nodes
    model.setObjective(quicksum(x[v] for v in nodes), GRB.MAXIMIZE)
    model.optimize()
    
    clique = [v for v in nodes if x[v].X > 0.5]
    return clique


def greedy_init(G):
    def get_min_degree_vertex(Residual_graph):
        '''Takes in the residual graph R and returns the node with the lowest degree'''
        degrees = [val for (node, val) in Residual_graph.degree()]
        node = [node for (node, val) in Residual_graph.degree()]
        node_degree = dict(zip(node, degrees))
        return (min(node_degree, key = node_degree.get))
    n = G.number_of_nodes()                 #Storing total number of nodes in 'n'
    max_ind_sets = []                       #initializing a list that will store maximum independent sets
    for j in range(1, n+1):
        R = G.copy()                        #Storing a copy of the graph as a residual
        neigh = [n for n in R.neighbors(j)] #Catch all the neighbours of j
        R.remove_node(j)                    #removing the node we start from
        max_ind_sets.append([j])
        R.remove_nodes_from(neigh)          #Removing the neighbours of j
        if R.number_of_nodes() != 0:
            x = get_min_degree_vertex(R)
        while R.number_of_nodes() != 0:
            neigh2 = [m for m in R.neighbors(x)]
            R.remove_node(x)
            max_ind_sets[j-1].append(x)
            R.remove_nodes_from(neigh2)
            if R.number_of_nodes() != 0:
                x = get_min_degree_vertex(R)
    return(max_ind_sets)

# ================================================================
# Clique Validation using nx.Graph
# ================================================================
def is_clique(G, clique):
    """Check if the given set of nodes forms a clique in G."""
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            if not G.has_edge(clique[i], clique[j]):
                return False
    return True

def validate_maximum_cliques(G, clique_bk, clique_ilp):
    size_bk = len(clique_bk)
    size_ilp = len(clique_ilp)
    valid_bk = is_clique(G, clique_bk)
    valid_ilp = is_clique(G, clique_ilp)
    if not valid_bk:
        print("Bron-Kerbosch output is not a clique.")
    if not valid_ilp:
        print("ILP output is not a clique.")
    if size_bk == size_ilp and valid_bk and valid_ilp:
        print("Both algorithms found valid maximum cliques of the same size.")
    else:
        print("The cliques differ in size or validity.")

# ================================================================
# Graph Parsing (returns nx.Graph)
# ================================================================
def parse_graph_file(filename):
    G = nx.Graph()
    with open(filename, 'r') as f:
        lines = f.read().strip().splitlines()
    # The first line contains the number of nodes and edges (we ignore them here)
    edge_lines = lines[1:]
    for line in edge_lines:
        u_str, v_str, _ = line.split()
        u = int(u_str)
        v = int(v_str)
        G.add_edge(u, v)
    return G

# ================================================================
# Graph Generation
# ================================================================
def generate_graph():
    import random
    import os
    n = 300
    p = 0.10
    G = nx.erdos_renyi_graph(n, p)
    os.makedirs("input", exist_ok=True)
    random_int = random.randint(1, 1000)
    filename = f"input/graph_{random_int}.txt"
    with open(filename, "w") as f:
        f.write(f"{n} {G.number_of_edges()}\n")
        for u, v in G.edges():
            f.write(f"{u} {v} 1\n")
    print(f"Graph generated and saved to {filename}")

# ================================================================
# Main function
# ================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Maximum Clique: Generate a graph or process an input graph file using Bron-Kerbosch and ILP methods."
    )
    parser.add_argument("--generate", action="store_true", help="Generate a new random graph and save it to the 'input' directory.")
    parser.add_argument("graph", nargs="?", default=None,
                        help="Path to an input graph file to process. Required if not generating a graph.")
    args = parser.parse_args()

    if args.generate:
        generate_graph()
    elif args.graph:
        G = parse_graph_file(args.graph)
        clique_bk = BK(G)
        clique_ilp = ILP(G)
        validate_maximum_cliques(G, clique_bk, clique_ilp)
        print("Bron-Kerbosch Clique:", clique_bk)
        print("ILP Clique:", clique_ilp)

if __name__ == "__main__":
    main()
