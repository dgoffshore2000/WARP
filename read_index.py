#coding:utf-8
#
def read_index(path):
    import numpy as np
    index = open(path,'r')
    line = index.readline()
    #
    freqn = int(line[0:12])
    direcn = int(line[15:25])
    motion_n = int(line[28:38])
    force_n = int(line[38:48])
    #
    freq = np.zeros([freqn])
    direc = np.zeros([direcn])
    #
    for i in range(3 + motion_n + force_n):
        line = index.readline()
    #
    freq = [1]*freqn
    direc = [1]*direcn
    t=-1
    for i in range(direcn):
        low = 17 * i 
        up = 17 * (i + 1) 
        t = t + 1
        
        dt = float(line[low:up])/3.1415926*180
        direc[t] = dt
    #
    t = -1
    #
    line=index.readline()
    for i in range(freqn):
        low = 17 * i
        up = 17 * (i + 1)
        t = t + 1

        ft = float(line[low:up])
        freq[t] = ft
    index.close()
    return direcn,freqn,direc,freq

  
