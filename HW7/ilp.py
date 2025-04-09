import argparse
import networkx as nx
import gurobipy as gp

# ================================================================
# Bron-Kerbosch Algorithm
# ================================================================
def BK(G):
    best_clique = set()
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
# Maximum Clique with ILP
# ================================================================
def ILP(G):
    # --- Model Initialization ---
    m = gp.Model("max_clique")
    m.setParam('OutputFlag', 1)
    m.setParam('Threads', 0)

    nodes = sorted(G.nodes())
    x = m.addVars(nodes, vtype=gp.GRB.BINARY, name="x")
    
    n = len(nodes)
    for i in range(n):
        u = nodes[i]
        for j in range(i+1, n):
            v = nodes[j]
            if not G.has_edge(u, v):
                m.addConstr(x[u] + x[v] <= 1, f"no_edge_{u}_{v}")
    
    m.setObjective(gp.quicksum(x[v] for v in nodes), gp.GRB.MAXIMIZE)
    m.optimize()
    
    clique = [v for v in nodes if x[v].X > 0.5]
    return clique

# ================================================================
# Clique Validation
# ================================================================
def is_clique(G, clique):
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

def test():
    import time
    import csv
    import random
    random.seed(42)

    output_file = "test_results.csv"
    num_graphs = 10
    num_runs = 5
    n = 1000
    p = 0.01

    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["GraphID", "Method", "Run", "CliqueSize", "TimeSeconds", "IsValidClique"])

        for graph_id in range(1, num_graphs + 1):
            G = nx.erdos_renyi_graph(n, p, seed=random.randint(0, 1000))

            for run in range(1, num_runs + 1):
                # --- Bron-Kerbosch ---
                start = time.time()
                clique_bk = BK(G)
                elapsed_bk = time.time() - start
                is_valid_bk = is_clique(G, clique_bk)
                writer.writerow([graph_id, "BK", run, len(clique_bk), round(elapsed_bk, 6), is_valid_bk])

                # --- ILP ---
                start = time.time()
                clique_ilp = ILP(G)
                elapsed_ilp = time.time() - start
                is_valid_ilp = is_clique(G, clique_ilp)
                writer.writerow([graph_id, "ILP", run, len(clique_ilp), round(elapsed_ilp, 6), is_valid_ilp])

    print(f"Test results saved to {output_file}")

# ================================================================
# Main
# ================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Maximum Clique: Generate a graph or process an input graph file using Bron-Kerbosch and ILP methods."
    )
    parser.add_argument("--generate", action="store_true", 
                        help="Generate a new random graph and save it to the 'input' directory.")
    parser.add_argument("--test", action="store_true",
                        help="Run test mode on multiple random graphs and output results to CSV.")
    parser.add_argument("graph", nargs="?", default=None,
                        help="Path to an input graph file to process. Required if not generating a graph.")
    args = parser.parse_args()

    if args.generate:
        generate_graph()
    elif args.test:
        test()
    elif args.graph:
        G = parse_graph_file(args.graph)
        clique = ILP(G)
        print("Max clique: ", clique)

if __name__ == "__main__":
    main()
