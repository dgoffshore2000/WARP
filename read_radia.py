#coding:utf-8
#
# 注意（Nemoh 命名陷阱，官方手册明确）：results/CA.dat 是【辐射阻尼】、
# results/CM.dat 是【附加质量】，与文件名直觉相反。
# 本函数签名按物理含义命名：第 1 参读入 addedmass、第 2 参读入 damp，
# 因此调用方必须传 read_radia(CM.dat, CA.dat, freqn)。
# （桌面版 WARP.py/WARP_clean.py 目前传的是 (CA, CM)，其绘图口径是反的——历史遗留，未改动。）
def read_radia(addedmass_path, damping_path, freqn):
    import numpy as np
    addedmass=np.zeros([freqn,6,6])
    damp=np.zeros([freqn,6,6])
    cmfile=open(addedmass_path,'r')
    cafile=open(damping_path,'r')
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

