############ The greedy algorithm for exemplar clustering #########
# An implementation of the greedy algorithm that optimizes a function f()
# under a cardinality constraint k. Also contains an implementation of the
# examplar-based clustering function f() from
# https://las.inf.ethz.ch/files/mirzasoleiman13distributed.pdf



# The distance function, simple hamming distance for testing purposes
def d(e1, e2):
    score = 0
    for i in range(len(e1)):
        if e1[i] != e2[i]:
            score += 1
    return score

# The loss function for the k-medoid problem defined in Section 3.1
# of https://las.inf.ethz.ch/files/mirzasoleiman13distributed.pdf
# Input:
#   S: a list of elements which are the exemplars
#   D: a list of elements correponding to the ground set of elements
# Output:
#   An integer corresponding to the loss from having S as exemplars
# Dependencies:
#   uses the distance function d(.,.) that is dependent on the application
def L(e0, D, new, closest):
    score = 0
    for e1 in D:
        score += min(closest[str(e1)], d(e1, new))
    return score

"""
    # Computes the value of set S over ground set D as described in Section 3.1
    # of https://las.inf.ethz.ch/files/mirzasoleiman13distributed.pdf
    # Input:
    #   S: a list of elements for which we want the value
    #   D: a list of elements correponding to the ground set of elements
    #   e0: an auxiliary element
    # Output:
    #   An integer corresponding to the value of S
    # Dependencies:
    #   uses the loss L() function defined above
    #def f(S, D, e0):
    #    return  - L(S,e0, D)
    """

# The classical greedy algorithm for maximizing f() with at most k elements
# Input:
#   V: a list of elements that are exemplars candidates
#   D: a list of elements that the exemplars should represent
#     (V = D on local machines but not on central machine)
#   k: an integer that is the cardinality constraint for greedy
#   e0: an auxiliary element
# Output:
#   S: a list of k elements from V that represent D well
# Dependencies:
#   uses the function f() that we wish to optimize defined above
def greedy(V, D, k, e0):
    S = []
    closest = dict()
    losse0 = 0
    for e in D:
        loss = d(e,e0)
        closest[str(e)] = loss
        losse0 += loss
    for i in range(k):
        bestElement = V[0]
        lS = L(e0, D,e0,closest)
        bestContribution = lS - L(e0, D,V[0],closest)
        for e in V:
            contribution = lS - L(e0, D,e,closest)
            if contribution > bestContribution:
                bestElement = e
                bestContribution = contribution
        S.append(bestElement)
        for e in D:
            distBeste = d(e,bestElement)
            if distBeste < closest[str(e)]:
                closest[str(e)] = distBeste
    score = losse0 - L(e0,D,e0,closest)
    return (S,score)
