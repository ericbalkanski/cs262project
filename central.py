########### A Central Machine ###############
# central.central(filename,k,port,m):
# The central machine receives up-to-date solutions
# from the m local machines, and each time loads
# data D from file filename to find the best subset
# of size at most k of the union all the local
# solutions V that best represents data D.
#
# Input:
#   filename: (string) names the file holding data D to be represented
#   k: (int) # of reps in requested solution set
#   port: (int) port number for communication via socket library
#   m: (int) # of local machines
#
# Output:
#   none, writes reps and scores to log as side effect
#
# Imports:
#   socket: receive messages from local machines
#   greedy: our module, see greedy.py
#   json: decodes data sent over wire
#   copy.deepcopy: to use lists by value, not reference
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#   time.time: records system time for logging
#   os.stat: checks file sizes to set buffer size
#############################################

import socket
import greedy 
import json
from copy import deepcopy
from csv import reader
from time import time
from os import stat

def central(filename, k, port, m):
    
    # make dummy entry for greedy alg
    linelen = 6 # magic number for now, num fields
    e0 = "z,"*(linelen-1)+"z"
    e1 = "a,"*(linelen-1)+"a"
    
    #set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    
    # open log
    logfile = './log/central_port' + str(port)
    centlog = open(logfile,'w')
    print 'CENTRAL started on port ' + str(port)
    centlog.write('CENTRAL, port:' + str(port) + 'k: ' + str(k) + ',  # machines: ' + str(m) + '\n')
    centlog.close()
    
    # initialize recevied reps
    V = [[],]*m
    
    # receive local solutions
    while True:
        
        # get local reps
        conn, addr = s.accept()
        bufsize = 10*stat(filename).st_size # how much data to receive, estimate
        data = conn.recv(bufsize)
        conn.close()

        # process received reps
        i,Vi = json.loads(data)
        print 'CENTRAL port ' + str(port) + ', data received from machine ' + str(i)
        V[i] = deepcopy(Vi)
        Vflat = []
        for v in V:
            Vflat += v

        # load local data to be represented
        lines = open(filename, 'r')
        D = []
        for line in reader(lines): #comma splitting, respects " "
            if len(line) == linelen: # ignore partial lines
                D.append(line)
        lines.close()

        # compute representatives of local data from received reps
        S, score =  greedy.greedy(Vflat,D,k,e0)
        
        # log reps and scores
        now = time()
        numpts = len(D)
        print 'CENTRAL port ' + str(port)+ ', \t time: ' + str(now) + '\t entries: ' + str(numpts) +'\t score: ' + str(score)
        centlog = open(logfile,'a')
        centlog.write(str(now) + '\t' +  str(numpts) + '\t' + str(score) + '\t' + str(S) + '\n')
        centlog.close()

        # write current solution so people, oracle can read it
        fsoln = './log/central_solution_' + str(port)
        f = open(fsoln,'w')
        for rep in S:
            towrite = rep[0]+','+rep[1]+',"'+rep[2]+'",'+rep[3]+','+rep[4]+','+rep[5]+'\n'
            f.write(towrite)
        f.close()