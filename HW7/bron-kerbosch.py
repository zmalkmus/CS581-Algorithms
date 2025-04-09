import argparse
import networkx as nx

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

def main():
    parser = argparse.ArgumentParser(description="Bron-Kerbosch Algorithm")
    parser.add_argument("graph_file", type=str, help="Path to the graph file")
    args = parser.parse_args()

    G = parse_graph_file(args.graph_file)

    clique = BK(G)

    print("Max clique:", clique)

if __name__ == "__main__":
    main()