import random

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


def numVertices(G):
    return max(v for e in G for v in e)


# randomPermutation: int -> (int -> int)
def randomPermutation(n):
    L = list(range(n))
    random.shuffle(L)
    return L


def makePermutationFunction(L):
    return lambda i: L[i]


def makeInversePermutationFunction(L):
    return lambda i: L.index(i)


class Prover(object):
    def __init__(self, G1, G2, isomorphism):
        '''
            isomomorphism is a list of integers representing
            an isomoprhism from G1 to G2.
        '''
        self.G1 = G1
        self.G2 = G2
        self.n = numVertices(G1)
        assert self.n == numVertices(G2)

        self.isomorphism = isomorphism
        self.state = None

    def sendIsomorphicCopy(self):
        isomorphism = randomPermutation(self.n)
        pi = makePermutationFunction(isomorphism)

        H = [(pi(i), pi(j)) for (i, j) in self.G1]

        self.state = isomorphism
        return H

    def proveIsomorphicTo(self, graphChoice):
        randomIsomorphism = self.state
        piInverse = makeInversePermutationFunction(randomIsomorphism)

        if graphChoice == 1:
            return piInverse
        else:
            f = makePermutationFunction(self.isomorphism)
            return lambda i: f(piInverse(i))


class Verifier(object):
    def __init__(self, G1, G2):
        self.G1 = G1
        self.G2 = G2
        self.n = numVertices(G1)
        assert self.n == numVertices(G2)

    def chooseGraph(self, H):
        choice = random.choice(1, 2)
        self.state = H, choice
        return choice

    def accepts(self, isomorphism):
        '''
            Return True if and only if the given isomorphism
            is a valid isomorphism between the randomly
            chosen graph in the first step, and the H presented
            by the Prover.
        '''
        H, choice = self.state
        graphToCheck = [self.G1, self.G2][choice - 1]
        f = isomorphism

        isValidIsomorphism = (graphToCheck == [(f(i), f(j)) for (i, j) in H])
        return isValidIsomorphism


def runProtocol(G1, G2, isomorphism):
    p = Prover(G1, G2, isomorphism)
    v = Verifier(G1, G2)

    H = p.sendIsomorphicCopy()
    choice = v.chooseGraph(H)
    witnessIsomorphism = p.proveIsomorphicTo(choice)

    return v.accepts(witnessIsomorphism)
