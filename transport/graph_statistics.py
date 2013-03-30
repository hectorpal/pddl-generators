#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import itertools
import random
import sys


MAX_EPSILON_ATTEMPTS = 1000
MAX_CONNECTION_ATTEMPTS = 100
MAX_SEED = 10000000


class Point(object):
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point(%s, %d, %d)" % (self.name, self.x, self.y)

    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def round_distance(self, other):
        return int(round(self.distance(other)))
    

class Graph(object):
    def __init__(self):
        self.vertices = []
        self.edges = []

    def add_vertex(self, v):
        self.vertices.append(v)

    def add_edge(self, u, v):
        self.edges.append((u, v))
        self.edges.append((v, u))

    def is_connected(self):
        neighbours = defaultdict(list)
        for u, v in self.edges:
            neighbours[u].append(v)
        reached = set()
        queue = self.vertices[:1]
	reached.add(queue[0])
        while queue:
            for succ in neighbours[queue.pop()]:
                if succ not in reached:
                    reached.add(succ)
                    queue.append(succ)
        return len(reached) == len(self.vertices)

    def dump_pddl(self, out=None):
        for v in self.vertices:
            print >> out, "(location %s)" % v.name
        for u, v in self.edges:
            dist = u.round_distance(v)
            print >> out, "(connected %s %s)" % (u.name, v.name)
            print >> out, "(= (distance %s %s) %d)" % (u.name, v.name, dist)

    def dump_tikz(self, out=None):
        print >> out,  r"\documentclass{article}"
        print >> out,  r"\usepackage{tikz}"
        print >> out,  r"\begin{document}"
        print >> out,  r"\begin{tikzpicture}"
        for v in self.vertices:
            print >> out,  r"  \node[fill] (%s) at (%.2f, %.2f) {};" % (
                v.name, v.x * 0.01, v.y * 0.01);
        for u, v in self.edges:
            if u < v:
                print >> out,  r"  \draw (%s) -- (%s);" % (u.name, v.name)
        print >> out,  r"\end{tikzpicture}"
        print >> out,  r"\clearpage"
        print >> out,  r"\begin{verbatim}"
        self.dump_pddl(out)
        print >> out,  r"\end{verbatim}"
        print >> out,  r"\end{document}"


def find_suitable_point(graph, width, height, epsilon):
    for attempts in itertools.count():
        if attempts == MAX_EPSILON_ATTEMPTS:
            raise ValueError("failed to place vertex: reduce EPSILON")
        name = "loc-%d" % (len(graph.vertices) + 1)
        x = random.randrange(width)
        y = random.randrange(height)
        p = Point(name, x, y)
        if all(p.round_distance(pp) >= epsilon for pp in graph.vertices):
            return p


def generate(num_vert, width, height, connect_distance, epsilon):
    graph = Graph()
    for _ in range(num_vert):
        p = find_suitable_point(graph, width, height, epsilon)
        graph.add_vertex(p)
        for pp in graph.vertices:
            if 0 < p.round_distance(pp) <= connect_distance:
                graph.add_edge(p, pp)
    return graph


def generate_connected(num_vert, width, height, connect_distance, epsilon):
    for attempts in itertools.count():
        if attempts == MAX_CONNECTION_ATTEMPTS:
            raise ValueError(
                "failed to connect graph: increase CONNECT_DISTANCE")
        graph = generate(num_vert, width, height, connect_distance, epsilon)
        if graph.is_connected():
            return graph


def usage():
    raise SystemExit("usage: %s SEED NUM_VERTICES WIDTH HEIGHT "
                     "CONNECT_DISTANCE EPSILON" % sys.argv[0])


def parse_args():
    try:
        parameters = map(int, sys.argv[1:])
    except TypeError:
        usage()
    if len(parameters) != 6:
        usage()
    return parameters[0], parameters[1:]


def main(seed, graph_params):
    if not seed:
        seed = random.randrange(MAX_SEED) + 1
    random.seed(seed)
    try:
        g = generate_connected(*graph_params)
    except ValueError, e:
        raise SystemExit(str(e))
    print "%% %s %s" % (seed, " ".join(map(str, graph_params)))
    g.dump_tikz()


if __name__ == "__main__":
    main(*parse_args())
