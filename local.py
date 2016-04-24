########### A local Machine ###############
# A local machine first loads the data V it has on its machine, then computes
# a subset of V that represent V well, and then sends that solution to the 
# central server.
#
# Input:
#   filename: a string that is the filename for the local data V
#   k: an integer that is the cardinality constraint for the local solution
#   port: an integer that is the port that the local solution
#                       should be sent to
#
# Output:
#   none, prints and sends to central the k best reps as side effects
#
# Imports:
#   greedy: our module, see greedy.py
#   socket: sends messages between local and central machines
#   json: encodes data to be sent over wire
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#   os.stat: returns file information, inc time of last update st_mtime
#
# TODO:
# - cleverer sending scheme than whole new set?
#############################################

import greedy
import socket
import json
from csv import reader
from os import stat

def local(filename, k, port, threshold, idnum):
    
    # time of last file update
    lastupdate = 0
    
    # open log
    if port > 0:
        # for regular machine, delete old log
        logfile = './log/loc' + str(idnum) + '_port' + str(port)
        loclog = open(logfile,'a')
        loclog.write('LOCAL, k: ' + str(k) + ', threshold: ' + str(threshold) + '\n')
        loclog.close()
    else:
        # for oracle machine, append to old log
        logfile = './log/oracle'
    
    # make dummy entry for greedy alg
    linelen = 6 # magic number for now, num fields
    e0 = "z,"*(linelen-1)+"z"
    
    # keep track of reps sent to central machine
    reps = []
    
    # monitor source file for updates
    while True:
        
        try:

            if lastupdate < stat(filename).st_mtime:
        
                # update timestamp
                lastupdate = stat(filename).st_mtime

                # read data
                lines = open(filename, 'r')
                V = []
                for line in reader(lines): #comma splitting, respects " "
                    if len(line) == linelen: # ignore partial lines
                        V.append(line)
                    else:
                        print line
                lines.close()

                # find representatives
                numpts = len(V)
                #print '******************** \n local ' + str(idnum) + ', # data points ' + str(numpts)
                if numpts <= k:
                    S = V
                    score = -1
                else:
                    S,score = greedy.greedy(V,V,k,e0)
                #print '********************'

            
                # record score (most important for oracle)
                print 'local ' + str(idnum) + ' on port '+ str(port) + ', \t time: ' + str(lastupdate) + '\t entries: ' + str(numpts) +'\t score: ' + str(score)
                loclog = open(logfile,'a')
                loclog.write(str(lastupdate) + '\t' +  str(numpts) + '\t' + str(score) + '\n')
                loclog.close()
                
                # check if sending to central machine is possible
                if port < 0:
                    return
    
                # compare S to preexisting reps
                if len(S) == k:
                    diff = k
                    for i in range(k):
                        for j in range(len(reps)):
                            if S[i] == reps[j]:
                                diff -= 1
                                break
                else: # on first k calculations
                    reps = S
                    diff = threshold+1
    
                # send representatives to central machine
                print 'local ' + str(idnum) + ' on port '+ str(port) + ' diff: ' + str(diff)
                if diff > threshold:
                    print 'local ' + str(idnum) + ' on port '+ str(port) + ' sending to central'
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('', port))
                    sock.send(json.dumps((idnum,S)))
                    sock.close()
                    reps = S
                        
        except IOError: pass # if data file won't open, keep trying