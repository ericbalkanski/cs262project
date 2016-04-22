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
#   random.randint: generates random integers
#   time.sleep: allows pause before and between inserts
#
# TODO:
# - make sure update is slow enough for oracle?
# - rather than long-pausing, start machines?
# - read from website rather than downloaded source file??

from itertools import islice
from random import randint
from time import sleep

def formatDateandOther(source, out, size):
    data = open(source,'r')
    output = open(out,'w')
    count = 0
    count2 = 0
    for datum in islice(data,1,size):
        count += 1
        if not "\"" in datum:
            count2 += 1
            output.write(datum[6:10] + datum[datum.index(","): -1]+"\n")
    print count, count2

def datamanager(source,initsize,maxsize,timescale,foracle,fcentral,*args):
    
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
        print datum
        finsert = randint(1,maxf-1)
        f[finsert].write(datum)
        # give all data to oracle
        f[0].write(datum)

    # close machine files and pause to allow other processes to start
    for i in range(0,maxf-1):
        f[i].close()
    print 'data initialized'
    sleep(50*timescale)
    print 'beginning insertion'

    # perform insertions
    oracle = open(foracle,'a')
    for datum in islice(data,initsize+1,maxsize):
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
        oracle.write(datum)
        # pause between insertions
        sleep(timescale)

    # after all data inserted, close all files
    print 'out of data, closing files.', maxsize, ' datapoints used'
    oracle.close()
    data.close()