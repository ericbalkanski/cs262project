########### A local Machine ###############
# A local machine first loads the data V it has on its machine, then computes
# a subset of V that represent V well, and then sends that solution to the 
# central server.
# Input:
#   filename: a string that is the filename for the local data V
#   k: an integer that is the cardinality constraint for the local solution
#   portCentralMachine: an integer that is the port that the local solution
#                       should be sent to
#   e0: an auxiliary element

import greedy
import socket
import json

def main(filename, k, portCentralMachine, e0):
    
    lines = open(filename, 'r')

    V = []
    for line in lines:
        e = line.split(',')
        e[-1] = e[-1][0:-1]
        V.append(e)
    print len(V)
    
    S = greedy.greedy(V,V,k,e0)
    print S
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('', portCentralMachine))
    sock.send(json.dumps(S))
    sock.close()