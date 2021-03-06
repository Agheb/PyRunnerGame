#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Dijkstra Graph Algorithm"""
from collections import defaultdict, deque


class Graph(object):
    """
        slightly modified version from mdsrosa @ https://gist.github.com/mdsrosa/c71339cb23bc51e711d8

        originally created by econchick @ https://gist.github.com/econchick/4666413

    """
    def __init__(self):
        self.nodes = set()
        self.edges = defaultdict(list)
        self.distances = {}

    def add_node(self, value):
        """adds a node to the graph"""
        if not isinstance(value, str):
            value = str(value)
        self.nodes.add(value)

    def add_edge(self, from_node, to_node, distance):
        """adds a path from node a to node b"""
        if not isinstance(from_node, str):
            from_node = str(from_node)
        if not isinstance(to_node, str):
            to_node = str(to_node)
        self.edges[from_node].append(to_node)
        self.edges[to_node].append(from_node)
        self.distances[(from_node, to_node)] = distance

    @staticmethod
    def dijkstra(graph, initial):
        """finds a dijkstra path on the graph"""
        visited = {initial: 0}
        path = {}

        nodes = set(graph.nodes)

        while nodes:
            min_node = None
            for node in nodes:
                if node in visited:
                    if min_node is None:
                        min_node = node
                    elif visited[node] < visited[min_node]:
                        min_node = node
            if min_node is None:
                break

            nodes.remove(min_node)
            current_weight = visited[min_node]

            for edge in graph.edges[min_node]:
                try:
                    weight = current_weight + graph.distances[(min_node, edge)]
                except KeyError:
                    continue
                if edge not in visited or weight < visited[edge]:
                    visited[edge] = weight
                    path[edge] = min_node

        return visited, path

    def shortest_path(self, origin, destination):
        """finds the shortest path from a to b"""
        if not isinstance(origin, str):
            origin = str(origin)
        if not isinstance(destination, str):
            destination = str(destination)

        visited, paths = self.dijkstra(self, origin)
        full_path = deque()
        _destination = paths[destination]

        while _destination != origin:
            full_path.appendleft(_destination)
            _destination = paths[_destination]

        full_path.appendleft(origin)
        full_path.append(destination)

        return visited[destination], list(full_path)
