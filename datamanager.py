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
#   time.time: allows system time in logs
#   os.rename: allows swap file for deleting entries
#   local.local: runs local machine, allows oracle score to be logged
#   csv.reader: separates data elements without splitting on commas
#               within quoted strings, as are found in our data
#   multiprocessing: starts local, central, and oracle simulations
#   greedy.score: score central machine solutions
#
# TODO:
# - read from website?
# - document each function
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


# select features. we keep time of day, primary crime type,
# location description, arrest (boolean), domestic (boolean),
# and district #. See Chicago crime database for details.
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

#
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

#
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

        if isoracle:
            # get oracle score
            local(foracle,k,-1,0,-1)
        
            # pause between insertions
            sleep(timescale)
        
            # score current central solutions
            for p in thresh:
                # get central solution
                port = baseport+p
                fcentreps = './log/central_solution_'+str(port)
                try:
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

#
def dodelete(maxf,foracle,fcentral,*args):
    # pick machine and line to delete
    fdelete = randint(1,maxf-1)
    if fdelete == 1:
        f = open(fcentral,'?')
    else:
        f = open(args[fdelete-2],'?')
   
   # stop if there's nothing in the file
    fsize = sum(1 for entry in f)
    if not fsize:
        return
    
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

#
def datamanager(source,initsize,maxsize,timescale,deleteprob,k,thresholds,baseport,isoracle,foracle,fcentral,*args):
    
    # insert initial data
    initialinsert(source,initsize,foracle,fcentral,*args)
    
    # determine limits of data
    #if maxsize < initsize:
    #    maxsize = initsize;
        # maxsize = sum(1 for datum in data) # size of source
        
    # start processes
    #for t in thresholds:
    t = thresholds
    port = baseport + t
    c = multiprocessing.Process(target=central, args=('./sample/central',k,port,len(args),))
    c.start()
    for m,arg in enumerate(args):
        l = multiprocessing.Process(target=local, args=(arg,k,port,t,m,))
        l.start()

    # update data with insertions and deletions
    print 'beginning insertion'
    update(source,initsize,maxsize,deleteprob,timescale,k,baseport,thresholds,isoracle,foracle,fcentral,*args)

