#coding:utf-8
#
def read_motion_rao(path,direcn,freqn):
    import numpy
    mags=numpy.zeros([direcn,freqn,6])
    phas=numpy.zeros([direcn,freqn,6])
    file=open(path,'r')
    for i in range(2):
        line=file.readline()
        if line =="":
            break
        else:
            pass
    for i in range(direcn):
        line=file.readline()
        for j in range(freqn):
            line=file.readline()
            for k in range(6):
                low_a = 11 + 15 * (1 * (k-1) + 1)
                up_a  = 11 + 15 * (1 * (k-1) + 2)
                mag = float(line[low_a:up_a])
                low_p = 101 + 15 * (1 * (k-1) + 1)
                up_p  = 101 + 15 * (1 * (k-1) + 2)
                pha = float(line[low_p:up_p])
                mags[i,j,k] = mag
                phas[i,j,k] = pha
    return mags,phas
    file.close()
  
