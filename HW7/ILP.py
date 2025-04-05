import argparse
from gurobipy import Model, GRB, quicksum

# ================================================================
# Bron-Kerbosch Algorithm
# ================================================================
def BK(adjacency_list):
    n = len(adjacency_list)
    adjacency_sets = []
    for nbrs in adjacency_list:
        adjacency_sets.append(set(nbrs))
    best_clique = set()
    def bron_kerbosch(R, P, X):
        nonlocal best_clique
        if not P and not X:
            if len(R) > len(best_clique):
                best_clique = R.copy()
            return
        for v in list(P):
            bron_kerbosch(R | {v}, 
                          P & adjacency_sets[v], 
                          X & adjacency_sets[v])
            P.remove(v)
            X.add(v)
    R = set()
    P = set(range(n))
    X = set()
    bron_kerbosch(R, P, X)
    return sorted(best_clique)

# ================================================================
# Maximum Clique with ILP
# ================================================================
def ILP(adjacency_list):
    model = Model("max_clique")
    n = len(adjacency_list)
    x = model.addVars(n, vtype=GRB.BINARY, name="x")
    for i in range(n):
        adjacency_set_i = set(adjacency_list[i])
        adjacency_set_i.add(i)
        for j in range(i+1, n):
            if j not in adjacency_set_i:
                model.addConstr(x[i] + x[j] <= 1, f"no_edge_{i}_{j}")
    model.setObjective(quicksum(x[i] for i in range(n)), GRB.MAXIMIZE)
    model.optimize()
    clique = [i for i in range(n) if x[i].X > 0.5]
    return clique

# ================================================================
# Clique Validation
# ================================================================
def is_clique(adjacency_list, clique):
    """Check if the given set of vertices forms a clique."""
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            if clique[j] not in adjacency_list[clique[i]]:
                return False
    return True

def validate_maximum_cliques(adjacency_list, clique_bk, clique_ilp):
    size_bk = len(clique_bk)
    size_ilp = len(clique_ilp)
    valid_bk = is_clique(adjacency_list, clique_bk)
    valid_ilp = is_clique(adjacency_list, clique_ilp)
    if not valid_bk:
        print("Bron-Kerbosch output is not a clique.")
    if not valid_ilp:
        print("ILP output is not a clique.")
    if size_bk == size_ilp and valid_bk and valid_ilp:
        print("Both algorithms found valid maximum cliques of the same size.")
    else:
        print("The cliques differ in size or validity.")

# ================================================================
# Graph Parsing
# ================================================================
def parse_graph_file(filename):
    with open(filename, 'r') as f:
        lines = f.read().strip().splitlines()
    edge_lines = lines[1:] 
    max_vertex = -1
    edges = []
    for line in edge_lines:
        u_str, v_str, w_str = line.split()
        u = int(u_str)
        v = int(v_str)
        edges.append((u, v))
        if u > max_vertex:
            max_vertex = u
        if v > max_vertex:
            max_vertex = v
    N_actual = max_vertex + 1
    adjacency_list = [[] for _ in range(N_actual)]
    for (u, v) in edges:
        adjacency_list[u].append(v)
        adjacency_list[v].append(u)
    return adjacency_list

# ================================================================
# Graph Generation
# ================================================================
def generate_graph():
    import networkx as nx
    import random
    import os

    n = 1000
    p = 0.01
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
    parser = argparse.ArgumentParser(description="Maximum Clique: Generate a graph or process an input graph file using Bron-Kerbosch and ILP methods.")
    parser.add_argument("--generate", action="store_true", help="Generate a new random graph and save it to the 'inputs' directory.")
    parser.add_argument("graph", nargs="?", default=None,help="Path to an input graph file to process. Required if not generating a graph.")
    args = parser.parse_args()

    if args.generate:
        generate_graph()
    elif args.graph:
        adjacency_list = parse_graph_file(args.graph)
        clique_bk = BK(adjacency_list)
        clique_ilp = ILP(adjacency_list)
        validate_maximum_cliques(adjacency_list, clique_bk, clique_ilp)
        print("Bron-Kerbosch Clique:", clique_bk)
        print("ILP Clique:", clique_ilp)

if __name__ == "__main__":
    main()