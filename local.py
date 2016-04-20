########### A local Machine ###############
# A local machine first loads the data V it has on its machine, then computes
# a subset of V that represent V well, and then sends that solution to the 
# central server.
#
# Input:
#   filename: a string that is the filename for the local data V
#   k: an integer that is the cardinality constraint for the local solution
#   portCentralMachine: an integer that is the port that the local solution
#                       should be sent to
#
# Output:
#   none, prints and sends to central the k best reps as side effects
#
# Imports:
#   greedy: our module, see greedy.py
#   socket: sends messages between local and central machines
#   json: encodes objects to be sent over wire
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#   os.stat: returns file information, inc time of last update st_mtime
#
# TODO:
# - write dist fn between sets of reps
# - cleverer sending scheme than whole new set?

import greedy
import socket
import json
from csv import reader
from os import stat

def local(filename, k, portCentralMachine, logfile, threshold):
    
    # time of last file update
    lastupdate = 0
    
    # open log
    loclog = open(logfile,'w')
    
    # make dummy entry
    linelen = 22 # magic number for now, num fields
    e0 = "z,"*(linelen-1)+"z"
    
    # keep track of reps to central machine
    reps = []
    
    # monitor source file for updates
    while True:

        if lastupdate < stat(filename).st_mtime:
        
            # update timestamp
            lastupdate = stat(filename).st_mtime

            # read data
            lines = open(filename, 'r')
            V = []
            for line in reader(lines): #comma splitting, respects " "
                if len(line) == linelen:
                    V.append(line)
            lines.close()

            # find representatives
            print '********************'
            print '# data points ', len(V)
            if len(V) <= k:
                S = V
                score = -1
            else:
                S,score = greedy.greedy(V,V,k,e0)
            print '********************'
            print S
            
            # record score (most important for oracle)
            print 'time: ' + str(lastupdate) + '\t score: ' + str(score)
            loclog.write(str(lastupdate) + '\t' + str(score) + '\n')
    
            # compare S to preexisting reps
            if reps:
                diff = threshold*2 # TODO: dist(S,reps)
            else:
                reps = S
                diff = threshold+1
    
            # send representatives to central machine
            if diff > threshold:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('', portCentralMachine))
                sock.send(json.dumps(S))
                sock.close()
                reps = S




