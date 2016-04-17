########### A Central Machine ###############
# The central machine first receives solutions from the m local machines,
# then loads data D from filename, and then find the best subset of size at 
# most k of the union all the local solutions V that best represents data D.
# Input:
#   filename: a string that contains the data D that needs to represented
#   k: an integer that is the cardinality constraint for the solution
#   m: an integer that is the number of local machines that this central 
#      machines should receive local solutions from.
#   e0: an auxiliary element
# Output:
#   S: a list of elements that is a subset of all local solutions V that
#      represents the data D from filename

import socket
import greedy 
import json

PORT = 2456

def main(filename, k, m, e0):
    
    #set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', PORT))
    s.listen(1)
    
    # receive all local solutions
    V = []
    count = 0
    while(count < m):
        conn, addr = s.accept()
        data = conn.recv(1024)
        conn.close()    
        Vi = json.loads(data)
        print "Received:"
        print Vi
        V += Vi
        count += 1
    print V  

    # load data that needs to be represented
    lines = open(filename, 'r')
    D = []
    for line in lines:
        e = line.split(',')
        e[-1] = e[-1][0:-1]
        D.append(e)
    
    # compute a good solution
    S =  greedy.greedy(V,D,k,e0)
    print S
    
