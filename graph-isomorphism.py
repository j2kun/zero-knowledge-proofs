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
    return lambda i: L[i - 1] + 1


def makeInversePermutationFunction(L):
    return lambda i: 1 + L.index(i - 1)


def applyIsomorphism(G, f):
    return [(f(i), f(j)) for (i, j) in G]


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

        H = applyIsomorphism(self.G1, pi)

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
        choice = random.choice([1, 2])
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

        isValidIsomorphism = (graphToCheck == applyIsomorphism(H, f))
        return isValidIsomorphism


def runProtocol(G1, G2, isomorphism):
    p = Prover(G1, G2, isomorphism)
    v = Verifier(G1, G2)

    H = p.sendIsomorphicCopy()
    choice = v.chooseGraph(H)
    witnessIsomorphism = p.proveIsomorphicTo(choice)

    return v.accepts(witnessIsomorphism)


def convinceBeyondDoubt(G1, G2, isomorphism, errorTolerance=1e-20):
    probabilityFooled = 1

    while probabilityFooled > errorTolerance:
        result = runProtocol(G1, G2, isomorphism)
        assert result
        probabilityFooled *= 0.5
        print(probabilityFooled)


if __name__ == "__main__":
    G1 = exampleGraph
    n = numVertices(G1)
    p = randomPermutation(n)

    f = makePermutationFunction(p)
    finv = makeInversePermutationFunction(p)
    G2 = applyIsomorphism(G1, f)

    assert applyIsomorphism(G1, f) == G2
    assert applyIsomorphism(G2, finv) == G1

    convinceBeyondDoubt(G1, G2, p)
