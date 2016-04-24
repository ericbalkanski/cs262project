# TODO: document

import numpy as np
import matplotlib.pyplot as plt

# filenames
root = '/home/e/Desktop/log/'
oracle = root + 'oracle'
cent0 = root + 'central_port2000'
cent1 = root + 'central_port2001'
cent2 = root + 'central_port2002'
cent3 = root + 'central_port2003'
cent4 = root + 'central_port2004'
#cent5 = root + 'central_port2005'

# open files and put systime and f scores into array
ora = np.loadtxt(oracle,skiprows=0,usecols=(0,2))
c0 = np.loadtxt(cent0,skiprows=1,usecols=(0,2))
c1 = np.loadtxt(cent1,skiprows=1,usecols=(0,2))
c2 = np.loadtxt(cent2,skiprows=1,usecols=(0,2))
c3 = np.loadtxt(cent3,skiprows=1,usecols=(0,2))
c4 = np.loadtxt(cent4,skiprows=1,usecols=(0,2))
#c5 = np.loadtxt(cent5,skiprows=1,usecols=(0,2))


# plot each process's score versus update
def mainplot():
    plt.scatter(ora[:,0],ora[:,1],color='k',s=5,label='oracle')
    plt.scatter(c0[:,0],c0[:,1],color='r',s=5,label='0')
    plt.scatter(c1[:,0],c1[:,1],color='g',s=5,label='1')
    plt.scatter(c2[:,0],c2[:,1],color='b',s=5,label='2')
    plt.scatter(c3[:,0],c3[:,1],color='c',s=5,label='3')
    plt.scatter(c4[:,0],c4[:,1],color='m',s=5,label='4')
    #    plt.scatter(c5[:,0],c5[:,1],color='y',s=5,label='5')
    plt.xlabel('system time')
    plt.ylabel('f score')
    plt.title('Global versus local solutions')
    plt.legend(loc='outside right',title='threshold')
    plt.show()

mainplot()