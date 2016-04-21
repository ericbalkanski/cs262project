########### A data-generation simulator ###############
# Reads data from a file or website,
# writing it to file associated with machines,
# selecting the machine uniformly at random.
#
# Input:
#   source: csv file containing all test data
#   initsize: number of datapoints written to files
#             before long pause
#   maxsize: total number of datapoints written to files
#   timescale: pause between updates
#   foracle: data file for oracle (used in scoring)
#   fcentral: data file for central machine
#   *args: data file for local machines
#
# Output:
#    none, writes data to files as side effect
#
# Imports:
#   itertools.islice: allows access to parts of files
#   random.randint: generates random integers for machine selection
#   random.random: generates random floats between 0 and 1, for deletion
#   time.sleep: allows pause before and between updates
#   os.rename: allows swap file for deleting entries
#   local.local: runs local machine, allows oracle score to be logged
#
# TODO:
# - rather than long-pausing, start machines?
# - read from website rather than downloaded source file??
#############################################

from itertools import islice
from random import randint, random
from time import sleep
from os import rename
from local import local

def datamanager(source,initsize,maxsize,timescale,deleteprob,k,threshold,logoracle,foracle,fcentral,*args):
    
    # open source file
    data = open(source,'r')
    print 'source file open'
    
    # determine limits of data
    if not maxsize:
        maxsize = initsize;
        # maxsize = sum(1 for datum in data) # size of source
    initsize = min(initsize,maxsize)
    
    # open machine files
    f = []
    f.append(open(foracle,'w'))
    f.append(open(fcentral,'w'))
    for arg in args:
        f.append(open(arg,'w'))
    maxf = len(f)
    print 'machine files open, ', maxf-2, 'local'

    # write initial data to machine files
    for datum in islice(data,1,initsize):
        # randomly select machine for insert
        finsert = randint(1,maxf-1)
        f[finsert].write(datum)
        # give all data to oracle
        f[0].write(datum)

    # close machine files and pause to allow other processes to start
    for i in range(0,maxf-1):
        f[i].close()
    print 'data initialized'
    sleep(10*timescale)
    print 'beginning insertion'

    # perform insertions
    for datum in islice(data,initsize+1,maxsize):
        # delete with probability deleteprob
        if random() < deleteprob:
            # pick machine and line to delete
            fdelete = randint(1,maxf-1)
            if fdelete == 1:
                f = open(fcentral,'?')
            else:
                f = open(args[fdelete-2],'?')
            # stop if there's nothing in the file
            fsize = sum(1 for entry in f)
            if not fsize:
                continue
            # select entry to delete
            edelete = randint(0,fsize-1)
            # delete entry
            swap = open('./swap')
            for i,entry in enumerate(f):
                if i != edelete:
                    swap.write(entry)
                else:
                    deleted = entry
            f.close()
            swap.close()
            if fdelete == 1:
                rename('./swap',fcentral)
            else:
                rename('./swap',args[fedelte-2])
            # also delete from oracle file
            swap = open('./swap')
            for entry in open(foracle,'r'):
                if entry != deleted:
                    swap.write(entry)
            foracle.close()
            swap.close()
            rename('./swap',foracle)
        # randomly select machine for insert
        finsert = randint(1,maxf-1)
        # write data to machine file
        print 'inserting to machine ', finsert
        if finsert == 1:
            f = open(fcentral,'a')
            f.write(datum)
            f.close
        else:
            f = open(args[finsert-2],'a')
            f.write(datum)
            f.close
        # give all data to oracle
        oracle = open(foracle,'a')
        oracle.write(datum)
        oracle.close()
        # get oracle score
        local(foracle,k,-1,logoracle,threshold)
        # pause between insertions
        sleep(timescale)

    # after all data inserted, close all files
    print 'out of data, closing files.', maxsize, ' datapoints used'
    oracle.close()
    data.close()