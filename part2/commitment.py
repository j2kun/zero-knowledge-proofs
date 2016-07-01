import random


class CommitmentScheme(object):
    def __init__(self, oneWayPermutation, hardcorePredicate, securityParameter):
        '''
            oneWayPermutation: int -> int
            hardcorePredicate: int -> {0, 1}
        '''
        self.oneWayPermutation = oneWayPermutation
        self.hardcorePredicate = hardcorePredicate
        self.securityParameter = securityParameter

        # a random string of length `self.securityParameter` used only once per commitment
        self.secret = self.generateSecret()

    def generateSecret(self):
        raise NotImplemented

    def commit(self, x):
        raise NotImplemented

    def reveal(self):
        return self.secret


class BBSBitCommitmentScheme(CommitmentScheme):
    def generateSecret(self):
        # the secret is a random quadratic residue
        self.secret = self.oneWayPermutation(random.getrandbits(self.securityParameter))
        return self.secret

    def commit(self, bit):
        unguessableBit = self.hardcorePredicate(self.secret)
        return (
            self.oneWayPermutation(self.secret),
            unguessableBit ^ bit,  # python xor
        )


class BBSBitCommitmentVerifier(object):
    def __init__(self, oneWayPermutation, hardcorePredicate):
        self.oneWayPermutation = oneWayPermutation
        self.hardcorePredicate = hardcorePredicate

    def verify(self, securityString, claimedCommitment):
        trueBit = self.decode(securityString, claimedCommitment)
        unguessableBit = self.hardcorePredicate(securityString)  # wasteful, whatever
        return claimedCommitment == (
            self.oneWayPermutation(securityString),
            unguessableBit ^ trueBit,  # python xor
        )

    def decode(self, securityString, claimedCommitment):
        unguessableBit = self.hardcorePredicate(securityString)
        return claimedCommitment[1] ^ unguessableBit


class BBSIntCommitmentScheme(CommitmentScheme):
    def __init__(self, numBits, oneWayPermutation, hardcorePredicate, securityParameter=512):
        '''
            A commitment scheme for integers of a prespecified length `numBits`. Applies the
            bit commitment scheme to each bit independently.
        '''
        self.schemes = [BBSBitCommitmentScheme(oneWayPermutation, hardcorePredicate, securityParameter)
                        for _ in range(numBits)]
        super().__init__(oneWayPermutation, hardcorePredicate, securityParameter)

    def generateSecret(self):
        self.secret = [x.secret for x in self.schemes]
        return self.secret

    def commit(self, integer):
        # first pad bits to desired length
        integer = bin(integer)[2:].zfill(len(self.schemes))
        bits = [int(bit) for bit in integer]
        return [scheme.commit(bit) for scheme, bit in zip(self.schemes, bits)]


class BBSIntCommitmentVerifier(object):
    def __init__(self, numBits, oneWayPermutation, hardcorePredicate):
        self.verifiers = [BBSBitCommitmentVerifier(oneWayPermutation, hardcorePredicate)
                          for _ in range(numBits)]

    def decodeBits(self, secrets, bitCommitments):
        return [v.decode(secret, commitment) for (v, secret, commitment) in
                zip(self.verifiers, secrets, bitCommitments)]

    def verify(self, secrets, bitCommitments):
        return all(
            bitVerifier.verify(secret, commitment)
            for (bitVerifier, secret, commitment) in
            zip(self.verifiers, secrets, bitCommitments)
        )

    def decode(self, secrets, bitCommitments):
        decodedBits = self.decodeBits(secrets, bitCommitments)
        return int(''.join(str(bit) for bit in decodedBits), 2)


if __name__ == "__main__":
    import blum_blum_shub
    securityParameter = 10
    oneWayPerm = blum_blum_shub.blum_blum_shub(securityParameter)
    hardcorePred = blum_blum_shub.parity

    print('Bit commitment')
    scheme = BBSBitCommitmentScheme(oneWayPerm, hardcorePred, securityParameter)
    verifier = BBSBitCommitmentVerifier(oneWayPerm, hardcorePred)

    for _ in range(10):
        bit = random.choice([0, 1])
        commitment = scheme.commit(bit)
        secret = scheme.reveal()
        trueBit = verifier.decode(secret, commitment)
        valid = verifier.verify(secret, commitment)

        print('{} == {}? {}; {} {}'.format(bit, trueBit, valid, secret, commitment))

    print('Int commitment')
    scheme = BBSIntCommitmentScheme(10, oneWayPerm, hardcorePred)
    verifier = BBSIntCommitmentVerifier(10, oneWayPerm, hardcorePred)
    choices = list(range(1024))
    for _ in range(10):
        theInt = random.choice(choices)
        commitments = scheme.commit(theInt)
        secrets = scheme.reveal()
        trueInt = verifier.decode(secrets, commitments)
        valid = verifier.verify(secrets, commitments)

        print('{} == {}? {}; {} {}'.format(theInt, trueInt, valid, secrets, commitments))
