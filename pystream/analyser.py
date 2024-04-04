import networkx as nx

from pystream.core import Graph


class GraphAnalyzer:
    def _add(self, g, n):
        if n.name in g.nodes:
            return

        for c in n.children:
            self._add(g, c)
            g.add_edge(n.name, c.name)

    def visualise(self, graph: Graph) -> None:
        G = nx.Graph()
        for n in graph.root_nodes:
            self._add(G, n)
        return G
