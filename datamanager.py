########### Data-generation Functions ###############
# Functions to read Chicago crime data from a file,
# preprocess it, and write it to files assigned to processes,
# selecting the process uniformly at random. See in
# particular datagenerator.simulate, which initializes
# local data, starts central and local machines, updates
# data, and computes oracle scores.
#############################################

from itertools import islice
from random import randint, random
from time import sleep, time
from os import rename
from csv import reader
import multiprocessing

from local import local
from central import central
from greedy import score

########### a data preprocessing function ###############
# features(d):
# Sample from the features provided. We keep time of day,
# primary crime type, location description, arrest (boolean),
# domestic (boolean), and district number.
# See Chicago crime database for details.
# To use Boston dataset, see comments.
#
# Input:
#   d: a single entry read from crime database
#
# Output: a comma separated string of desired features
##############################################
def features(d):
    # sort times into 6 4-hour windows
    timestr = d[2]
    hour = int(timestr[11:13]) + 12*(timestr[20:22] == 'PM')
    if hour <= 4:
        timeofday = 'LATE NIGHT'
    elif hour <= 8:
        timeofday = 'EARLY MORNING'
    elif hour <= 12:
        timeofday = 'MORNING'
    elif hour <= 16:
        timeofday = 'AFTERNOON'
    elif hour <= 20:
        timeofday = 'EVENING'
    else:
        timeofday = 'NIGHT'

    # selects time of day, primary description (e.g. 'THEFT'), location
    # description (e.g. 'STREET') -- in "" because some of these contain
    # commas, whether there was an arrest, whether it was domestic, and
    # the district in which it occured
    return timeofday+','+d[5]+',"'+d[7]+'",'+d[8]+','+d[9]+','+d[11]+'\n'

    # Boston data differs from Chicago
    # print 'WARNING Boston data'
    # if d[1] == 'ARREST' or d[2] == 'Arrest' or d[3] == 'Arrest':
    #       isarrest = 'true'
    # else:
    #   isarrest = 'false'
    # return d[10]+','+d[2]+',"NA",'+isarrest+','+d[9]+','+d[4]+'\n'

########### a data file initialization function ###############
# initialinsert(source,initsize,foracle,fcentral,*args):
# Read from file source, preprocess the first initsize entries,
# and write them uniformly at random to fcentral (to be accessed
# by the central machine) or one of *args (the files to be accessed
# by each local machine). Also, write every entry to foracle to
# be read by the oracle for performance measurement.
#
# Input:
#   source: (string) filename where crime database is saved
#   initsize: (int) number of entries to insert
#   foracle: (string) filename to write oracle data
#   fcentral: (string) filename to write central machine's data
#   *args: (strings) filenames to write local machines' data
#
# Output: None, writes data to files as side effect.
#
# Imports:
#   itertools.islice: allows access to parts of files
#   random.randint: generates random integers for machine selection
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
##############################################
def initialinsert(source,initsize,foracle,fcentral,*args):
   # open source file
    data = open(source,'r')
    print 'source file open'
    
    # open machine files
    f = []
    f.append(open(foracle,'w'))
    f.append(open(fcentral,'w'))
    for arg in args:
        f.append(open(arg,'w'))
    maxf = len(f)
    print 'machine files open, ', maxf-2, ' local'
    
    # write initial data to machine files
    for d in reader(islice(data,1,initsize)):
        # only record selected features
        datum = features(d)
        # randomly select machine for insert
        finsert = randint(1,maxf-1)
        f[finsert].write(datum)
        # give all data to oracle
        f[0].write(datum)
    
    # close files
    for i in range(0,maxf-1):
        f[i].close()
    data.close()
    print 'data initialized'

########### a data file update function ###############
# update(source,initsize,maxsize,deleteprob,timescale,
#        k,baseport,thresh,isoracle,foracle,fcentral,*args):
# Read from file source, preprocess entries betwen initsize and maxsize,
# and write them uniformly at random to fcentral (to be accessed
# by the central machine) or one of *args (the files to be accessed
# by each local machine). Also, write every entry to foracle to
# be read by the oracle for performance measurement, performed if
# isoracle is true. With probability deleteprob, delete an entry
# from a local/central file and the oracle file. Perform an update
# every timescale seconds. The numbers k, baseport, and thresh
# are used in oracle scoring.
#
# Input:
#   source: (string) filename where crime database is saved
#   initsize: (int) number of entry to start with
#   maxsize: (int) number of entry to end with
#   deleteprob: (float) probability of deletion on each round
#   timescale: (int) sec to wait between updates
#   k: (int) size of oracle solution
#   baseport: (int) used to find logs for scoring
#   thresh: (int) used to find logs for scoring
#   isoracle: (bool) used to turn oracle scoring on or off
#   foracle: (string) filename to write oracle data
#   fcentral: (string) filename to write central machine's data
#   *args: (strings) filenames to write local machines' data
#
# Output: None, writes data to files as side effect.
#
# Imports:
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#   itertools.islice: allows access to parts of files
#   random.randint: generates random integers for machine selection
#   random.random: generates random floats between 0 and 1, for deletion
#   time.sleep: allows pause before and between updates
#   local.local: runs local process on oracle file for scoring
#   greedy.score: as oracle, score central machine solutions on whole dataset
#   time.time: allows system time in logs
##############################################
def update(source,initsize,maxsize,deleteprob,timescale,k,baseport,thresh,isoracle,foracle,fcentral,*args):
    # read data from file
    data = open(source,'r')
    
    # number of files
    maxf = len(args)+2
    
    # perform insertions
    for d in reader(islice(data,initsize,maxsize+1)):
        
        # only record selected features
        datum = features(d)
        
        # delete with probability deleteprob
        if random() < deleteprob:
            dodelete(maxf,foracle,fcentral,*args)
        
        # randomly select machine for insert
        finsert = randint(1,maxf-1)
        
        # write data to machine file
        if finsert == 1:
            print 'inserting to central machine'
            f = open(fcentral,'a')
            f.write(datum)
            f.close
        else:
            print 'inserting to local machine ' + str(finsert-2)
            f = open(args[finsert-2],'a')
            f.write(datum)
            f.close

        # give all data to oracle
        oracle = open(foracle,'a')
        oracle.write(datum)
        oracle.close()
    
        if not isoracle:
            # pause between insertions
            sleep(timescale)
    
        if isoracle:
            # get oracle score
            local(foracle,k,-1,0,-1)
        
            # pause between insertions
            sleep(timescale)
        
            # score current central solutions
            for p in thresh:
                port = baseport+p
                fcentreps = './log/central_solution_'+str(port)
                try:
                    # get central solution
                    centreps = open(fcentreps,'r')
                    centsol = []
                    for rep in reader(centreps):
                        centsol.append(rep)
                    centreps.close()
            
                    # get all data
                    Voracle = []
                    alldata = open(foracle,'r')
                    for datum in reader(alldata):
                        Voracle.append(datum)
                    alldata.close()
            
                    # score central solution
                    e0 = "z,"*5+"z"
                    if centsol:
                        centscore = score(centsol,Voracle,e0)
            
                    # record central solution
                    numpts = len(Voracle)
                    now = time()
                    print 'oracle score for central on port ' + str(port) + ' with ' + str(numpts) + ' points: ' + str(centscore)
                    fscore = open('./log/central_score_'+str(port),'a')
                    fscore.write(str(now) + '\t' +  str(numpts) + '\t' + str(centscore) + '\n')
                    fscore.close()
                    
                except IOError:
                        pass

    # after all data inserted, close all files
    print 'out of data, closing source file.', maxsize, ' datapoints used'
    data.close()

########### a datapoint deletion function ###############
# dodelete(maxf,foracle,fcentral,*args):
# Delete one entry at random, selecting from maxf entries.
# Delete it from both the central or local file it's in and
# the oracle file, which holds all data.
# WARNING: BUGGY AND EXPENSIVE
#
# Input:
#   maxf: (int) number of datapoints to delete from
#   foracle: (string) filename holding oracle data
#   fcentral: (string) filename holding central machine's data
#   *args: (strings) filenames holding local machines' data
#
# Output: None, writes data to files as side effect.
#
# Imports:
#   random.randint: generates random integers for machine and entry selection
#   os.rename: allows swap file for deleting entries
##############################################
def dodelete(maxf,foracle,fcentral,*args):
    # pick machine and line to delete
    fdelete = randint(1,maxf-1)
    if fdelete == 1:
        print 'deleting from central machine'
        f = open(fcentral,'r')
    else:
        print 'deleting from local machine ' + str(fdelete-2)
        f = open(args[fdelete-2],'r')
   
   # stop if there's nothing in the file
    fsize = sum(1 for entry in f)
    if not fsize:
        return
    
    # select entry to delete
    edelete = randint(0,fsize-1)

    # delete entry
    swap = open('./swap','w')
    deleted = ''
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
        rename('./swap',args[fdelete-2])

    # also delete from oracle file
    swap = open('./swap','w')
    oracle = open(foracle,'r')
    for entry in oracle:
        if entry != deleted:
            swap.write(entry)
    oracle.close()
    swap.close()
    rename('./swap',foracle)

########### a system simulation function ###############
# simulate(source,initsize,maxsize,timescale,deleteprob,
#          k,thresholds,baseport,isoracle,foracle,fcentral,*args):
# Initialize data files with first initsize entries from source,
# then start central and local machines that compute k best reps
# for a list of thresholds. Update data files until maxsize entries
# have been used.
#
# Input:
#   source: (string) filename where crime database is saved
#   initsize: (int) number of entries to start with
#   maxsize: (int) number of entries to end with
#   timescale: (int) sec to wait between updates
#   deleteprob: (float) probability of deletion on each round
#   k: (int) size of solution
#   thresholds: (list of ints) score differences to trigger on,
#               each corresponds to its own central+locals simulation
#   baseport: (int) central/local ports and log names based on this
#   isoracle: (bool) used to turn oracle scoring on or off
#   foracle: (string) filename for oracle data
#   fcentral: (string) filename for central machine's data
#   *args: (strings) filenames for local machines' data
#
# Output: None, writes data to files as side effect.
#
# Imports:
#   multiprocessing: starts local, central, and oracle simulations
#   local.local: runs local machine, allows oracle + local simulation
#   central.central: runs central machine, for simulation
##############################################
def simulate(source,initsize,maxsize,timescale,deleteprob,k,thresholds,baseport,isoracle,foracle,fcentral,*args):
    
    # insert initial data
    initialinsert(source,initsize,foracle,fcentral,*args)
    
    # determine limits of data -- in practice, this is far too expensive to matter
    #if maxsize < initsize:
    #    maxsize = initsize;
        # maxsize = sum(1 for datum in data) # size of source
        
    # start processes
    for t in thresholds:
    #t = thresholds
        port = baseport + t
        c = multiprocessing.Process(target=central, args=('./sample/central',k,port,len(args),))
        c.start()
        for m,arg in enumerate(args):
            l = multiprocessing.Process(target=local, args=(arg,k,port,t,m,))
            l.start()

    # update data with insertions and deletions
    print 'beginning insertion'
    update(source,initsize,maxsize,deleteprob,timescale,k,baseport,thresholds,isoracle,foracle,fcentral,*args)

