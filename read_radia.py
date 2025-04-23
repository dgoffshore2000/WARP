#coding:utf-8
#
def read_radia(cmpath,capath,freqn):
    import numpy as np
    addedmass=np.zeros([freqn,6,6])
    damp=np.zeros([freqn,6,6])
    cmfile=open(cmpath,'r')
    cafile=open(capath,'r')
    cmline=cmfile.readline()
    caline=cafile.readline()
    for i in range(freqn):
        cmline=cmfile.readline()
        caline=cafile.readline()
        if cmline=="" :
            break
        else:
            pass
        if caline=="" :
            break
        else:
            pass
        for j in range(6):
            cmline=cmfile.readline()
            caline=cafile.readline()
            for k in range(6):
                low=14*k
                up=14*(k+1)
                addedmass[i,j,k] = float(cmline[low:up])
                damp[i,j,k]      = float(caline[low:up])
    cmfile.close()
    cafile.close()
    return addedmass,damp

