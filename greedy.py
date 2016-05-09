############ The greedy algorithm for exemplar clustering #########
# An implementation of the greedy algorithm that optimizes a function f()
# under a cardinality constraint k. Also contains an implementation of the
# examplar-based clustering loss L() from 
# https://las.inf.ethz.ch/files/mirzasoleiman13distributed.pdf

import copy

# The distance function, which in our case is the hamming distance between
# two elements, i.e., how many features these elements differ on.
# Input:
#  e1: an element which is a list of multiple features
#  e2: another element which is also a list of multiple features
# Output:
#  an integer corresponding to how many features e1 and e2 differ on
# Assumptions:
#  The inputs e1 and e2 are assume to be lists of same length where the features
#  are ordered identically
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
def loss(S,D):
    score = 0
    for e1 in D:
        closest = 10000 # an arbitrarily high integer
        for e2 in S:
            dist = d(e1,e2)
            if dist < closest:
                closest = dist
        score += closest
    return score

# Computes the loss associated with adding element new to the current solution
# maintained by closest. This function could just use loss() previously defined,
# the advantage here is a faster runtime since greedy can maintain a dictionary 
# closest of the current closest points while only searching for element new
# with the best marginal contribution
#   e0: an auxiliary element
#   D: a list of elements correponding to the ground set of elements  
#   new: an element that is being considered to be added to the solution 
#        maintained by the greedy algorithm
#  closest: a dictionarry mapping the elements in D to their closest element
#           in the solution S maintained by the greedy algorithm according to 
#           the distance function d()
# Output:
#   An integer corresponding to the loss from having the solution S' = S U new
#   as the set of exemplars where S is the solution associated with the 
#   dictionary closest
# Dependencies:
#   uses the distance function d(.,.) that is dependent on the application
def L(e0, D, new, closest):
    score = 0
    for e1 in D:
        score += min(closest[str(e1)], d(e1, new))
    return score
    
    
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
        print i
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

# Computes the value of set S over ground set D as described in Section 3.1
# of https://las.inf.ethz.ch/files/mirzasoleiman13distributed.pdf
# Input:
#   S: a list of elements for which we want the value
#   D: a list of elements correponding to the ground set of elements
#   e0: an auxiliary element    
# Output:
#   An integer corresponding to the value of S
# Dependencies:
#   uses the loss function loss() defined above
def score(S,D,e0):
    copyS = copy.copy(S)
    copyS.append(e0)
    return loss([e0],D) - loss(copyS,D)
    

