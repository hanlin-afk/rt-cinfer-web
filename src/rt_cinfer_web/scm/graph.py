"""A compact directed acyclic graph implementation for SCMs."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field


@dataclass
class CausalGraph:
    """Directed acyclic graph for causal assumptions."""

    edges: set[tuple[str, str]] = field(default_factory=set)

    def add_edge(self, parent: str, child: str) -> "CausalGraph":
        self.edges.add((parent, child))
        if not self.is_acyclic():
            self.edges.remove((parent, child))
            raise ValueError(f"Adding {parent!r}->{child!r} creates a cycle")
        return self

    @property
    def nodes(self) -> set[str]:
        nodes: set[str] = set()
        for parent, child in self.edges:
            nodes.add(parent)
            nodes.add(child)
        return nodes

    def parents(self, node: str) -> set[str]:
        return {p for p, c in self.edges if c == node}

    def children(self, node: str) -> set[str]:
        return {c for p, c in self.edges if p == node}

    def ancestors(self, node: str) -> set[str]:
        result: set[str] = set()
        stack = list(self.parents(node))
        while stack:
            current = stack.pop()
            if current in result:
                continue
            result.add(current)
            stack.extend(self.parents(current))
        return result

    def descendants(self, node: str) -> set[str]:
        result: set[str] = set()
        stack = list(self.children(node))
        while stack:
            current = stack.pop()
            if current in result:
                continue
            result.add(current)
            stack.extend(self.children(current))
        return result

    def topological_order(self) -> list[str]:
        indegree = {node: 0 for node in self.nodes}
        children: dict[str, list[str]] = defaultdict(list)
        for parent, child in self.edges:
            children[parent].append(child)
            indegree[child] += 1
        q = deque(sorted([node for node, degree in indegree.items() if degree == 0]))
        order: list[str] = []
        while q:
            node = q.popleft()
            order.append(node)
            for child in children[node]:
                indegree[child] -= 1
                if indegree[child] == 0:
                    q.append(child)
        if len(order) != len(indegree):
            raise ValueError("Graph contains a cycle")
        return order

    def is_acyclic(self) -> bool:
        try:
            self.topological_order()
            return True
        except ValueError:
            return False

    def markov_blanket(self, node: str) -> set[str]:
        parents = self.parents(node)
        children = self.children(node)
        co_parents: set[str] = set()
        for child in children:
            co_parents |= self.parents(child)
        co_parents.discard(node)
        return parents | children | co_parents


def default_web_vitals_graph(metric: str = "lcp_ms", treatment: str = "edge_cache_enabled") -> CausalGraph:
    """Default causal graph for e-commerce Web Vitals."""

    g = CausalGraph()
    confounders = [
        "device_mobile",
        "traffic_paid",
        "region_west",
        "network_rtt_ms",
        "js_kb",
        "image_kb",
        "route_complexity",
        "personalization_score",
    ]
    for c in confounders:
        g.add_edge(c, treatment)
        g.add_edge(c, metric)
    g.add_edge(treatment, metric)
    g.add_edge("hour_sin", "traffic_paid")
    g.add_edge("hour_cos", "traffic_paid")
    g.add_edge("region_west", "network_rtt_ms")
    g.add_edge("route_complexity", "js_kb")
    g.add_edge("route_complexity", "image_kb")
    return g
