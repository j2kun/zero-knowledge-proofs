import random

import blum_blum_shub
import commitment

ONE_WAY_PERMUTATION = blum_blum_shub.blum_blum_shub(512)
HARDCORE_PREDICATE = blum_blum_shub.parity

# a graph is a list of edges, and for simplicity we'll say
# every vertex shows up in some edge
exampleGraph = [
    (1, 2),
    (1, 4),
    (1, 3),
    (2, 5),
    (2, 5),
    (3, 6),
    (5, 6)
]

'''
    A 3-coloring is a {int: int} where the output int is 0, 1, or 2.
    Note that we want to have as few bits as possible, since the bit
    commitment scheme blows up the size of the coloring by a factor
    of n.
'''
exampleColoring = {
    1: 0,
    2: 1,
    3: 2,
    4: 1,
    5: 2,
    6: 0,
}


def numVertices(G):
    return max(v for e in G for v in e)


def randomPermutation(n):
    L = list(range(n))
    random.shuffle(L)
    return L


class Prover(object):
    def __init__(self, graph, coloring, oneWayPermutation=ONE_WAY_PERMUTATION, hardcorePredicate=HARDCORE_PREDICATE):
        self.graph = [tuple(sorted(e)) for e in graph]
        self.coloring = coloring
        self.vertices = list(range(numVertices(graph)))
        self.oneWayPermutation = oneWayPermutation
        self.hardcorePredicate = hardcorePredicate
        self.colorSchemes = None
        self.permutedColoring = None

    def commitToColoring(self):
        self.vertexToScheme = {
            v: commitment.BBSIntCommitmentScheme(
                2, self.oneWayPermutation, self.hardcorePredicate
            ) for v in self.vertices
        }

        permutation = randomPermutation(3)
        self.permutedColoring = {
            v: permutation[self.coloring[v]] for v in self.vertices
        }

        return {v: s.commit(self.permutedColoring[v])
                for (v, s) in self.vertexToScheme.items()}

    def revealColors(self, u, v):
        u, v = min(u, v), max(u, v)
        if not (u, v) in self.graph:
            raise Exception('Must query an edge!')

        return (
            (self.permutedColoring[u], self.vertexToScheme[u].reveal()),
            (self.permutedColoring[v], self.vertexToScheme[v].reveal()),
        )


class Verifier(object):
    def __init__(self, graph, oneWayPermutation=ONE_WAY_PERMUTATION, hardcorePredicate=HARDCORE_PREDICATE):
        self.graph = [tuple(sorted(e)) for e in graph]
        self.oneWayPermutation = oneWayPermutation
        self.hardcorePredicate = hardcorePredicate
        self.promisedColoring = None

    def chooseEdge(self, commitedColoring):
        self.commitedColoring = commitedColoring
        self.chosenEdge = random.choice(self.graph)
        return self.chosenEdge

    def accepts(self, revealed):
        verifier = commitment.BBSIntCommitmentVerifier(2, self.oneWayPermutation, self.hardcorePredicate)
        revealedColors = []

        for (w, (trueColor, bitSecrets)) in zip(self.chosenEdge, revealed):
            revealedColors.append(trueColor)
            if not verifier.verify(trueColor, bitSecrets, self.commitedColoring[w]):
                return False

        if revealedColors[0] != revealedColors[1]:
            return False

        return True


def runProtocol(G1, coloring):
    pass
