########### A local Machine ###############
# local.local(filename,k,port,threshold,idnum):
# A local machine first loads the data V from filename,
# then computes a k-member subset of V that represents
# V well. If the new set differs from its last-sent set
# by more than threshold, it sends that solution, along
# with its ID number idnum to the central server listening
# on port.
#
# Input:
#   filename: (string) names the file holding local data V
#   k: (int) # of reps in requested solution set
#   port: (int) port number for communication via socket library
#   threshold: (int) if solution has changed this much, send to central
#   idnum: (int) unique ID assigned to each local process
#
# Output:
#   none, prints and sends to central the k best reps as side effects
#
# Imports:
#   greedy: our module, see greedy.py
#   socket: sends messages between local and central machines
#   json: encodes data to be sent over wire
#   copy.deepcopy: to use lists by value, not reference
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#   os.stat: returns file information, inc time of last update st_mtime
#############################################

import greedy
import socket
import json
from copy import deepcopy
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
    
    # keep track of reps already sent to central machine
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
                if numpts <= k:
                    S = V
                    score = -1
                else:
                    S,score = greedy.greedy(V,V,k,e0)
                
                # if it's an oracle, log and return
                if port < 0:
                    print 'oracle on port '+ str(port) + ', \t time: ' + str(lastupdate) + '\t entries: ' + str(numpts) +'\t oracle score: ' + str(score)
                    loclog = open(logfile,'a')
                    loclog.write(str(lastupdate) + '\t' +  str(numpts) + '\t' + str(score) + '\n')
                    loclog.close()
                    return
                        
                # log time, # datapts, score
                print 'local ' + str(idnum) + ' on port '+ str(port) + ', \t time: ' + str(lastupdate) + '\t entries: ' + str(numpts) +'\t score: ' + str(score)
                loclog = open(logfile,'a')
                loclog.write(str(lastupdate) + '\t' +  str(numpts) + '\t' + str(score) + '\n')
                loclog.close()
    
                # compare to preexisting reps
                if reps and len(S) == k:
                    diff = k
                    for i in range(k):
                        for j in range(len(reps)):
                            if S[i] == reps[j]:
                                diff -= 1
                                break
                else: # on first k calculations
                    reps = deepcopy(S)
                    diff = threshold+1
    
                # if sufficient change, send reps to central machine
                print 'local ' + str(idnum) + ' on port '+ str(port) + ' diff: ' + str(diff)
                if diff > threshold and S:
                    print 'local ' + str(idnum) + ' on port '+ str(port) + ' sending to central'
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('', port))
                    sock.send(json.dumps((idnum,S)))
                    sock.close()
                    reps = deepcopy(S)
                        
        except IOError: continue # if data file won't open, keep trying
