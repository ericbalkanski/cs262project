########### A Central Machine ###############
# The central machine first receives solutions from the m local machines,
# then loads data D from filename, and then find the best subset of size at 
# most k of the union all the local solutions V that best represents data D.
# Input:
#   filename: a string that contains the data D that needs to represented
#   k: an integer that is the cardinality constraint for the solution
#   m: an integer that is the number of local machines that this central 
#      machines should receive local solutions from.
#
# Output:
#   none, writes reps and scores to log as side effect
#
# Imports:
#   socket: receive messages from local machines
#   greedy: our module, see greedy.py
#   json: decodes data sent over wire
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#
# TODO:
# - track which data comes from whom
#############################################

import socket
import greedy 
import json
from csv import reader
from time import time

def central(filename, k, port, m):
    
    # make dummy entry for greedy alg
    linelen = 22 # magic number for now, num fields
    e0 = "z,"*(linelen-1)+"z"
    e1 = "a,"*(linelen-1)+"a"
    
    #set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    
    # open log
    logfile = './log/central'
    centlog = open(logfile,'w')
    centlog.write('CENTRAL, k: ' + str(k) + ',  # machines: ' + str(m))
    
    # initialize recevied reps
    V = [e1,]*m
    
    # receive local solutions
    while True:
        
        # get local reps
        conn, addr = s.accept()
        data = conn.recv(1024)
        conn.close()

        # process received reps
        i,Vi = json.loads(data)
        print "Received:"
        print Vi
        print 'from machine ' + str(i)
        V[i] = Vi
        print V

        # load local data to be represented
        lines = open(filename, 'r')
        D = []
        for line in reader(lines): #comma splitting, respects " "
            if len(line) == linelen: # ignore partial lines
                D.append(line)
        lines.close()

        # compute representatives of local data from received reps
        print '********************'
        numpts = len(D)
        print '# data points ', numpts
        S, score =  greedy.greedy(V,D,k,e0)
        print '********************'
        print S

        # log reps and scores
        now = time()
        print 'time: ' + str(now) + '\t entries: ' + str(numpts) +'\t score: ' + str(score)
        centlog.write(str(now) + '\t' +  str(numpts) + '\t' + str(score) + '\t' + S + '\n')
