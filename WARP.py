#coding:utf-8
#------------------------------------------------
#  WARP-Wave-structure Analysis Response Program
#  by WeiGao
#-----------------------------------------------
import tkinter as tk
from tkinter import ttk
from tkinter import Menu
from tkinter import filedialog
from tkinter import messagebox as mbox
import numpy as np
#
import webbrowser
#
from PIL import Image, ImageTk
from io import BytesIO
#
import base64
import tempfile
#
import subprocess
import time
import random
#
import os
import shutil
#
import ToolTips as Tips
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')  # 可选：Qt5Agg、GTK3Agg、WXAgg 等
#
from mesh_view_heal import mesh_viewer as mv
#
import read_index as ri
import read_force_rao as rfr
import read_motion_rao as rmr
import read_radia as rrd
#
#
win = tk.Tk()
win.title("WARP-Wave-structure Analysis Response Program")
win.option_add("*Menu*Font", "Arial 11")
style = ttk.Style()
style.configure(".", font=("Arial", 11)) 



ICON_BASE64 = """
AAABAAEAICAAAAEAIACoEAAAFgAAACgAAAAgAAAAQAAAAAEAIAAAAAAAABAAABILAAASCwAAAAAAAAAAAAD/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////9fX1/+fm5v/o5ub/5+fn/+jn5//o5+f/6+vr//Hx8f/7+/v////////////////////////////////////////////////////////////+/f3/7uvr/9vY2P/T0dH/1tbW/+rq6v/9/f3/////////////////7/Dw/67ExP+Ro6P/cn5+/2qFhf9xf3//boKC/3SHh/+SkpL/p6Sk/7q5uf/b29v/+vr6///////////////////////////////////////+/f3/393d/42rq/9Jj4//QX19/2CKiv+fqKj/tLOz/9DQ0P/7+/v//f39///////b3t7/QZCQ/yiiov8dxMT/BtPT/y6Fhf8yh4f/Gp+f/yKiov89oqL/fZOT/56cnP/AwMD/9fX1/////////////////////////////fv7/6XOzv8zsLD/LZSU/0inp/9omZn/QZeX/y6xsf+lwsL/qKWl/66urv/Pz8///Pz8//z8/P/p6Oj/ebi4/wrl5f8lr6//cYOD/8TJyf/I2Nj/eb29/y+0tP8lubn/XpmZ/5mXl//BwcH/+vr6///////////////////+/v+vzc3/Nba2/yuhof+itrb/+PX1//v5+f/m6Oj/Z7m5/xrFxf8/ior/Z3Bw/7e3t//8/Pz///////////+fvLz/EdfX/x2srP+NjY3/4eHh///////9+/v/vM3N/y7IyP8bxsb/bJOT/5yamv/X19f/////////////////4uLi/z+zs/8Pxsb/d4yM/+3r6//////////////////Q2Nj/IsDA/wfb2/9bgID/ube3//z8/P///////////5+8vP8R1tb/G62t/4uMjP/h4OD//////////////v7/tMbG/yLFxf8ft7f/goiI/66urv/09PT////////9/f+Iurr/ENbW/y2YmP+vrKz//Pz8/////////////////+jn5/8+sbH/Cdra/1uAgP+5t7f//Pz8////////////msHB/wzc3P8um5v/i4yM/+Hg4P/////////////////29fX/W7W1/x3IyP9Phob/mZeX/9vb2///////7Orq/z61tf8A6en/U4SE/8/MzP//////////////////////6unp/zO+vv8Wzc3/YXp6/7m3t//8/Pz///////////+gu7v/FdLS/xmwsP+LjIz/4eDg//////////////////////+jw8P/BODg/yOnp/+Hh4f/w8PD//////+4zs7/Fc7O/yC2tv95hob/5OPj///////////////////////p6en/RK2t/wjb2/9agYH/ube3//z8/P///////////5y+vv8N2tr/Iaen/4uMjP/h4OD//////////////////////9Ta2v8hwcH/DNHR/2iBgf+wrq7/+vf3/4S1tf8L4eH/I6Oj/5aWlv/x8fH//////////////////////+np6f85uLj/DNfX/11+fv+5t7f//Pz8////////////msDA/wrd3f8pn5//i4yM/+Hg4P//////////////////////7Ovr/0iqqv8G5ub/RoiI/6aiov/o5ub/WK2t/w/j4/8vlJT/q6en//j4+P//////////////////////6unp/zS9vf8R0dH/YHx8/7i2tv/7+/v///////////+hurr/Gc/P/xmwsP+LjIz/4eDg///////////////////////69vb/TbW1/xTe3v9Dg4P/nZqa/87Nzf8pwcH/Bunp/01+fv+2tLT//f39///////////////////////l5eX/Qaur/wnc3P9Xg4P/rKmp/+/v7////////////5vAwP8L3d3/KKGh/4uMjP/h4OD///////////////////////36+v9nra3/BO3t/yKjo/+TkZH/srm5/yy6uv8S2Nj/VoCA/7+8vP/+/v7////////////8/Pz/8/Ly/6y+vv8QzMz/E+Pj/0aEhP+OjIz/rKys////////////nL+//wzb2/8jpqb/i4yM/+Hg4P////////////////////////z8/3mysv8I6Oj/G6ys/42Li/+Yqan/G8nJ/w7W1v9ef3//w8HB//7+/v///////////9Xa2v88lpb/FrS0/wDk5P8L39//CsTE/xuMjP+YqKj///////////+gurr/FtHR/xmwsP+LjIz/4eDg/////////////////////////v7/hLq6/xbY2P8po6P/iImJ/46env8O1dX/B9nZ/2Z9ff/DwcH//v7+////////////5+np/4+0tP+Jurr/i7m5/4q5uf+Ku7v/ira2/9Tb2////////////5rBwf8L3Nz/LZyc/4uMjP/h4OD///////////////////////////+Ps7P/B+fn/xK8vP+Gh4f/hJ6e/x3Hx/8dwsL/ZYKC/8G/v//+/v7/////////////////////////////////////////////////////////////////nr29/xDX1/8drKz/i4yM/+Hg4P////////////////////////7+/4a4uP8P39//H6+v/4WIiP+QpKT/ENPT/wrX1/9jf3//vr29//7+/v////////////////////////////////////////////////////////////////+fvLz/EdbW/xutrf+LjIz/4eDg/////////////////////////f3/fbe3/xDg4P8iqan/iImJ/5+srP8Vz8//B93d/2B+fv+5uLj//f39/////////////////////////////////////////////////////////////////5rBwf8M3Nz/Lpub/4uMjP/h4OD////////////////////////8/P97ra3/Buvr/xO1tf+Pjo7/s7y8/zG2tv8Zz8//WYCA/7OwsP/5+fn/////////////////////////////////////////////////////////////////oLu7/xXS0v8ZsLD/i4yM/+Hg4P///////////////////////vr6/2C2tv8S4OD/LJmZ/5aWlv/T09P/JcLC/wXo6P9VfX3/qqen//T09P////////////////////////////////////////////////////////////////+cvr7/Ddra/yGoqP+LjIz/4eDg///////////////////////69vb/U62t/wjt7f8zkZH/p6Sk/+jn5/9EtLT/COfn/z6Li/+gnJz/6+vr///////////////////////////////////////+/v7/+/v7/////////////////5rAwP8K3d3/Kp+f/4uMjP/h4OD//////////////////////+3s7P9Hra3/Bevr/z6Kiv++urr//fr6/3esrP8Q3d3/Kpub/5SRkf/b29v/////////////////////////////////6uvr/+Tl5f/MzMz/+/v7////////////obq6/xnPz/8ZsLD/i4yM/+Hg4P//////////////////////09ra/xjLy/8Wy8v/Z39//9rY2P//////pMXF/w/V1f8toKD/hIWF/8TExP/+/v7///////////////////////v5+f9noqL/cZeX/8G/v//9/f3///////////+bwMD/C93d/yihof+LjIz/4eDg//////////////////////+nwMD/HMnJ/xyvr/+Vmpr/9fT0///////c4OD/KsDA/wXY2P9ogoL/qaen//Hx8f//////////////////////4+Xl/zqUlP9nh4f/zcvL/////////////////5y/v/8M29v/I6am/4uMjP/h4eH/////////////////9/T0/16xsf8N2dn/SI2N/9XS0v////////////36+v9wtLT/A+Tk/zyTk/+XlJT/z8/P//////////////////////+vx8f/G56e/3WEhP/c29v/////////////////obq6/xfR0f8ZsLD/i4yM/9/e3v////////////////+0zs7/IsTE/xq7u/+vubn//fz8/////////////////8rS0v8ztbX/FsPD/3yMjP+pqKj/7Ozs////////////9vT0/1+ysv8Yp6f/iI2N/+fn5/////////////////+Wv7//C9zc/yydnf+IiYn/wL+//+zr6//p6Oj/scTE/zO8vP8Yz8//osTE//v5+f///////////////////////fv7/4G+vv8fw8P/UZub/5yenv+1tbX/7Ozs///8/P+ty8v/DtnZ/yWdnf+amJj/8vLy///////19fX/ws7O/2Kmpv8P5OT/DNPT/1d8fP9ygYH/a4eH/1OBgf8Urq7/M729/7TQ0P/9/Pz/////////////////////////////////7e7u/2O/v/8Vxsb/ap6e/5mfn/+ZnJz/fp+f/yO3t/8M3t7/T6Cg/8PAwP/5+fn//////9rd3f85jo7/Kaen/yu2tv8axsb/J6Sk/yiWlv8vl5f/WJaW/5C4uP/f5eX///7+////////////////////////////////////////////6O3t/4Ovr/8wo6P/Ip2d/yWPj/8vl5f/b7Cw/2aamv+Do6P//fv7//7+/v//////+Pn5/9fe3v/R29v/0dvb/9La2v/R29v/1t/f/+bo6P/z8/P//v7+////////////////////////////////////////////////////////////+vr6/9Hd3f+vycn/ssrK/+Dm5v/+/Pz/7/Hx/+Hk5P//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=
"""


def set_icon(window,ICON_BASE64):
    # 
    icon_data = base64.b64decode(ICON_BASE64)
    
    # 
    with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as tmp_file:
        tmp_file.write(icon_data)
        icon_path = tmp_file.name
    
    # 
    window.iconbitmap(icon_path)
    
    # 
    try:
        os.remove(icon_path)
    except Exception as e:
        pass  
#

set_icon(win,ICON_BASE64)

#----------------------
# line marker
#----------------------
cnames = ([ '.', ',','o','v','^','<','>','s','p','*','h','H','+','x','D','d','|','_'])
#----------------------
#constant
#----------------------
pi=3.1415926
#----------------------
#      Menu
#----------------------
def _quit():
    win.quit()
    win.destroy()
#
def status():
    db=modname.get()
    if db =="":
        mbox.showwarning("Warning","Model name missed")
        return
    modelpath=os.getcwd()+"/db/" +db+'/'+db+'.dat'
    hydropath= os.getcwd()+"/db/" +db+"/mesh/"+'Inertia_hull.dat'
    resultpath= os.getcwd()+"/db/" +db+"/results/"+'FKForce.tec'
    #
    module_wid=20
    state_wid=10
    fmt='{{:{}}}{{:>{}}}'.format(module_wid,state_wid)
    #
    if os.path.exists(modelpath):
        note1= '{:<20s}'.format("Modelfile")+'{:>10s}'.format("√")
    else:
        note1= '{:<20s}'.format("Modelfile")+'{:>10s}'.format("×")
    if os.path.exists(hydropath):
        note2= '{:<20s}'.format("Hydrostatic")+'{:>8s}'.format("√")
    else:
        note2= '{:<20s}'.format("Hydrostatic")+'{:>8s}'.format("×")
    if os.path.exists(resultpath):
        note3= '{:<20s}'.format("Hydrodynamic")+'{:>4s}'.format("√")
    else:
        note3= '{:<20s}'.format("Hydrodynamic")+'{:>4s}'.format("×")
    header=fmt.format("Items","Status")
    mbox.showinfo("STATUS",header+'\n'+'='*18+'\n'+note1+'\n'+note2+'\n'+note3)
#
def files():
    db=modname.get()
    if db =="":
        mbox.showwarning("Warning","Model name missed")
        return
    modelpath=os.getcwd()+"/db/" +db+'/'+db+'.dat'
    meshpath= os.getcwd()+"/db/" +db+'/mesh.cal'
    calpath= os.getcwd()+"/db/" +db+'/nemoh.cal'
    inppath= os.getcwd()+"/db/" +db+'/input_solver.txt'
    if os.path.exists(modelpath):
       note1= "Model file                           :  "+db+'.dat'+ "       √"
    else:
        note1="Model file                           :  "+db+'.dat'+ "       ×"
    if os.path.exists(meshpath):
       note2= "Hydrostatic control file      : " +"mesh.cal"+ "       √"
    else:
        note2="Hydrostatic control file      : " +"mesh.cal"+ "       ×"
    if os.path.exists(calpath):
        note3="Hydrodynamic control file : " +"nemoh.cal"+ "     √"
    else:
        note3="Hydrodynamic control file : " +"nemoh.cal"+ "     ×"
    if os.path.exists(inppath):
        note4="Calculation control file       : " +"input_solver.txt"+ "        √"
    else:
        note4="Calculation  control file      : " +"input_solver.txt"+ "        ×"
    mbox.showinfo("File List",note1+'\n'+note2+'\n'+note3+'\n'+note4)
#
def save_set():
    db=modname.get()
    if db=="":
        mbox.showerror("ERROR","Modelname is not set.")
        return
    symm=symname.get()
    if symm=="":
        mbox.showerror("ERROR","Symm of body is not set.")
        return
    xoz1=XOZ.get()
    if xoz1=="":
        mbox.showerror("ERROR","Symm about XOZ is not set.")
        return
    xoy=bodyXOY.get()
    if xoy=="":
        mbox.showerror("ERROR","Waterplane loaction XOY is not set.")
    cog=bodyCOG.get()
    if cog=="":
        mbox.showerror("ERROR","Body'COG is not set.")
        return
    tcol1=tcol.get()
    if tcol1=="":
        mbox.showerror("ERROR","'Tcol water line move' is not set.")
    p=rho.get()
    if p=="":
        mbox.showerror("ERROR","RHO of water is not set.")
        return
    g=gravity.get()
    if g=="":
        mbox.showerror("ERROR","Gravity is not set.")
        return
    wd1=wd.get()
    if wd1=="":
        mbox.showerror("ERROR","Water depth is not set.")
        return
    nb1=nb.get()
    if nb1=="":
        mbox.showerror("ERROR","Number of body is not set.")
    #
    setfile=open(os.getcwd()+"/db/" +db+'/'+db+'_set.dg','w')
    setfile.writelines("#---------------------------------------------------------"+'\n')
    setfile.writelines("#  WARP Demo -- Based on Nemoh                            "+'\n')
    setfile.writelines("#  Generate set file  "+'\n')
    setfile.writelines("#  Programmed by Wei Gao                                  "+'\n')
    setfile.writelines("#-------------------------------------------------------- "+'\n')
    setfile.writelines("Parameter Setting:"+'\n')
    setfile.writelines('{:<20s}'.format(db)+"! Model & DB name"+'\n')
    setfile.writelines('{:<20s}'.format(symm)+"! SYMM of model"+'\n')
    setfile.writelines('{:<20s}'.format(xoz1)+"! SYMM about XOZ plane"+'\n')
    setfile.writelines('{:<20s}'.format(xoy)+"! Water plane XOY location"+'\n')
    setfile.writelines('{:<20s}'.format(cog) +"! Model COG location"+'\n')
    setfile.writelines('{:<20s}'.format(tcol1)+"! Tcol fo water level"+'\n')
    setfile.writelines('{:<20s}'.format(p) +"! RHO of water"+'\n')
    setfile.writelines('{:<20s}'.format(g) +"! Gravity"+'\n')
    setfile.writelines('{:<20s}'.format(wd1) +"! Water depth"+'\n')
    setfile.writelines('{:<20s}'.format(nb1) +"! Numbers of body"+'\n')
    #
    i=0
    while len(wmpoints)>0:
        setfile.writelines('{:<20s}'.format(wmpoints[i])+"! Measure point"+'\n')
    else:
        setfile.writelines('{:<20s}'.format("0 0")+"! Measure point"+'\n')
    degree=[1]*6
    if Dsurge.get()==0 :
        degree[0]=1
    if Dsway.get()==0 :
        degree[1]=1
    if Dheave.get()==0 :
        degree[2]=1
    if Droll.get()==0 :
        degree[3]=1
    if Dpitch.get()==0 :
        degree[4]=1
    if Dyaw.get()==0 :
        degree[5]=1
    for index in range(6):
        setfile.writelines('{:<20s}'.format(str(degree[index]))+'! Force degree at '+str(index)+'\n')
    #
    freqt1=freqt.get()
    if freqt1 =="" :
        mbox.showerror("ERROR","Freq type is not set.")
    minw1=minw.get()
    if minw1 =="" :
        mbox.showerror("ERROR","Min wave frequency is not set.")
    maxw1=maxw.get()
    if maxw1 == "":
        mbox.showerror("ERROR","Max wave frequencyis not set.")
    numw1=numw.get()
    if numw1 == "":
            mbox.showerror("ERROR","Number of wave frequency is not set.")
    #
    minwd1=minwd.get()
    if minwd1 == "":
        mbox.showerror("ERROR","Min of wave direction is not set.")
    maxwd1=maxwd.get()
    if maxwd1 == "":
        mbox.showerror("ERROR","Max of wave direction is not set.")
    numwd1=numwd.get()
    if numwd1 == "":
        mbox.showerror("ERROR","Number of wave direction is not set.")
    #        
    setfile.writelines('{:<20s}'.format(freqt1)+"! Freq type 1,2,3=[rad/s,Hz,s] "+'\n')   
    setfile.writelines('{:<20s}'.format(minw1)+"! Min Wave frequency rad/s "+'\n')
    setfile.writelines('{:<20s}'.format(maxw1)+"! Max Wave frequency rad/s "+'\n')
    setfile.writelines('{:<20s}'.format(numw1)+"! MNumber of Wave frequency"+'\n')
    #
    setfile.writelines('{:<20s}'.format(minwd1)+"! Min Wave direction deg "+'\n')
    setfile.writelines('{:<20s}'.format(maxwd1)+"! Max Wave direction deg"+'\n')
    setfile.writelines('{:<20s}'.format(numwd1)+"! Number of Wave frequency"+'\n')
    #
    shpre1=shpre.get()
    irf1=irf.get()
    if irf1 =="":
        irf1=" 0 0 0 "
    Koch1=Koch.get()
    if Koch1 =="":
        Koch1=" 0 0 0 "
    Frees1=Frees.get()
    if Frees1 =="":
        Frees1=" 0 0 0 0 "
    if shpre1=="":
        shpre1=" 0 "
    #
    raos1=raos.get()
    #
    freq_t1=freq_t.get()
    if freq_t1 == "":
        mbox.showerror("ERROR","Freq type is not set.")
    #
    setfile.writelines('{:<20s}'.format(str(irf1))+"! IRF a b c"+'\n')
    setfile.writelines('{:<20s}'.format(str(shpre1))+"! Show pressure 1 Yes; 0 No"+'\n')
    setfile.writelines('{:<20s}'.format(str(Koch1))+"! Kochin a b c"+'\n')
    setfile.writelines('{:<20s}'.format(str(Frees1))+"! Freesurface a b c d"+'\n')
    setfile.writelines('{:<20s}'.format(str(raos1))+"! Response Amplitude Operator (RAO), 0 no calculation, 1 calculated"+'\n')
    setfile.writelines('{:<20s}'.format(str(freq_t1))+"! Output freq type, 1,2,3=[rad/s,Hz,s]"+'\n')    
    #
    #  QTF setting
    #
    qtf1 = qtf.get()
    if qtf1 == 0: 
        qtff1 = 0
        qtfd1 = 0 
        qtfc1 = 0 
        fsmf1 = 0 
        fsmf_qtf1 = 0 
        hys_term1 = 0 
        freq_qtft1 = 0 
        duko1 = 0 
        HASBO1 = 0 
        HASFS_ASYMP1 = 0 
    else: 
        qtff1 = qtff.get() 
        qtfd1 = qtfd.get() 
        qtfc1 = qtfc.get() 
        fsmf1 = fsmf.get() 
        fsmf_qtf1 = fsmf_qtf.get() 
        hys_term1 = hys_term.get() 
        freq_qtft1 = freq_qtft.get() 
        duko1 = duko.get() 
        HASBO1 = HASBO.get() 
        HASFS_ASYMP1 = HASFS_ASYMP.get()
    #
    setfile.writelines('{:<20s}'.format(str(qtf1))+"! QTF flag, 1 is calculated"+'\n')
    setfile.writelines('{:<20s}'.format(str(qtff1))+"! Number of radial frequencies, Min, and Max values for the QTF computation"+'\n')
    setfile.writelines('{:<20s}'.format(str(qtfd1))+"! 0 Unidirection, Bidirection 1 "+'\n')
    setfile.writelines('{:<20s}'.format(str(qtfc1))+"! Contrib, 1 DUOK, 2 DUOK+HASBO, 3 Full QTF (DUOK+HASBO+HASFS+ASYMP)"+'\n')
    setfile.writelines('{:<20s}'.format(str(fsmf1))+"! Name of free surface meshfile (Only for Contrib 3), type 'NA' if not applicable "+'\n')
    setfile.writelines('{:<20s}'.format(str(fsmf_qtf1))+"! Free surface QTF parameters: Re Nre NBessel (for Contrib 3)"+'\n')
    setfile.writelines('{:<20s}'.format(str(hys_term1))+"! 1 Includes Hydrostatic terms of the quadratic first order motion, -[K]xi2_tilde"+'\n')
    setfile.writelines('{:<20s}'.format(str(freq_qtft1))+"! For QTFposProc, output freq type, 1,2,3=[rad/s,Hz,s]"+'\n')
    setfile.writelines('{:<20s}'.format(str(duko1))+"! For QTFposProc, 1 includes DUOK in total QTFs, 0 otherwise"+'\n')
    setfile.writelines('{:<20s}'.format(str(HASBO1))+"! For QTFposProc, 1 includes HASBO in total QTFs, 0 otherwise "+'\n')
    setfile.writelines('{:<20s}'.format(str(HASFS_ASYMP1))+"! For QTFposProc, 1 includes HASFS+ASYMP in total QTFs, 0 otherwise"+'\n')
    #
    GQ1= GQ.get()
    eps1= eps.get()
    solver1= solver.get()
    GMRES1= GMRES.get()
    if GQ1 == "":
        mbox.showerror("ERROR","GQ is not set.")
    #
    setfile.writelines('{:<20s}'.format(str(GQ1))+"! Gauss quadrature (GQ) surface integration, N^2 GQ Nodes, specify N(1,4) "+'\n')
    setfile.writelines('{:<20s}'.format(str(eps1))+"! eps_zmin for determine minimum z of flow and source points of panel, zmin=eps_zmin*body_diameter  "+'\n')
    setfile.writelines('{:<20s}'.format(str(solver1))+"! 0 GAUSS ELIM.; 1 LU DECOMP.: 2 GMRES	!Linear system solver  "+'\n')
    setfile.writelines('{:<20s}'.format(str(GMRES1))+"! Restart parameter, Relative Tolerance, max iter -> additional input for GMRES "+'\n')
    
    #
    setfile.close()
    mbox.showinfo("NOTE","Setting file saved" )
#
def read_set():
    db=modname.get()
    if db=="":
        mbox.showerror("ERROR","No model name input.")
        return
    if os.path.exists(os.getcwd()+"/db/" +db+'/'+db+'_set.dg'):
        setfile=open(os.getcwd()+"/db/" +db+'/'+db+'_set.dg','r')
    else:
        mbox.showerror("ERROR","No set file.")
        return
    line=setfile.readline()
    for index in range(6):
        line=setfile.readline()
    line=setfile.readline()
    symname.set(line[0:9])
    line=setfile.readline()
    XOZ.set(line[0:9])
    line=setfile.readline()
    bodyXOY.set(line[0:9])
    line=setfile.readline()
    bodyCOG.set(line[0:15])
    line=setfile.readline()
    tcol.set(line[0:9])
    line=setfile.readline()
    rho.set(line[0:9])
    line=setfile.readline()
    gravity.set(line[0:9])
    line=setfile.readline()
    wd.set(line[0:9])
    line=setfile.readline()
    nb.set(line[0:9])
    line=setfile.readline()
    line=setfile.readline()
    deg=line[0:3]
    if int(deg)==1:
        ch_surge.select()
    line=setfile.readline()
    deg=line[0:3]
    if int(deg)==1:
        ch_sway.select()
    line=setfile.readline()
    deg=line[0:3]
    if int(deg)==1:
        ch_heave.select()
    line=setfile.readline()
    deg=line[0:3]
    if int(deg)==1:
        ch_roll.select()
    line=setfile.readline()
    deg=line[0:3]
    if int(deg)==1:
        ch_pitch.select()
    line=setfile.readline()
    deg=line[0:3]
    if int(deg)==1:
        ch_yaw.select()
    #
    line=setfile.readline()
    freqt.set(line[0:9])
    line=setfile.readline()
    minw.set(line[0:9])
    line=setfile.readline()
    maxw.set(line[0:9])
    line=setfile.readline()
    numw.set(line[0:9])
    line=setfile.readline()
    minwd.set(line[0:9])
    line=setfile.readline()
    maxwd.set(line[0:9])
    line=setfile.readline()
    numwd.set(line[0:9])
    line=setfile.readline()
    irf.set(line[0:9])
    line=setfile.readline()
    if line[0:9]=='':
        shpre.set(0)
    elif int(line[0:9])==1:
        shpre.set(1)
    else:
        shpre.set(0)
    #
    line=setfile.readline()
    Koch.set(line[0:9])
    line=setfile.readline()
    Frees.set(line[0:9])
    #
    line=setfile.readline()
    if line[0:9]=='':
        raos.set(1)
    elif int(line[0:9])==1:
        raos.set(1)
    else:
        raos.set(0)    
    line=setfile.readline()
    freq_t.set(line[0:9])
    #   
    line=setfile.readline()
    if int(line[0:9])==1:
        qtf.set(1)
        #
        line=setfile.readline()
        qtff.set(line[0:9])
        line=setfile.readline()
        qtfd.set(line[0:9])
        line=setfile.readline()
        qtfc.set(line[0:9])
        line=setfile.readline()
        fsmf.set(line[0:9])
        line=setfile.readline()
        fsmf_qtf.set(line[0:9])
        line=setfile.readline()
        hys_term.set(line[0:9])
        line=setfile.readline()
        freq_qtft.set(line[0:9])
        line=setfile.readline()
        duko.set(line[0:9])
        line=setfile.readline()
        HASBO.set(line[0:9])
        line=setfile.readline()
        HASFS_ASYMP.set(line[0:9])
    else:
        qtf.set(0)     
        for i in range(10):
            line=setfile.readline()
    #
    #   run setting
    #
    line=setfile.readline()
    GQ.set(line[0:9])
    line=setfile.readline()
    eps.set(line[0:9])    
    line=setfile.readline()
    solver.set(line[0:9])    
    line=setfile.readline()
    GMRES.set(line[0:9])    
    #
    mbox.showinfo("NOTE","Set file read finish.Measure points" +'\n' \
                          " setting should inputed by user")
#
#  web help
#
def web_help():
    try:
        webbrowser.open("https://dgoffshore2000.github.io/WARP/", new=2)  # new=2表示在新标签页打开
    except Exception as e:
        print(f"无法打开网页: {e}")
#
#

def about():
    #
    # 
    pai_base64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQIBAQEBAQIBAQECAgICAgICAgIDAwQDAwMDAwICAwQDAwQEBAQEAgMFBQQEBQQEBAT/2wBDAQEBAQEBAQIBAQIEAwIDBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAT/wAARCANkAtwDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD+/iiiigAooooAKKKKACiiigAooooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigCHY3p+tGxvT9amooAh2N6frRsb0/WpqKAIdjen60bG9P1qaigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKK/yYf8Ag7H/AOU1nxz/AOyV+AP/AFEtPoA/1nqK/wAA1PuinUAf7+FFf4B9FAH+/hRX+AfRQB/v4UV/gH0UAf7+FFf4B9FAH+/hRX+AfX+8z8Df+SI/Bv8A7JZ4f/8ATPa0Aer5FFfypf8AB4cf+NRdn/2dX4O/9JPEVf5WuGHOCMd+mKAP9/YkAZPApQQeRX8WP/Bk3PI37D/7XZmlaQj9qy2Uea7OcHwhofAyf84r+06gAooooAKKKKACiiv8GH44f8lj+MH/AGVDX/8A0739AH+89RX+APTk+8uTjnrQB/v7dKAQeRX8WP8AwZNSO37D37XpB8xv+GrYdxdmJP8AxSGiepP+TX9oozgZAB9B0FAFmiiigAoor/Nd/wCD2r/k979kD/s1W5/9S7WaAP8ASior/AHooA/3+KK/xu/+DdP/AJTU/sE/9lQ1H/1E/EFf7IlABRRRQAUV/iv/APBcL/lL7/wUS/7Os8Vf+lpr8qpPvt9aAP8Af1or/AHr+6z/AIMef+S0/wDBQb/sl/gL/wBO3iSgD/RMo60V/iv/APBb/wD5S4f8FEP+zrvFP/pbQB/tQUV/gH0UAf7+FFf4B9FAH+/hRX82f/Bpt/yhX+Bf/ZUPiD/6l2p1/SZQAUUUUAFFFf5MP/B2P/yms+Of/ZK/AH/qJafQB/rPUV/hcfsH/wDJ737Gv/Z1fw8/9S/SK/3R6ACiiigAor/Jh/4Ox/8AlNZ8c/8AslfgD/1EtPr+atPuigD/AH8qK/wD6KAP9/Civ8A7IHUgfjSblHf+tAH+/lRX+AZvX3NJ5g7D+lAH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ooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAhU4Oe3epcj1H51A/wAue+KpyTlckngU1GT2Qm0t2alFNQgqPXAzTqlyinZvUe+wUUzzE/vCk82P+9+hpOUVux2fYkop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njN4GYHwQzHwn8LMJjYQxFaNZPEKDtJTg3rGT3UEtlbzPz3hfwy8TJ+JuF4641xFKfs4yjaGuji1vp1fY+wE+6KdSDp1z7+tLX8PwVoJeR/VwUUUVQBRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABQQDwaKKAEIB6iloopNJ7gFN2r6U6ihJLYAAA4FIAB0FLRT3d2Ky2sGBkH06UEA8GiigwG7F9P1p1FFF29zdRitkQEknJpKKKBliiiiiyWwBSYA7daWiudJJ3QABgYHQcCiiiugVktgooooGFFFFAAQDwaCAeDRRR5CsiueRg9KKKKLsd3a3QsU3Yvp+tOopNJ7oLIbsX0/WlCgZ469e9LRQoxWyAOlIQD1FLRXO0nugCiiimAUUUUAFFFFACFQTkj9aXAyD6dKKK3srcvQwXxXEKgnJH601gApwKfTX+6axWrVzouxwAHApoRRwB+pp1Fb3a2JaTVmAAHAooooDlj2CggHg0UUByx7Ddi+n606iim23uCSWyCiiikMKKKKACiiigAowMg+nSiigBCoJyR+tLRRQBXooooAKcvJAPSm05PvCk0pKzQEu0cDHTpzSbF9P1p1FMwe7GeWn90UoRAchRTqKFpsF3sFFFFBuFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABTX+6adTX+6aAHUUUUAFFFFBzhRRRQdAUUUUAFFFFABRRRQAUUUVnKN9UAUUUVoAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAU1/umnU1/umgCGnoMnPpTKnAwAPSgBaKKKACiiigiUb6oKKKKAjG2rCiiigsKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACmv9006mv900AOooooAKKKKCJRvqgooooLCiiigAooooAKKKKACiiigAoooJA5NABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABTX+6adTX+6aAGIMnPpUtIBgAelLQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAf/9m4Svc/AAAAAGm/SXBeLZpByIUuIi7fZMw="
    #
    
    about_window = tk.Toplevel()
    about_window.title("About WARP")
    
    set_icon(about_window,ICON_BASE64)
    
    # 创建左侧图文容器
    left_frame = ttk.Frame(about_window)
    left_frame.grid(row=0, column=0, padx=20, sticky='n')

    # 添加打赏标题
    lbl_donation = ttk.Label(left_frame, text="Donation/打赏")
    lbl_donation.pack(pady=(0,5))

    # 加载Base64图片

    image_data = base64.b64decode(pai_base64)
    img = Image.open(BytesIO(image_data))
    img = img.resize((160, 160), Image.LANCZOS)  # 更高质量的缩放
    photo = ImageTk.PhotoImage(img)
    
    # 显示图片
    img_label = ttk.Label(left_frame, image=photo)
    img_label.image = photo  # 保持引用
    img_label.pack()

    # 右侧文字信息（优化对齐）
    info_text = (
        "This Program (WARP) is developed by Wei Gao.\n"
        "WARP is used as pre-process tool for open-source BEM software Nemoh.\n"
        "QQ        : 3230129780\n"
        "WeChat  : dg_offshore\n"
        "E-mail    : dg_offshore@163.com"
    )
    right_frame = ttk.Frame(about_window)
    right_frame.grid(row=0, column=1, padx=20, sticky='nw')
    
    text_label = ttk.Label(right_frame, text=info_text, 
                          justify='left', 
                          font=("Segoe UI", 10))
    text_label.pack(pady=10, anchor='w')

    # 统一关闭按钮样式
    btn_style = ttk.Style()
    btn_style.configure('TButton', padding=6, font=("微软雅黑", 9))
    
    btn_close = ttk.Button(about_window, text="Close", 
                          style='TButton',
                          command=about_window.destroy)
    btn_close.grid(row=1, column=0, columnspan=2, 
                  pady=20, sticky='s')

    # 配置网格布局权重
    about_window.grid_columnconfigure(0, weight=0)
    about_window.grid_columnconfigure(1, weight=1)
    about_window.grid_rowconfigure(0, weight=1)
#
#
# mesh view heal
#
def mesh_view():
    db=modname.get()
    if db =="":
       mbox.showerror('ERRO','DB name not specified!')
       return
    #
    modelpath = os.getcwd()+'/DB/' + db +'/'+db+'.dat'
    mv(modelpath)
#
#
#    menu
#
#
menuBar = Menu(win)
win.config(menu = menuBar)
fileMenu = Menu(menuBar, tearoff = 0)
menuBar.add_cascade(label="File  ", menu=fileMenu)
fileMenu.add_command(label = "Status",command=status)
fileMenu.add_command(label = "File list",command=files)
fileMenu.add_command(label = "Save Set file",command=save_set)
fileMenu.add_command(label = "Read Set file",command=read_set)
fileMenu.add_command(label = "Exit",command=_quit)
#
#
helpMenu = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label="Help  ", menu=helpMenu)
helpMenu.add_command(label = "About",command=about)
helpMenu.add_command(label = "Help",command=web_help)
#----------------------
# Tabs set
#----------------------
tabControl = ttk.Notebook(win)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text = " MODEL ")
tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text = " HYST ")
tab3 = ttk.Frame(tabControl)
tabControl.add(tab3, text = " MASS ")
tab4 = ttk.Frame(tabControl)
tabControl.add(tab4, text = " CASE ")
tab5 = ttk.Frame(tabControl)
tabControl.add(tab5, text = " RUN  ")
tab6 = ttk.Frame(tabControl)
tabControl.add(tab6, text = " PLOT ")
#
tabControl.pack(expand=1, fill="both")
#----------------------
#   tab1 GUI
# command click -- convert APDL file
#----------------------
def newfolder():
    db=modname.get()
    dbpath=os.getcwd()+'/DB/' + db
    model=modname.get()
    if model =="":
        mbox.showerror('ERRO','Please input model name!')
        return
    #
    if not os.path.exists(dbpath):
        os.mkdir(dbpath)
        mbox.showinfo('Note','Folder established.')
        return
    else:
        mbox.showinfo('Note','Folder already exist.')
#
# tab1 model readin
#
monty1 = ttk.LabelFrame(tab1, text = "Working Folder and Model Set")
monty1.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='W')
monty10 = ttk.LabelFrame(monty1, text = "Name:",)
monty10.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='N')
#
ttk.Label(monty10, text="Set model name   ").grid(column=0, row=2,sticky='W')
modname = tk.StringVar()
modnameEntered = ttk.Entry(monty10, width=12, textvariable=modname)
modnameEntered.grid(column=0, row=3)
Tips.createToolTip(modnameEntered,'Model name without .bat')
#
ttk.Label(monty10, text="Set model symm  ").grid(column=0, row=4,sticky='W')
symname = tk.StringVar()
symnameEntered = ttk.Entry(monty10, width=12, textvariable=symname)
symnameEntered.grid(column=0, row=5)
Tips.createToolTip(symnameEntered,'Only symm abt XOZ plane, 2 0 for no XOZ symm; 2 1 for XOZ symm')
#
ttk.Label(monty10, text="  ").grid(column=0, row=6,sticky='W')
newfolder = ttk.Button(monty10, text="New Folder",command = newfolder)
newfolder.grid(column= 0, row=7)
#
monty11 = ttk.LabelFrame(monty1, text = "Note:")
monty11.grid(column = 2, row = 0, padx = 8, pady = 4,sticky='N')
notetab1= \
"* Model name is the model's name without .dat" + "\n" \
"* Model symmetry x y,x means symmetry about" + "\n" \
"  YOZ plane;y means symmetry about XOZ plane" + "\n" \
"  " + "\n"
ttk.Label(monty11, text=notetab1).grid(column=0, row=0,sticky='NW')
#
montyView = ttk.LabelFrame(monty1, text = "Mesh Check")
montyView.grid(column = 3, row = 0, padx = 8, pady = 4,sticky='N')
meshview = ttk.Button(montyView, text="Mesh View",command = mesh_view)
meshview.grid(column= 0, row=0)

#
#
#------------------------------------------------------------------------------
# tab2 hydrostatic
# command click -- hydrostatic
#
def runmesh():
    db=modname.get()
    #
    #
    dbpath=os.getcwd()+"/db/" +db+"/mesh.cal"
    model=modname.get()
    symm=symname.get()
    symmXOZ=XOZ.get()
    loca=bodyXOY.get()
    cg=bodyCOG.get()
    g=gravity.get()
    rh=rho.get()
    tc=tcol.get()
    if db =="":
       mbox.showerror('ERRO','DB name not specified!')
       return
    if model =="":
       mbox.showerror('ERRO','DB name not specified!')
       return
    if symmXOZ =="":
       mbox.showerror('ERRO','XOZ symm is not specified!')
       return
    if loca =="":
       mbox.showerror('ERRO','Body Location is not specified!')
       return
    if cg =="":
       mbox.showerror('ERRO','Body COG is not specified!')
       return
    #
    #
    filepath = os.getcwd()+"/db/" +db+"/summary_model.txt"
    if  os.path.exists(filepath ):
        print(1)
    else:
        modelpath = os.getcwd()+"/db/" +db+"/"+db+".dat"
        modelfile = open(modelpath ,"r")
        line = modelfile.readline()
        symm = line
        n=0
        m=0
        line = modelfile.readline()
        temp = line.split()
        while temp[0]!='0':
            n=n+1
            line = modelfile.readline()
            temp = line.split()
        line = modelfile.readline()
        temp = line.split()
        while temp[0]!='0':
            m=m+1
            line = modelfile.readline()
            temp = line.split()
        #
        summarypath=os.getcwd()+"/db/" +db+ '/summary_model.txt'
        sufile=open(summarypath,"w")
        sufile.writelines("*-----------------------------------------"+'\n')
        sufile.writelines("*   WARP Demo -- Based on Nemoh            "+'\n')
        sufile.writelines("*   Programmed by Wei Gao                 "+'\n')
        sufile.writelines("*-----------------------------------------"+'\n')
        sufile.writelines("1.Model Summary"+'\n')
        sufile.writelines("  DB name  is                : "+ str(db)+'\n')
        sufile.writelines("  Model name is              : "+ str(model)+'\n')
        sufile.writelines("  Symm of model is           : "+ str(symm)+'\n')
        sufile.writelines("  Total model node number is : "+ str(n)+'\n')
        sufile.writelines("  Total model panel number is: "+ str(m)+'\n')
        sufile.close()
        #
        modelfile.close()
        #
        model_no_dat = open(os.getcwd()+"/db/" +db+"/"+model,'w')
        model_no_dat.writelines(str(n)+'\n')
        model_no_dat.writelines(str(m)+'\n')
        #
        modelfile = open(modelpath ,"r")
        line = modelfile.readline()
        line = modelfile.readline()
        temp = line.split()
        while temp[0]!='0':
            a = "{0:.3f}".format(float(temp[1]))
            b = "{0:.3f}".format(float(temp[2]))
            c = "{0:.3f}".format(float(temp[3]))
            a = '{:>15s}'.format(temp[1])
            b = '{:>15s}'.format(temp[2])
            c = '{:>15s}'.format(temp[3])
            model_no_dat.writelines(a+b+c+'\n')
            line = modelfile.readline()
            temp = line.split()
        #
        line = modelfile.readline()
        temp = line.split()
        while temp[0]!='0':
            a = '{:>5s}'.format(temp[0])
            b = '{:>5s}'.format(temp[1])
            c = '{:>5s}'.format(temp[2])
            d = '{:>5s}'.format(temp[3])
            model_no_dat.writelines(a+b+c+d+'\n')
            line = modelfile.readline()
            temp = line.split()
        model_no_dat.close()
        modelfile.close()
    #
    #
    #
    file=open(os.getcwd()+"/db/" +db+"/summary_model.txt","r")
    line=file.readline()
    while line:
        line=file.readline()
        if line[0:30]=="  Total model panel number is:" :
            panels=line[31:35]
        elif line[0:30]=="  Total model node number is :":
            nodes=line[31:35]
    file.close()
    #
    if panels =="":
       mbox.showerror('ERRO','Penels is not specified!')
       return
    if tc =="":
       mbox.showerror('ERRO','Tcol is not specified!')
       return
    if rh =="":
       mbox.showerror('ERRO','RHO of Water is not specified!')
       return
    if g =="":
       mbox.showerror('ERRO','Gravity is not specified!')
       return
    #
    meshcal=open(dbpath,'w')
    meshcal.writelines('{:<20s}'.format(model)+"! modelname   "+'\n')
    meshcal.writelines('{:<20s}'.format(symmXOZ)+"! SYMM of XOZ   "+'\n')
    meshcal.writelines('{:<20s}'.format(loca)+"! location at XOY   "+'\n')
    meshcal.writelines('{:<20s}'.format(cg)+"! COG   "+'\n')
    meshcal.writelines('{:<20s}'.format(str(int(panels)))+"! panels   "+'\n')
    meshcal.writelines("1"+"\n")
    meshcal.writelines('{:<20s}'.format(tc)+"! TCOL water line move   "+'\n')
    meshcal.writelines('{:<20s}'.format(str(1))+"! for scale"+'\n')
    meshcal.writelines('{:<20s}'.format(rh)+"! rho of water  "+'\n')
    meshcal.writelines('{:<20s}'.format(g)+"! gravity   "+'\n')
    meshcal.close()
    #
    mbox.showinfo('NOTE','Mesh.cal Established')
    #
    # run mesh
    #
    filepath = os.getcwd()+"/db/" +db
    batchpath = os.getcwd()+"/db/" +db+"/run_mesh.bat"
    meshpath = os.getcwd()+"/bin/mesh.exe"
    file=open(batchpath,'w')
    file.writelines("cd " + filepath+'\n')
    file.writelines(meshpath + '\n')
    file.close()
    #
    meshfolder=filepath+"/mesh"
    if not os.path.exists(meshfolder):
        os.mkdir(meshfolder)
    else:
        mbox.showwarning('Warning','Folder exist, it will be replaced.')
        shutil.rmtree(meshfolder)
        os.mkdir(meshfolder)
    #
    shutil.copy(os.getcwd()+"/db/" +db+"/"+model,meshfolder+"/"+model)
    #
    #
    batchpath=os.getcwd()+"/db/" +db+"/run_mesh.bat"
    p=subprocess.Popen("cmd.exe /c" + batchpath,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curline=p.stdout.readline()
    logpath=os.getcwd()+"/db/" +db+"/logmesh.txt"
    logfile=open(logpath,'w')
    logfile.writelines("Start at :"+time.asctime()+'\n')
    while curline!=b'':
        curline=p.stdout.readline()
        if len(curline)<=2:
            pass
        else:
            log=str(curline)
            log=log[4:-5]
            logfile.writelines(log+'\n')
            print(log)
    logfile.writelines("Finish at :" +time.asctime()+'\n')
    logfile.close()
    p.wait()
    if p.poll()==0:
        print ('Success')
        mbox.showinfo('NOTE','Mesh run finish.')
    else:
        print ('failed')
        mbox.showerror('ERROR','Mesh run failed,chech logmesh file.')
    #
    #
#
def update_hydrosum():
    db=modname.get()
    p=rho.get()
    g=gravity.get()
    file=open(os.getcwd()+"/db/" +db+"/mesh/"+"Hydrostatics.dat",'r')
    line=file.readline()
    xf=line[5:13]
    xg=line[20:28]
    line=file.readline()
    yf=line[5:13]
    yg=line[20:28]
    line=file.readline()
    zf=line[5:13]
    zg=line[20:28]
    line=file.readline()
    disp=line[15:]
    line=file.readline()
    WPA=line[18:]
    file.close()
    #  Inertia
    file=open(os.getcwd()+"/db/" +db+"/mesh/"+"Inertia_hull.dat",'r')
    Ix=file.readline()
    Iy=file.readline()
    Iz=file.readline()
    file.close()
    # still water stiffness
    file=open(os.getcwd()+"/db/" +db+"/mesh/"+"KH.dat",'r')
    file.readline()
    file.readline()
    line=file.readline()
    Kz=line[30:75]
    line=file.readline()
    Krx=line[30:75]
    line=file.readline()
    Kry=line[30:75]
    file.close()
    #  write to summary file
    sumfile=open(os.getcwd()+"/db/" +db+"/summary_hydrosta.txt",'w')
    sumfile.writelines("*-----------------------------------------"+'\n')
    sumfile.writelines("*   WARP Demo -- Based on Nemoh        "+'\n')
    sumfile.writelines("*   Programmed by Wei Gao                 "+'\n')
    sumfile.writelines("*-----------------------------------------"+'\n')
    sumfile.writelines("2.Hydrostatic Summary"+'\n')
    sumfile.writelines("2.1 Basic Floating"+'\n')
    sumfile.writelines("   XB m = " + xf +";  XG m = " + xg +'\n')
    sumfile.writelines("   YB m = " + yf +";  YG m = " + yg +'\n')
    sumfile.writelines("   ZB m = " + zf +";  ZG m = " + zg +'\n')
    # 基本稳性
    #
    g=gravity.get()
    GMX=round(float(Krx[15:30])/float(g)/float(disp)/float(p),2)
    GMY=round(float(Kry[30:45])/float(g)/float(disp)/float(p),2)
    sumfile.writelines("   GMX m  :" + str(GMX) +'\n')
    sumfile.writelines("   GMY m  :" + str(GMY) +'\n')
    #
    sumfile.writelines("2.2 Hull inertia based on input model"+'\n')
    sumfile.writelines("   Displacement     m3:  " + disp)
    sumfile.writelines("   Water plane area m2:  " + WPA)
    sumfile.writelines("   IX kgm2: " + Ix)
    sumfile.writelines("   IY kgm2: " + Iy)
    sumfile.writelines("   IZ kgm2: " + Iz)
    sumfile.writelines("2.3 Still water stiffness"+'\n')
    sumfile.writelines("    Z     N : " + Kz +'\n')
    sumfile.writelines("   RX  N/rad: " + Krx +'\n')
    sumfile.writelines("   RY  N/rad: " + Kry +'\n')
    #
    mbox.showinfo('NOTE','Summary file updated.')
#
# tab2 gui
#
monty2 = ttk.LabelFrame(tab2, text = "Hydrostatic set")
monty2.grid(column = 0, row = 0, padx = 8, pady = 4)
ttk.Label(monty2, text="Symm about XOZ").grid(column=0, row=1,sticky='W')
XOZ = tk.StringVar()
XOZEntered = ttk.Entry(monty2, width=12, textvariable=XOZ)
XOZEntered.grid(column=0, row=2)
Tips.createToolTip(XOZEntered,'0 means no;1 means yes')
ttk.Label(monty2, text="Wateplane location X Y").grid(column=0, row=4,sticky='W')
bodyXOY = tk.StringVar()
bodyXOYEntered = ttk.Entry(monty2, width=12, textvariable=bodyXOY)
bodyXOYEntered.grid(column=0, row=5)
Tips.createToolTip(bodyXOYEntered,'Location of water plane origin X,Y')
ttk.Label(monty2, text="COG location X Y Z").grid(column=0, row=6,sticky='W')
bodyCOG = tk.StringVar()
bodyCOGEntered = ttk.Entry(monty2, width=12, textvariable=bodyCOG)
bodyCOGEntered.grid(column=0, row=7)
#
#
monty3 = ttk.LabelFrame(tab2, text = "Hydrostatic set")
monty3.grid(column = 8, row = 0, padx = 8, pady = 4)
ttk.Label(monty3, text="Tcol Water Line Move").grid(column=2, row=1,sticky='W')
tcol = tk.StringVar()
tcolEntered = ttk.Entry(monty3, width=12, textvariable=tcol)
tcolEntered.grid(column=2, row=2)
Tips.createToolTip(tcolEntered,'Draft level movement at Z direction')
ttk.Label(monty3, text="RHO of water kg").grid(column=2, row=3,sticky='W')
rho = tk.StringVar()
rhoEntered = ttk.Entry(monty3, width=12, textvariable=rho)
rhoEntered.grid(column=2, row=4)
ttk.Label(monty3, text="Gravity  m/s2").grid(column=2, row=5,sticky='W')
gravity = tk.StringVar()
gravityEntered = ttk.Entry(monty3, width=12, textvariable=gravity)
gravityEntered.grid(column=2, row=6)
#
monty21 = ttk.LabelFrame(tab2, text = "Note:")
monty21.grid(column = 10, row = 0, padx = 8, pady = 4,sticky='NW')
notetab2= "Hydrostatic calculate "
ttk.Label(monty21, text=notetab2).grid(column=0, row=0,sticky='W')
#
notetab2= "  "
ttk.Label(monty21, text=notetab2).grid(column=0, row=1,sticky='N')
run_mesh = ttk.Button(monty21, text="Run",command = runmesh)
run_mesh.grid(column= 0, row=2,sticky='N')
#
notetab2= "  "
ttk.Label(monty21, text=notetab2).grid(column=0, row=3,sticky='W')
updateHm = ttk.Button(monty21, text="Summary",command = update_hydrosum)
updateHm.grid(column= 0, row=4,sticky='N')
#
notetab2= "  "
ttk.Label(monty21, text=notetab2).grid(column=0, row=5,sticky='N')
#
#   tab3 input for RAO cal
#
def save_data_rao():
    db = modname.get()
    if os.path.exists(os.getcwd()+"/db/" +db+"/Mechanics"):
        shutil.rmtree(os.getcwd()+"/db/" +db+"/Mechanics")
        os.mkdir(os.getcwd()+"/db/" +db+"/Mechanics")
    else:
        os.mkdir(os.getcwd()+"/db/" +db+"/Mechanics")
    #
    #  innertia.dat
    #
    mass1 = mass.get()
    if mass1 =="":
        mbox.showerror('ERRO','Mass not specified!')
        return
    mass1 = float(mass1)
    #
    Ixx1 = Ixx.get()
    if Ixx1 =="":
        mbox.showerror('ERRO','Ixx not specified!')
        return
    Ixx1 = float(Ixx1)
    #
    Ixy1 = Ixy.get()
    if Ixy1 =="":
        Ixy1 = 0
    Ixy1 = float(Ixy1)
    #
    Ixz1 = Ixz.get()
    if Ixz1 =="":
        Ixz1 = 0
    Ixz1 = float(Ixz1)
    #
    Iyy1 = Iyy.get() 
    if Iyy1 =="":
        mbox.showerror('ERRO','Iyy not specified!')
        return
    Iyy1 = float(Iyy1)
    #
    Iyz1 = Iyz.get()
    if Iyz1 =="":
        Iyz1 = 0
    Iyz1 = float(Iyz1)
    #
    Izz1 = Izz.get()
    if Izz1 =="":
        mbox.showerror('ERRO','Izz not specified!')
        return
    Izz1 = float(Izz1)
    #
    mass_matrix = np.zeros((6,6))
    mass_matrix[0,0] = mass1
    mass_matrix[1,1] = mass1
    mass_matrix[2,2] = mass1
    mass_matrix[3,3] = Ixx1
    mass_matrix[3,4] = Ixy1
    mass_matrix[3,5] = Ixz1
    mass_matrix[4,4] = Iyy1
    mass_matrix[4,5] = Iyz1
    mass_matrix[5,5] = Izz1
    #
    massfile=open(os.getcwd()+"/db/" +db+'/Mechanics'+'/Inertia.dat','w')
    for i in range(6): 
        temp = ""
        for j in range(6): 
            temp1 = str(format(mass_matrix[i,j],'.7E'))
            temp = temp + ('{:<16s}'.format(temp1))      
        massfile.writelines(temp + '\n')
    massfile.close()
    #
    #  badd.dat   damping added
    #
    dadd_matrix = np.zeros((6,6))
    D111 = D11.get()
    if D111 =="":
        D111 = 0
    dadd_matrix[0,0] = float(D111)
    #
    D121 = D12.get()
    if D121 =="":
        D121 = 0
    dadd_matrix[0,1] = float(D121)
    #
    D131 = D13.get()
    if D131 =="":
        D131 = 0
    dadd_matrix[0,2] = float(D131)
    #
    D141 = D14.get()
    if D141 =="":
        D141 = 0
    dadd_matrix[0,3] = float(D141)
    #
    D151 = D15.get()
    if D151 =="":
        D151 = 0
    dadd_matrix[0,4] = float(D151)  
    #
    D161 = D16.get()
    if D161 =="":
        D161 = 0
    dadd_matrix[0,5] = float(D161)  
    #
    D211 = D21.get()
    if D211 =="":
        D211 = 0
    dadd_matrix[1,0] = float(D211)
    #
    D221 = D22.get()
    if D221 =="":
        D221 = 0
    dadd_matrix[1,1] = float(D221)
    #
    D231 = D23.get()
    if D231 =="":
        D231 = 0
    dadd_matrix[1,2] = float(D231)
    #
    D241 = D24.get()
    if D241 =="":
        D241 = 0
    dadd_matrix[1,3] = float(D241)
    #
    D251 = D25.get()
    if D251 =="":
        D251 = 0
    dadd_matrix[1,4] = float(D251)  
    #
    D261 = D26.get()
    if D261 =="":
        D261 = 0
    dadd_matrix[1,5] = float(D261) 
    #
    #
    #
    D311 = D31.get()
    if D311 =="":
        D311 = 0
    dadd_matrix[2,0] = float(D311)
    #
    D321 = D32.get()
    if D321 =="":
        D321 = 0
    dadd_matrix[2,1] = float(D321)
    #
    D331 = D33.get()
    if D331 =="":
        D331 = 0
    dadd_matrix[2,2] = float(D331)
    #
    D341 = D34.get()
    if D341 =="":
        D341 = 0
    dadd_matrix[2,3] = float(D341)
    #
    D351 = D35.get()
    if D351 =="":
        D351 = 0
    dadd_matrix[2,4] = float(D351)  
    #
    D361 = D36.get()
    if D361 =="":
        D361 = 0
    dadd_matrix[2,5] = float(D361)  
    #
    #
    D411 = D41.get()
    if D411 =="":
        D411 = 0
    dadd_matrix[3,0] = float(D411)
    #
    D421 = D42.get()
    if D421 =="":
        D421 = 0
    dadd_matrix[3,1] = float(D421)
    #
    D431 = D43.get()
    if D431 =="":
        D431 = 0
    dadd_matrix[3,2] = float(D431)
    #
    D441 = D44.get()
    if D441 =="":
        D441 = 0
    dadd_matrix[3,3] = float(D441)
    #
    D451 = D45.get()
    if D451 =="":
        D451 = 0
    dadd_matrix[3,4] = float(D451)  
    #
    D461 = D46.get()
    if D461 =="":
        D461 = 0
    dadd_matrix[3,5] = float(D461) 
    #
    #
    D511 = D51.get()
    if D511 =="":
        D511 = 0
    dadd_matrix[4,0] = float(D511)
    #
    D521 = D52.get()
    if D521 =="":
        D521 = 0
    dadd_matrix[4,1] = float(D521)
    #
    D531 = D53.get()
    if D531 =="":
        D531 = 0
    dadd_matrix[4,2] = float(D531)
    #
    D541 = D54.get()
    if D541 =="":
        D541 = 0
    dadd_matrix[4,3] = float(D541)
    #
    D551 = D55.get()
    if D551 =="":
        D551 = 0
    dadd_matrix[4,4] = float(D551)  
    #
    D561 = D56.get()
    if D561 =="":
        D561 = 0
    dadd_matrix[4,5] = float(D561) 
    #
    #
    D611 = D61.get()
    if D611 =="":
        D611 = 0
    dadd_matrix[5,0] = float(D611)
    #
    D621 = D62.get()
    if D621 =="":
        D621 = 0
    dadd_matrix[5,1] = float(D621)
    #
    D631 = D63.get()
    if D631 =="":
        D631 = 0
    dadd_matrix[5,2] = float(D631)
    #
    D641 = D64.get()
    if D641 =="":
        D641 = 0
    dadd_matrix[5,3] = float(D641)
    #
    D651 = D65.get()
    if D651 =="":
        D651 = 0
    dadd_matrix[5,4] = float(D651)  
    #
    D661 = D66.get()
    if D661 =="":
        D661 = 0
    dadd_matrix[5,5] = float(D661)     
    #
    #  Km.dat   stiffness added
    #
    kmadd_matrix = np.zeros((6,6))
    S111 = S11.get()
    if S111 =="":
        S111 = 0
    kmadd_matrix[0,0] = float(S111)
    #
    S121 = S12.get()
    if S121 =="":
        S121 = 0
    kmadd_matrix[0,1] = float(S121)
    #
    S131 = S13.get()
    if S131 =="":
        S131 = 0
    kmadd_matrix[0,2] = float(S131)
    #
    S141 = S14.get()
    if S141 =="":
        S141 = 0
    kmadd_matrix[0,3] = float(S141)
    #
    S151 = S15.get()
    if S151 =="":
        S151 = 0
    kmadd_matrix[0,4] = float(S151)  
    #
    S161 = S16.get()
    if S161 =="":
        S161 = 0
    kmadd_matrix[0,5] = float(S161)  
    #
    S211 = S21.get()
    if S211 =="":
        S211 = 0
    kmadd_matrix[1,0] = float(S211)
    #
    S221 = S22.get()
    if S221 =="":
        S221 = 0
    kmadd_matrix[1,1] = float(S221)
    #
    S231 = S23.get()
    if S231 =="":
        S231 = 0
    kmadd_matrix[1,2] = float(S231)
    #
    S241 = S24.get()
    if S241 =="":
        S241 = 0
    kmadd_matrix[1,3] = float(S241)
    #
    S251 = S25.get()
    if S251 =="":
        S251 = 0
    kmadd_matrix[1,4] = float(S251)  
    #
    S261 = S26.get()
    if S261 =="":
        S261 = 0
    kmadd_matrix[1,5] = float(S261) 
    #
    #
    #
    S311 = S31.get()
    if S311 =="":
        S311 = 0
    kmadd_matrix[2,0] = float(S311)
    #
    S321 = S32.get()
    if S321 =="":
        S321 = 0
    kmadd_matrix[2,1] = float(S321)
    #
    S331 = S33.get()
    if S331 =="":
        S331 = 0
    kmadd_matrix[2,2] = float(S331)
    #
    S341 = S34.get()
    if S341 =="":
        S341 = 0
    kmadd_matrix[2,3] = float(S341)
    #
    S351 = S35.get()
    if S351 =="":
        S351 = 0
    kmadd_matrix[2,4] = float(S351)  
    #
    S361 = S36.get()
    if S361 =="":
        S361 = 0
    kmadd_matrix[2,5] = float(S361)  
    #
    #
    S411 = S41.get()
    if S411 =="":
        S411 = 0
    kmadd_matrix[3,0] = float(S411)
    #
    S421 = S42.get()
    if S421 =="":
        S421 = 0
    kmadd_matrix[3,1] = float(S421)
    #
    S431 = S43.get()
    if S431 =="":
        S431 = 0
    kmadd_matrix[3,2] = float(S431)
    #
    S441 = S44.get()
    if S441 =="":
        S441 = 0
    kmadd_matrix[3,3] = float(S441)
    #
    S451 = S45.get()
    if S451 =="":
        S451 = 0
    kmadd_matrix[3,4] = float(S451)  
    #
    S461 = S46.get()
    if S461 =="":
        S461 = 0
    kmadd_matrix[3,5] = float(S461) 
    #
    #
    S511 = S51.get()
    if S511 =="":
        S511 = 0
    kmadd_matrix[4,0] = float(S511)
    #
    S521 = S52.get()
    if S521 =="":
        S521 = 0
    kmadd_matrix[4,1] = float(S521)
    #
    S531 = S53.get()
    if S531 =="":
        S531 = 0
    kmadd_matrix[4,2] = float(S531)
    #
    S541 = S54.get()
    if S541 =="":
        S541 = 0
    kmadd_matrix[4,3] = float(S541)
    #
    S551 = S55.get()
    if S551 =="":
        S551 = 0
    kmadd_matrix[4,4] = float(S551)  
    #
    S561 = S56.get()
    if S561 =="":
        S561 = 0
    kmadd_matrix[4,5] = float(S561) 
    #
    #
    S611 = S61.get()
    if S611 =="":
        S611 = 0
    kmadd_matrix[5,0] = float(S611)
    #
    S621 = S62.get()
    if S621 =="":
        S621 = 0
    kmadd_matrix[5,1] = float(S621)
    #
    S631 = S63.get()
    if S631 =="":
        S631 = 0
    kmadd_matrix[5,2] = float(S631)
    #
    S641 = S64.get()
    if S641 =="":
        S641 = 0
    kmadd_matrix[5,3] = float(S641)
    #
    S651 = S65.get()
    if S651 =="":
        S651 = 0
    kmadd_matrix[5,4] = float(S651)  
    #
    S661 = S66.get()
    if S661 =="":
        S661 = 0
    kmadd_matrix[5,5] = float(S661) 
    #
    #
    daddfile=open(os.getcwd()+"/db/" +db+'/Mechanics'+'/badd.dat','w')
    for i in range(6): 
        temp = ""
        for j in range(6): 
            temp1 = str(format(dadd_matrix[i,j],'.7E'))
            temp = temp + ('{:<16s}'.format(temp1))      
        daddfile.writelines(temp + '\n')
    daddfile.close()
    #
    kmaddfile=open(os.getcwd()+"/db/" +db+'/Mechanics'+'/km.dat','w')
    for i in range(6): 
        temp = ""
        for j in range(6): 
            temp1 = str(format(kmadd_matrix[i,j],'.7E'))
            temp = temp + ('{:<16s}'.format(temp1))      
        kmaddfile.writelines(temp + '\n')
    kmaddfile.close()
    #
    #  Kh.dat   hydrostatic stiffness copy
    #
    if os.path.exists(os.getcwd()+"/db/" +db+"/mesh/kh.dat"):
        shutil.copy2(os.getcwd()+"/db/" +db+"/mesh/kh.dat",os.getcwd()+"/db/" +db+"/Mechanics")
    else:
        mbox.showerror('ERRO','Hydrostatic(mesh) not run!')
        return
    mbox.showinfo('NOTE','Mass, damping and stiffness data saved.')
#
#
#
monty6 = ttk.LabelFrame(tab3, text = "RAO Calculation Input")
monty6.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='NW')
#
monty61 = ttk.LabelFrame(monty6, text = "Mass")
monty61.grid(column = 0, row = 1, padx = 8, pady = 4,sticky='NW')
mass= tk.StringVar()
massTEntered = ttk.Entry(monty61, width=12, textvariable=mass)
massTEntered.grid(column=0, row=1)
#
monty62 = ttk.LabelFrame(monty6, text = "Inertia moment")
monty62.grid(column = 0, row = 2, padx = 8, pady = 4,sticky='NW')
Ixx= tk.StringVar()
IxxTEntered = ttk.Entry(monty62, width=12, textvariable=Ixx)
IxxTEntered.grid(column=0, row=4)
Ixy= tk.StringVar()
IxyTEntered = ttk.Entry(monty62, width=12, textvariable=Ixy)
IxyTEntered.grid(column=1, row=4)
Ixz= tk.StringVar()
IxzTEntered = ttk.Entry(monty62, width=12, textvariable=Ixz)
IxzTEntered.grid(column=2, row=4)
Iyy= tk.StringVar()
IyyTEntered = ttk.Entry(monty62, width=12, textvariable=Iyy)
IyyTEntered.grid(column=1, row=5)
Iyz= tk.StringVar()
IyzTEntered = ttk.Entry(monty62, width=12, textvariable=Iyz)
IyzTEntered.grid(column=2, row=5)
Izz= tk.StringVar()
IzzTEntered = ttk.Entry(monty62, width=12, textvariable=Izz)
IzzTEntered.grid(column=2, row=6)
#
#
#
monty63 = ttk.LabelFrame(monty6, text = "Damping Added")
monty63.grid(column = 0, row = 3, padx = 8, pady = 4,sticky='NW')
D11= tk.StringVar()
D11_Entered = ttk.Entry(monty63, width=12, textvariable=D11)
D11_Entered.grid(column=0, row=9,sticky='W')
D12 = tk.StringVar()
D12_Entered = ttk.Entry(monty63, width=12, textvariable=D12)
D12_Entered.grid(column=1, row=9,sticky='W')
D13 = tk.StringVar()
D13_Entered = ttk.Entry(monty63, width=12, textvariable=D13)
D13_Entered.grid(column=2, row=9,sticky='W')
D14 = tk.StringVar()
D14_Entered = ttk.Entry(monty63, width=12, textvariable=D14)
D14_Entered.grid(column=3, row=9,sticky='W')
D15 = tk.StringVar()
D15_Entered = ttk.Entry(monty63, width=12, textvariable=D15)
D15_Entered.grid(column=4, row=9,sticky='W')
D16 = tk.StringVar()
D16_Entered = ttk.Entry(monty63, width=12, textvariable=D16)
D16_Entered.grid(column=5, row=9,sticky='W')
#
D21= tk.StringVar()
D21_Entered = ttk.Entry(monty63, width=12, textvariable=D21)
D21_Entered.grid(column=0, row=10,sticky='W')
D22 = tk.StringVar()
D22_Entered = ttk.Entry(monty63, width=12, textvariable=D22)
D22_Entered.grid(column=1, row=10,sticky='W')
D23 = tk.StringVar()
D23_Entered = ttk.Entry(monty63, width=12, textvariable=D23)
D23_Entered.grid(column=2, row=10,sticky='W')
D24 = tk.StringVar()
D24_Entered = ttk.Entry(monty63, width=12, textvariable=D24)
D24_Entered.grid(column=3, row=10,sticky='W')
D25 = tk.StringVar()
D25_Entered = ttk.Entry(monty63, width=12, textvariable=D25)
D25_Entered.grid(column=4, row=10,sticky='W')
D26 = tk.StringVar()
D26_Entered = ttk.Entry(monty63, width=12, textvariable=D26)
D26_Entered.grid(column=5, row=10,sticky='W')
#
D31= tk.StringVar()
D31_Entered = ttk.Entry(monty63, width=12, textvariable=D31)
D31_Entered.grid(column=0, row=11,sticky='W')
D32 = tk.StringVar()
D32_Entered = ttk.Entry(monty63, width=12, textvariable=D32)
D32_Entered.grid(column=1, row=11,sticky='W')
D33 = tk.StringVar()
D33_Entered = ttk.Entry(monty63, width=12, textvariable=D33)
D33_Entered.grid(column=2, row=11,sticky='W')
D34 = tk.StringVar()
D34_Entered = ttk.Entry(monty63, width=12, textvariable=D34)
D34_Entered.grid(column=3, row=11,sticky='W')
D35 = tk.StringVar()
D35_Entered = ttk.Entry(monty63, width=12, textvariable=D35)
D35_Entered.grid(column=4, row=11,sticky='W')
D36 = tk.StringVar()
D36_Entered = ttk.Entry(monty63, width=12, textvariable=D36)
D36_Entered.grid(column=5, row=11,sticky='W')
#
D41= tk.StringVar()
D41_Entered = ttk.Entry(monty63, width=12, textvariable=D41)
D41_Entered.grid(column=0, row=12,sticky='W')
D42 = tk.StringVar()
D42_Entered = ttk.Entry(monty63, width=12, textvariable=D42)
D42_Entered.grid(column=1, row=12,sticky='W')
D43 = tk.StringVar()
D43_Entered = ttk.Entry(monty63, width=12, textvariable=D43)
D43_Entered.grid(column=2, row=12,sticky='W')
D44 = tk.StringVar()
D44_Entered = ttk.Entry(monty63, width=12, textvariable=D44)
D44_Entered.grid(column=3, row=12,sticky='W')
D45 = tk.StringVar()
D45_Entered = ttk.Entry(monty63, width=12, textvariable=D45)
D45_Entered.grid(column=4, row=12,sticky='W')
D46 = tk.StringVar()
D46_Entered = ttk.Entry(monty63, width=12, textvariable=D46)
D46_Entered.grid(column=5, row=12,sticky='W')
#
D51= tk.StringVar()
D51_Entered = ttk.Entry(monty63, width=12, textvariable=D51)
D51_Entered.grid(column=0, row=13,sticky='W')
D52 = tk.StringVar()
D52_Entered = ttk.Entry(monty63, width=12, textvariable=D52)
D52_Entered.grid(column=1, row=13,sticky='W')
D53 = tk.StringVar()
D53_Entered = ttk.Entry(monty63, width=12, textvariable=D53)
D53_Entered.grid(column=2, row=13,sticky='W')
D54 = tk.StringVar()
D54_Entered = ttk.Entry(monty63, width=12, textvariable=D54)
D54_Entered.grid(column=3, row=13,sticky='W')
D55 = tk.StringVar()
D55_Entered = ttk.Entry(monty63, width=12, textvariable=D55)
D55_Entered.grid(column=4, row=13,sticky='W')
D56 = tk.StringVar()
D56_Entered = ttk.Entry(monty63, width=12, textvariable=D56)
D56_Entered.grid(column=5, row=13,sticky='W')
#
D61= tk.StringVar()
D61_Entered = ttk.Entry(monty63, width=12, textvariable=D61)
D61_Entered.grid(column=0, row=14,sticky='W')
D62 = tk.StringVar()
D62_Entered = ttk.Entry(monty63, width=12, textvariable=D62)
D62_Entered.grid(column=1, row=14,sticky='W')
D63 = tk.StringVar()
D63_Entered = ttk.Entry(monty63, width=12, textvariable=D63)
D63_Entered.grid(column=2, row=14,sticky='W')
D64 = tk.StringVar()
D64_Entered = ttk.Entry(monty63, width=12, textvariable=D64)
D64_Entered.grid(column=3, row=14,sticky='W')
D65 = tk.StringVar()
D65_Entered = ttk.Entry(monty63, width=12, textvariable=D65)
D65_Entered.grid(column=4, row=14,sticky='W')
D66 = tk.StringVar()
D66_Entered = ttk.Entry(monty63, width=12, textvariable=D66)
D66_Entered.grid(column=5, row=14,sticky='W')
#
#
monty64 = ttk.LabelFrame(monty6, text = "Stiffness Added")
monty64.grid(column = 0, row = 4, padx = 8, pady = 4,sticky='NW')
S11= tk.StringVar()
S11TEntered = ttk.Entry(monty64, width=12, textvariable=S11)
S11TEntered.grid(column=0, row=16,sticky='W')
S12= tk.StringVar()
S12TEntered = ttk.Entry(monty64, width=12, textvariable=S12)
S12TEntered.grid(column=1, row=16,sticky='W')
S13= tk.StringVar()
S13TEntered = ttk.Entry(monty64, width=12, textvariable=S13)
S13TEntered.grid(column=2, row=16,sticky='W')
S14= tk.StringVar()
S14TEntered = ttk.Entry(monty64, width=12, textvariable=S14)
S14TEntered.grid(column=3, row=16,sticky='W')
S15= tk.StringVar()
S15TEntered = ttk.Entry(monty64, width=12, textvariable=S15)
S15TEntered.grid(column=4, row=16,sticky='W')
S16= tk.StringVar()
S16TEntered = ttk.Entry(monty64, width=12, textvariable=S16)
S16TEntered.grid(column=5, row=16,sticky='W')
#
S21= tk.StringVar()
S21TEntered = ttk.Entry(monty64, width=12, textvariable=S21)
S21TEntered.grid(column=0, row=17,sticky='W')
S22= tk.StringVar()
S22TEntered = ttk.Entry(monty64, width=12, textvariable=S22)
S22TEntered.grid(column=1, row=17,sticky='W')
S23= tk.StringVar()
S23TEntered = ttk.Entry(monty64, width=12, textvariable=S23)
S23TEntered.grid(column=2, row=17,sticky='W')
S24= tk.StringVar()
S24TEntered = ttk.Entry(monty64, width=12, textvariable=S24)
S24TEntered.grid(column=3, row=17,sticky='W')
S25= tk.StringVar()
S25TEntered = ttk.Entry(monty64, width=12, textvariable=S25)
S25TEntered.grid(column=4, row=17,sticky='W')
S26= tk.StringVar()
S26TEntered = ttk.Entry(monty64, width=12, textvariable=S26)
S26TEntered.grid(column=5, row=17,sticky='W')
#
S31= tk.StringVar()
S31TEntered = ttk.Entry(monty64, width=12, textvariable=S31)
S31TEntered.grid(column=0, row=18,sticky='W')
S32= tk.StringVar()
S32TEntered = ttk.Entry(monty64, width=12, textvariable=S32)
S32TEntered.grid(column=1, row=18,sticky='W')
S33= tk.StringVar()
S33TEntered = ttk.Entry(monty64, width=12, textvariable=S33)
S33TEntered.grid(column=2, row=18,sticky='W')
S34= tk.StringVar()
S34TEntered = ttk.Entry(monty64, width=12, textvariable=S34)
S34TEntered.grid(column=3, row=18,sticky='W')
S35= tk.StringVar()
S35TEntered = ttk.Entry(monty64, width=12, textvariable=S35)
S35TEntered.grid(column=4, row=18,sticky='W')
S36= tk.StringVar()
S36TEntered = ttk.Entry(monty64, width=12, textvariable=S36)
S36TEntered.grid(column=5, row=18,sticky='W')
#
S41= tk.StringVar()
S41TEntered = ttk.Entry(monty64, width=12, textvariable=S41)
S41TEntered.grid(column=0, row=19,sticky='W')
S42= tk.StringVar()
S42TEntered = ttk.Entry(monty64, width=12, textvariable=S42)
S42TEntered.grid(column=1, row=19,sticky='W')
S43= tk.StringVar()
S43TEntered = ttk.Entry(monty64, width=12, textvariable=S43)
S43TEntered.grid(column=2, row=19,sticky='W')
S44= tk.StringVar()
S44TEntered = ttk.Entry(monty64, width=12, textvariable=S44)
S44TEntered.grid(column=3, row=19,sticky='W')
S45= tk.StringVar()
S45TEntered = ttk.Entry(monty64, width=12, textvariable=S45)
S45TEntered.grid(column=4, row=19,sticky='W')
S46= tk.StringVar()
S46TEntered = ttk.Entry(monty64, width=12, textvariable=S46)
S46TEntered.grid(column=5, row=19,sticky='W')
#
S51= tk.StringVar()
S51TEntered = ttk.Entry(monty64, width=12, textvariable=S51)
S51TEntered.grid(column=0, row=20,sticky='W')
S52= tk.StringVar()
S52TEntered = ttk.Entry(monty64, width=12, textvariable=S52)
S52TEntered.grid(column=1, row=20,sticky='W')
S53= tk.StringVar()
S53TEntered = ttk.Entry(monty64, width=12, textvariable=S53)
S53TEntered.grid(column=2, row=20,sticky='W')
S54= tk.StringVar()
S54TEntered = ttk.Entry(monty64, width=12, textvariable=S54)
S54TEntered.grid(column=3, row=20,sticky='W')
S55= tk.StringVar()
S55TEntered = ttk.Entry(monty64, width=12, textvariable=S55)
S55TEntered.grid(column=4, row=20,sticky='W')
S56= tk.StringVar()
S56TEntered = ttk.Entry(monty64, width=12, textvariable=S56)
S56TEntered.grid(column=5, row=20,sticky='W')
#
S61= tk.StringVar()
S61TEntered = ttk.Entry(monty64, width=12, textvariable=S61)
S61TEntered.grid(column=0, row=21,sticky='W')
S62= tk.StringVar()
S62TEntered = ttk.Entry(monty64, width=12, textvariable=S62)
S62TEntered.grid(column=1, row=21,sticky='W')
S63= tk.StringVar()
S63TEntered = ttk.Entry(monty64, width=12, textvariable=S63)
S63TEntered.grid(column=2, row=21,sticky='W')
S64= tk.StringVar()
S64TEntered = ttk.Entry(monty64, width=12, textvariable=S64)
S64TEntered.grid(column=3, row=21,sticky='W')
S65= tk.StringVar()
S65TEntered = ttk.Entry(monty64, width=12, textvariable=S65)
S65TEntered.grid(column=4, row=21,sticky='W')
S66= tk.StringVar()
S66TEntered = ttk.Entry(monty64, width=12, textvariable=S66)
S66TEntered.grid(column=5, row=21,sticky='W')
#
ttk.Label(monty6, text="     ").grid(column=0, row=22,sticky='NW')
makerao = ttk.Button(monty6, text="Save",command = save_data_rao)
makerao.grid(column= 2, row=23,sticky="N")
#
#-----------------------------------------------------------------------------------------------
#
# tab4  set cal file
# command click -- prepare
#----------------------
def addmpoints():
    temp=wmp.get()
    if temp =="" :
        mbox.showinfo('NOTE','No wave measurement point')
        return
    else:
        wmpoints.append(temp)
        ttk.Label(monty41, text="Points is:").grid(column=0, row=9,sticky='w')
    i=10
    for wmpoint in wmpoints:
        ttk.Label(monty41, text=wmpoint).grid(column=0, row=i,sticky='w')
        i=i+1
        print(wmpoint)
#
def savecal():
    db=modname.get()
    if db=="":
        mbox.showerror("Error","Modelname missed")
        return
    p=rho.get()
    if p=="":
        mbox.showerror("Error","RHO of water missed")
        return
    g=gravity.get()
    if g=="":
        mbox.showerror("Error","Grivity missed")
        return
    wdn=wd.get()
    if wdn=="":
        mbox.showerror("Error","Waterdepth missed")
        return
    numb=nb.get()
    modelname=modname.get()
    #----------------------------------
    file=open(os.getcwd()+"/db/" +db+"/Summary_hydrosta.txt",'r')
    temps=[1,2,3,4,5,6]
    for temp in temps:
        file.readline()
    #
    line=file.readline()
    xg=line[28:36]
    line=file.readline()
    yg=line[28:36]
    line=file.readline()
    zg=line[28:36]
    cdgxyz=  '{:>10s}'.format(xg)+'{:>10s}'.format(yg)+'{:>10s}'.format("0.000")
    cdgrxyz= '{:>10s}'.format(xg)+'{:>10s}'.format(yg)+'{:>10s}'.format(zg)
    #
    freqts=freqt.get()
    if freqt=="":
        mbox.showerror("Error","Freq type. missed")
        return
    minwf=minw.get()
    if minwf=="":
        mbox.showerror("Error","Min wave freq. missed")
        return
    maxwf=maxw.get()
    if maxwf=="":
        mbox.showerror("Error","Max wave freq. missed")
        return
    numwf=numw.get()
    if numwf=="":
        mbox.showerror("Error","Numbers of wave freq. missed")
        return
    minwds=minwd.get()
    if minwds=="":
        mbox.showerror("Error","Min wave direction missed")
        return
    maxwds=maxwd.get()
    if maxwds=="":
        mbox.showerror("Error","Max wave direction missed")
        return
    numwds=numwd.get()
    if numwds=="":
        mbox.showerror("Error","Numbers of wave direction missed")
        return
    irfs=irf.get()

    if str(shpre.get())=='1':
        shpre1=1
    else:
        shpre1=0
    #
    kochins=Koch.get()
    freess=Frees.get()
    raoss=raos.get()
    #
    if raoss == 1: 
        if os.path.exists(os.getcwd()+"/db/" +db+"/motion"):
            shutil.rmtree(os.getcwd()+"/db/" +db+"/motion")
            os.mkdir(os.getcwd()+"/db/" +db+"/motion")
        else:
            os.mkdir(os.getcwd()+"/db/" +db+"/motion")
    #
    freq_ts=freq_t.get()
    #
    # qtf post
    #
    qtfs = qtf.get()
    qtffs = qtff.get()
    qtfds = qtfd.get()
    qtfcs = qtfc.get()
    fsmfs = fsmf.get()
    fsmf_qtfs = fsmf_qtf.get()
    hys_terms = hys_term.get()
    freq_qtfts = freq_qtft.get()
    dukos = duko.get()
    HASBOs = HASBO.get()
    HASFS_ASYMPs = HASFS_ASYMP.get()
    #
    file=open(os.getcwd()+"/db/" +modelname+"/summary_model.txt","r")
    line=file.readline()
    while line:
        line=file.readline()
        if line[0:30]=="  Total model panel number is:" :
            panels=int(line[31:35])
        elif line[0:30]=="  Total model node number is :":
            nodes=int(line[31:35])
    file.close()
    file=open(os.getcwd()+"/db/" +modelname+"/Nemoh.cal","w")
    file.writelines("--- Environment----"+'\n')
    file.writelines('{:<20s}'.format(p) +"! Fluid density kg/m**3 "+'\n')
    file.writelines('{:<20s}'.format(g) +"! Gravity       m/s**2 "+'\n')
    file.writelines('{:<20s}'.format(wdn)+"! Water depth   m     "+'\n')
    if len(wmpoints)!=0:
        for wmpoint in wmpoints:
            file.writelines('{:<20s}'.format(wmpoint) + "! XEFF YEFF, Wave measurement point m"+'\n')
    else:
        file.writelines( '{:<20s}'.format('0  0')+"! XEFF YEFF, Wave measurement point m"+'\n')
    file.writelines("--- Description of floating bodies ------"+'\n')
    file.writelines('{:<20s}'.format(numb)+"! Number of bodies"+'\n')
    file.writelines("--- Body 1 ---------------"+'\n')
    file.writelines('{:<20s}'.format(modelname+'.dat') +"! Name of mesh file" +'\n')
    file.writelines('{:<20s}'.format(str(nodes)+" " +str(panels))+"! Number of points and number of panels"+'\n')
    #
    i=0
    temp=[0]*6
    #
    if Dsurge.get()==1:
        temp[0]="1  0  0  "
        i=i+1
    else:
        temp[0]=" "
    if Dsway.get()==1:
        temp[1]="0  1  0  "
        i=i+1
    else:
        temp[1]=" "
    if Dheave.get()==1:
        temp[2]="0  0  1  "
        i=i+1
    else:
        temp[2]=" "
    if Droll.get()==1:
        temp[3]="1  0  0  "
        i=i+1
    else:
        temp[3]=" "
    if Dpitch.get()==1:
        temp[4]="0  1  0  "
        i=i+1
    else:
        temp[4]=" "
    if Dyaw.get()==1:
        temp[5]="0  0  1  "
        i=i+1
    else:
        temp[5]=" "
    #
    deg=i
    #
    file.writelines(str(deg) +"                 ! Number of degrees of freedom"+'\n')
    for i in range(6):
        if temp[i] ==" ":
            pass
        else:
            if i<3:
                file.writelines ("1" + "  " + temp[i] + "  " + cdgxyz + "   ! degree "+str(i+1)+'\n') #// cog
            else:
                file.writelines ("2" + "  " + temp[i] + "  " + cdgrxyz + "   ! degree "+str(i+1)+'\n') #// cog

    #
    file.writelines(str(deg) + "                 ! Number of degrees of freedom"+'\n')
    #
    for i in range(6):
        if temp[i] ==" ":
            pass
        else:
            if i<=2:
                file.writelines ("1" + "  " + temp[i] + "  " + cdgxyz + "   ! force "+str(i+1)+'\n') #// cog
            else:
                file.writelines ("2" + "  " + temp[i] + "  " + cdgrxyz + "   ! force "+str(i+1)+'\n') #// cog
    #
    file.writelines ('{:<20s}'.format(str("0"))+"! Number of lines of additional information"+'\n')
    file.writelines ("--- Load cases to be solved ---------"+'\n')
    file.writelines (str(freqts)+" "+str(numwf) +" "+str(minwf) +" "+str(maxwf) + "! Freq type 1,2,3=[rad/s,Hz,s], \
                                                             Number of wave frequencies/periods, Min, and Max"+'\n')
    file.writelines (str(numwds)+" "+str(minwds)+" "+str(maxwds)+"! Number of wave directions, Min and Max (degrees)" +'\n')
    file.writelines("--- Post processing -------"+'\n')
    if irfs=="":
        mbox.showinfo("NOTE","No IDRS.")
        file.writelines ('{:<20s}'.format('0  0   0  ')+"! IRF calculation (0 for no calculation), time step and duration"+'\n')
    else:
        file.writelines ('{:<20s}'.format(str(irfs))+ "! IRF calculation (0 for no calculation), time step and duration"+'\n')
    #
    if shpre1==0:
        file.writelines ('{:<20s}'.format('0 ') + "! Show pressure"+'\n')
        mbox.showinfo("NOTE","No Pressure.")
    else:
        file.writelines ('{:<20s}'.format('1 ')+ "! Show pressure"+'\n')
    #
    if kochins=="":
        mbox.showinfo("NOTE","No KOCHINS.")
        file.writelines ('{:<20s}'.format('0 0 0 ') + "! Kochin function     " \
                                   " ! Number of directions of calculation" \
                                   "(0 for no calculations), Min and Max (degrees)"+'\n')
    else:
        file.writelines ('{:<20s}'.format(str(kochins)) + "! Kochin function       "\
                                  "! Number of directions of calculation "\
                                  "(0 for no calculations), Min and Max (degrees)"+'\n')
    #
    if freess=="":
        mbox.showinfo("NOTE","No Free surface elevation.")
        file.writelines ('{:<20s}'.format('0 0 0 0') + "! Free surface elevation" \
                        "! Number of points in x direction (0 for no calcutions)" \
                        "and y direction and dimensions of domain in x and y direction"+'\n')
    else:
        file.writelines ('{:<20s}'.format(str(freess)) + "! Free surface elevation" \
                        "! Number of points in x direction (0 for no calcutions)" \
                        "and y direction and dimensions of domain in x and y direction"+'\n')
    #
    if raoss==0:
        mbox.showinfo("NOTE","RAO not considered.")
        file.writelines ('{:<20s}'.format('0') + "! Response Amplitude Operator (RAO), 0 no calculation, 1 calculated"+'\n')
    else:
        file.writelines ('{:<20s}'.format(str(raoss)) + "! Response Amplitude Operator (RAO), 0 no calculation, 1 calculated"+'\n')       
    #
    if freq_ts=="":
        mbox.showinfo("NOTE","rad/s is used.")
        file.writelines ('{:<20s}'.format('1') + "! output freq type, 1,2,3=[rad/s,Hz,s]"+'\n')
    else:
        file.writelines ('{:<20s}'.format(str(freq_ts)) + "! output freq type, 1,2,3=[rad/s,Hz,s]"+'\n')       
            
    #
    file.writelines ("----- QTF--------------------" +'\n')
    
    #
    if qtfs==0:
        mbox.showinfo("NOTE","QTF not considered.")
        file.writelines ('{:<20s}'.format('0') + "! QTF flag, 1 is calculated" +'\n')
    else:
        file.writelines ('{:<20s}'.format(str(qtfs)) + "! QTF flag, 1 is calculated" +'\n')
    #
    if qtffs=="":
        if qtfs==0:
            file.writelines ('{:<20s}'.format('0 0 0') + "! Number of radial frequencies, Min, and Max values for the QTF computation" +'\n')
    else:
        file.writelines ('{:<20s}'.format(str(qtffs)) + "! Number of radial frequencies, Min, and Max values for the QTF computation" +'\n')
    #
    if qtfds=="":
        if qtfs==0:
            file.writelines ('{:<20s}'.format('0') + "! 0 Unidirection, Bidirection 1 " +'\n')
    else:
        file.writelines ('{:<20s}'.format(str(qtfds)) + "! 0 Unidirection, Bidirection 1 " +'\n')
    #
    if qtfcs=="":
        if qtfcs=="":
            file.writelines ('{:<20s}'.format('0') + "! Contrib, 1 DUOK, 2 DUOK+HASBO, 3 Full QTF (DUOK+HASBO+HASFS+ASYMP)" +'\n')
        else:
            mbox.showinfo("NOTE","QTF direction not set.")
    else:
        file.writelines ('{:<20s}'.format(str(qtfcs)) + "! Contrib, 1 DUOK, 2 DUOK+HASBO, 3 Full QTF (DUOK+HASBO+HASFS+ASYMP"+'\n')
    #
    if fsmfs=="":
        if fsmfs=="":
            file.writelines ('{:<20s}'.format('0') + "! Name of free surface meshfile (Only for Contrib 3), type 'NA' if not applicable" +'\n')
        else:
            mbox.showinfo("NOTE","fsmf not set.")
    else:
        file.writelines ('{:<20s}'.format(str(fsmfs)) + "! Name of free surface meshfile (Only for Contrib 3), type 'NA' if not applicable"+'\n')
    #
    if fsmf_qtfs=="":
        if fsmf_qtfs=="":
            file.writelines ('{:<20s}'.format('0') + "! Free surface QTF parameters: Re Nre NBessel (for Contrib 3)" +'\n')
        else:
            mbox.showinfo("NOTE","fsmf parameter not set.")
    else:
        file.writelines ('{:<20s}'.format(str(fsmf_qtfs)) + "! Free surface QTF parameters: Re Nre NBessel (for Contrib 3)"+'\n')
    #
    if hys_terms=="":
        if hys_terms=="":
            file.writelines ('{:<20s}'.format('0') + "! 1 Includes Hydrostatic terms of the quadratic first order motion, -[K]xi2_tilde" +'\n')
        else:
            mbox.showinfo("NOTE","Hydrostatic terms not set.")
    else:
        file.writelines ('{:<20s}'.format(str(hys_terms)) + "! 1 Includes Hydrostatic terms of the quadratic first order motion, -[K]xi2_tilde"+'\n') 
    #
    if freq_qtfts=="":
        if freq_qtfts=="":
            file.writelines ('{:<20s}'.format('0') + "! For QTFposProc, output freq type, 1,2,3=[rad/s,Hz,s]" +'\n')
        else:
            mbox.showinfo("NOTE","QTFposProc, output freq type not set.")
    else:
        file.writelines ('{:<20s}'.format(str(freq_qtfts)) + "! For QTFposProc, output freq type, 1,2,3=[rad/s,Hz,s]"+'\n')  
    #
    if dukos=="":
        if dukos=="":
            file.writelines ('{:<20s}'.format('0') + "! For QTFposProc, 1 includes DUOK in total QTFs, 0 otherwise" +'\n')
        else:
            mbox.showinfo("NOTE","For QTFposProc, DUOK not set.")
    else:
        file.writelines ('{:<20s}'.format(str(dukos)) + "! For QTFposProc, 1 includes DUOK in total QTFs, 0 otherwise"+'\n')
    #
    if HASBOs=="":
        if HASBOs=="":
            file.writelines ('{:<20s}'.format('0') + "For QTFposProc, 1 includes HASBO in total QTFs, 0 otherwise" +'\n')
        else:
            mbox.showinfo("NOTE","For QTFposProc, HASBO not set.")
    else:
        file.writelines ('{:<20s}'.format(str(HASBOs)) + "! For QTFposProc, 1 includes HASBO in total QTFs, 0 otherwise"+'\n')
    #
    if HASFS_ASYMPs=="":
        if HASFS_ASYMPs=="":
            file.writelines ('{:<20s}'.format('0') + "! For QTFposProc, 1 includes HASFS+ASYMP in total QTFs, 0 otherwise" +'\n')
        else:
            mbox.showinfo("NOTE","For QTFposProc, HASFS_ASYMP not set.")
    else:
        file.writelines ('{:<20s}'.format(str(HASFS_ASYMPs)) + "! For QTFposProc, 1 includes HASFS+ASYMP in total QTFs, 0 otherwise"+'\n')
    #
    #
    file.close()
    mbox.showinfo('NOTE','Nemoh.cal file Established')
#
# tab4 gui
#
# env set and wave mearment points added
monty41 = ttk.LabelFrame(tab4, text = "Env set")
monty41.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='NW')
ttk.Label(monty41, text="Water depth m").grid(column=0, row=0,sticky='w')
wd = tk.StringVar()
wdEntered = ttk.Entry(monty41, width=12, textvariable=wd)
wdEntered.grid(column=0, row=1)
ttk.Label(monty41, text="Number of bodies").grid(column=0, row=2,sticky='W')
nb = tk.StringVar()
nbEntered = ttk.Entry(monty41, width=12, textvariable=nb,state='disable')
nb.set("1")
nbEntered.grid(column=0, row=3)
#
#
wmpoints=[]
ttk.Label(monty41, text="Wave measure points x y").grid(column=0, row=4,sticky='W')
wmp = tk.StringVar()
wmpEntered = ttk.Entry(monty41, width=12, textvariable=wmp)
wmpEntered.grid(column=0, row=5)
add_mpoint = ttk.Button(monty41, text="add",command = addmpoints)
add_mpoint.grid(column= 0, row=8,sticky="S")
#
# degrees of force
#
monty42 = ttk.LabelFrame(tab4, text = "Body set")
monty42.grid(column = 4, row = 0, padx = 8, pady = 4,sticky='NW')
ttk.Label(monty42, text="Freedom        ").grid(column=0, row=0,sticky='W')
#
Dsurge=tk.IntVar()
ch_surge=tk.Checkbutton(monty42,text = "Surge",variable=Dsurge)
ch_surge.select()
ch_surge.grid(column=0,row=9,sticky='W')
Dsway=tk.IntVar()
ch_sway=tk.Checkbutton(monty42,text = "Sway",variable=Dsway)
ch_sway.select()
ch_sway.grid(column=0,row=10,sticky='W')
Dheave=tk.IntVar()
ch_heave=tk.Checkbutton(monty42,text = "Heave",variable=Dheave)
ch_heave.select()
ch_heave.grid(column=0,row=11,sticky='W')
Droll=tk.IntVar()
ch_roll=tk.Checkbutton(monty42,text = "Roll",variable=Droll)
ch_roll.select()
ch_roll.grid(column=0,row=12,sticky='W')
Dpitch=tk.IntVar()
ch_pitch=tk.Checkbutton(monty42,text = "Pitch",variable=Dpitch)
ch_pitch.select()
ch_pitch.grid(column=0,row=13,sticky='W')
Dyaw=tk.IntVar()
ch_yaw=tk.Checkbutton(monty42,text = "Yaw",variable=Dyaw)
ch_yaw.select()
ch_yaw.grid(column=0,row=14,sticky='W')
#
# wave freq & direction
#
monty43 = ttk.LabelFrame(tab4, text = "Load Cases")
monty43.grid(column = 15, row = 0, padx = 8, pady = 4,sticky='NW')
#
ttk.Label(monty43, text="Freq type").grid(column=0, row=0,sticky='NW')
freqt = tk.StringVar()
freqtEntered = ttk.Entry(monty43, width=12, textvariable=freqt)
freqtEntered.grid(column=0, row=1)
Tips.createToolTip(freqtEntered,'1,2,3=[rad/s,Hz,s]')
#
ttk.Label(monty43, text="Min. Wave Freq. rad/s").grid(column=0, row=2,sticky='NW')
minw = tk.StringVar()
minwEntered = ttk.Entry(monty43, width=12, textvariable=minw)
minwEntered.grid(column=0, row=3)
#
ttk.Label(monty43, text="Max. Wave Freq. rad/s").grid(column=0, row=4,sticky='NW')
maxw = tk.StringVar()
maxwEntered = ttk.Entry(monty43, width=12, textvariable=maxw)
maxwEntered.grid(column=0, row=5)
ttk.Label(monty43, text="Numbers Wave Freq.").grid(column=0, row=6,sticky='NW')
numw = tk.StringVar()
numwEntered = ttk.Entry(monty43, width=12, textvariable=numw)
numwEntered.grid(column=0, row=7)
#
ttk.Label(monty43, text="Min. Wave Dirc. °").grid(column=0, row=8,sticky='NW')
minwd = tk.StringVar()
minwdEntered = ttk.Entry(monty43, width=12, textvariable=minwd)
minwdEntered.grid(column=0, row=9)
ttk.Label(monty43, text="Max. Wave Dirc. °").grid(column=0, row=10,sticky='NW')
maxwd = tk.StringVar()
maxwdEntered = ttk.Entry(monty43, width=12, textvariable=maxwd)
maxwdEntered.grid(column=0, row=11)
ttk.Label(monty43, text="Numbers Wave Dirc.").grid(column=0, row=12,sticky='NW')
numwd = tk.StringVar()
numwdEntered = ttk.Entry(monty43, width=12, textvariable=numwd)
numwdEntered.grid(column=0, row=13)
#
# post set
#
monty44 = ttk.LabelFrame(tab4, text = "Post Set")
monty44.grid(column = 20, row = 0, padx = 8, pady = 4,sticky='NW')
ttk.Label(monty44, text="IRF setting a b c.").grid(column=0, row=0,sticky='NW')
irf = tk.StringVar()
irfEntered = ttk.Entry(monty44, width=12, textvariable=irf)
irfEntered.grid(column=0, row=1)
ttk.Label(monty44, text="Show Pressure?").grid(column=0, row=2,sticky='NW')
shpre=tk.IntVar()
show_yp=tk.Checkbutton(monty44,text = "Yes",variable=shpre)
show_yp.grid(column=0,row=3,sticky='W')
#
ttk.Label(monty44, text="Kochin Funtion a b c").grid(column=0, row=4,sticky='NW')
Koch = tk.StringVar()
KochEntered = ttk.Entry(monty44, width=12, textvariable=Koch)
KochEntered.grid(column=0, row=5)
Tips.createToolTip(KochEntered,'Suggest value: 361 0 360')
#
ttk.Label(monty44, text="Free-surface a b c d").grid(column=0, row=6,sticky='NW')
Frees = tk.StringVar()
FreesEntered = ttk.Entry(monty44, width=12, textvariable=Frees)
FreesEntered.grid(column=0, row=7)
#
ttk.Label(monty44, text="Calculate RAO?").grid(column=0, row=8,sticky='NW')
raos=tk.IntVar()
show_yp=tk.Checkbutton(monty44,text = "Yes",variable=raos)
show_yp.grid(column=0,row=9,sticky='W')
#
ttk.Label(monty44, text="Output freq type").grid(column=0, row=10,sticky='NW')
freq_t = tk.StringVar()
freq_t_Entered = ttk.Entry(monty44, width=12, textvariable=freq_t)
freq_t_Entered.grid(column=0, row=11)
Tips.createToolTip(freq_t_Entered,'1,2,3=[rad/s,Hz,s]')
#
#   QTF set
#
monty45 = ttk.LabelFrame(tab4, text = "QTF Set")
monty45.grid(column = 30, row = 0, padx = 8, pady = 4,sticky='NW')
#
ttk.Label(monty45, text="QTF or not").grid(column=0, row=0,sticky='NW')
qtf=tk.IntVar()
show_yp=tk.Checkbutton(monty45,text = "Yes",variable=qtf)
show_yp.grid(column=0,row=3,sticky='W')
#
ttk.Label(monty45, text="QTF frequency set").grid(column=0, row=4,sticky='NW')
qtff = tk.StringVar()
qtff_Entered = ttk.Entry(monty45, width=12, textvariable=qtff)
qtff_Entered.grid(column=0, row=5)
Tips.createToolTip(qtff_Entered,'Number of radial frequencies, Min, and Max values for the QTF computation')
#
ttk.Label(monty45, text="Unidirection or Bidirection").grid(column=0, row=6,sticky='NW')
qtfd = tk.StringVar()
qtfd_Entered = ttk.Entry(monty45, width=12, textvariable=qtfd)
qtfd_Entered.grid(column=0, row=7)
Tips.createToolTip(qtfd_Entered,'0 Unidirection, Bidirection 1')
#
ttk.Label(monty45, text="Component").grid(column=0, row=8,sticky='NW')
qtfc = tk.StringVar()
qtfc_Entered = ttk.Entry(monty45, width=12, textvariable=qtfc)
qtfc_Entered.grid(column=0, row=9)
Tips.createToolTip(qtfc_Entered,'Contrib, 1 DUOK, 2 DUOK+HASBO, 3 Full QTF (DUOK+HASBO+HASFS+ASYMP)')
#
ttk.Label(monty45, text="Free surface meshfile").grid(column=0, row=10,sticky='NW')
fsmf = tk.StringVar()
fsmf_Entered = ttk.Entry(monty45, width=12, textvariable=fsmf)
fsmf_Entered.grid(column=0, row=11)
Tips.createToolTip(fsmf_Entered,"Name of free surface meshfile (Only for Contrib 3), type 'NA' if not applicable")
#
ttk.Label(monty45, text="Free surface QTF parameters").grid(column=0, row=12,sticky='NW')
fsmf_qtf = tk.StringVar()
fsmf_qtf_Entered = ttk.Entry(monty45, width=12, textvariable=fsmf_qtf)
fsmf_qtf_Entered.grid(column=0, row=13)
Tips.createToolTip(fsmf_qtf_Entered,'Re, Nre, NBessel (for Contrib 3)')
#
ttk.Label(monty45, text="Hydrostatic terms").grid(column=0, row=14,sticky='NW')
hys_term = tk.StringVar()
hys_term_Entered = ttk.Entry(monty45, width=12, textvariable=hys_term)
hys_term_Entered.grid(column=0, row=15)
Tips.createToolTip(hys_term_Entered,'1 Includes Hydrostatic terms of the quadratic first order motion, -[K]xi2_tilde')
#
ttk.Label(monty45, text="Output freq type").grid(column=0, row=16,sticky='NW')
freq_qtft = tk.StringVar()
freq_qtft_Entered = ttk.Entry(monty45, width=12, textvariable=freq_qtft)
freq_qtft_Entered.grid(column=0, row=17)
Tips.createToolTip(freq_qtft_Entered,'For QTFposProc, output freq type, 1,2,3=[rad/s,Hz,s]')
#
ttk.Label(monty45, text="DUOK in total QTFs").grid(column=0, row=18,sticky='NW')
duko = tk.StringVar()
duko_Entered = ttk.Entry(monty45, width=12, textvariable=duko)
duko_Entered.grid(column=0, row=19)
Tips.createToolTip(duko_Entered,'For QTFposProc, 1 includes DUOK in total QTFs, 0 otherwise')
#
ttk.Label(monty45, text="HASBO in total QTFs").grid(column=0, row=20,sticky='NW')
HASBO = tk.StringVar()
HASBO_Entered = ttk.Entry(monty45, width=12, textvariable=HASBO)
HASBO_Entered.grid(column=0, row=21)
Tips.createToolTip(HASBO_Entered,'For QTFposProc, 1 includes HASBO in total QTFs, 0 otherwise' )
#
ttk.Label(monty45, text="HASFS+ASYMP").grid(column=0, row=22,sticky='NW')
HASFS_ASYMP = tk.StringVar()
HASFS_ASYMP_Entered = ttk.Entry(monty45, width=12, textvariable=HASFS_ASYMP)
HASFS_ASYMP_Entered.grid(column=0, row=23)
Tips.createToolTip(HASBO_Entered,'For QTFposProc, 1 includes HASFS+ASYMP in total QTFs, 0 otherwise' )
#
# save cal
#
save_cal = ttk.Button(tab4, text="Save",command = savecal)
save_cal.grid(column= 30, row=25,sticky="N")
#-----------------------------------------------------------------------------------------
#
# tab5  set cal file
#
#
def intfile_run():
    #
    db=modname.get()
    if db=="":
        mbox.showerror("ERROR","Modelname missed!")
        return
    #
    gq_value=GQ.get()
    eps_value=eps.get()
    solver_value=solver.get()
    GMRES_value=GMRES.get()
    #
    #
    inputpath=os.getcwd()+"/db/" +db+"/input_solver.txt"
    inputfile=open(inputpath,'w')
    inputfile.writelines('{:<20s}'.format(str(gq_value))+" ! Gauss quadrature (GQ) surface integration, N^2 GQ Nodes, specify N(1,4) "+'\n')
    inputfile.writelines('{:<20s}'.format(str(eps_value))+" ! eps_zmin for determine minimum z of flow and source points of panel, zmin=eps_zmin*body_diameter "+'\n')
    inputfile.writelines('{:<20s}'.format(str(solver_value))+" ! 0 GAUSS ELIM.; 1 LU DECOMP.: 2 GMRES	!Linear system solver "+'\n')
    inputfile.writelines('{:<20s}'.format(str(GMRES_value))+" ! Restart parameter, Relative Tolerance, max iter -> additional input for GMRES "+'\n')
    #
    #
    inputfile.close()
    #
    if os.path.exists(os.getcwd()+"/db/" +db+"/input_solver.txt"):
        print("input_solver.txt ok")
    else:
        mbox.showerror("Error","Input file missed!")
        return
    if os.path.exists(os.getcwd()+"/db/" +db+"/nemoh.cal"):
        print("Nemoh.cal file ok")
    else:
        mbox.showerror("Error","Nemoh.cal file missed!")
        return
    if db=="":
        mbox.showerror("Error","Model name missed!")
        return
    #
    if os.path.exists(os.getcwd()+"/db/" +db+"/mesh/"):
        pass
    else:
        os.mkdir(os.getcwd()+"/db/" +db+"/mesh")
    #
    if os.path.exists(os.getcwd()+"/db/" +db+"/results"):
        shutil.rmtree(os.getcwd()+"/db/" +db+"/results")
        os.mkdir(os.getcwd()+"/db/" +db+"/results")
        os.mkdir(os.getcwd()+"/db/" +db+"/results/sources")
    else:
        os.mkdir(os.getcwd()+"/db/" +db+"/results")
        os.mkdir(os.getcwd()+"/db/" +db+"/results/sources")
    #
    batchpath = os.getcwd()+"/db/" +db+"/run.bat"
    filepath = os.getcwd()+"/db/" +db

    prepath = os.getcwd()+"/bin/preProc.exe"
    solvepath = os.getcwd()+"/bin/Solver.exe"
    postpath = os.getcwd()+"/bin/postProc.exe"
    file = open(batchpath,'w')
    file.writelines("cd " + filepath + '\n')
    file.writelines(prepath + '\n')
    file.writelines(solvepath + '\n')
    file.writelines(postpath + '\n')
    file.close()
    #
    import run_nemoh as rn
    #
    rn.bars(batchpath,filepath,montyRunsta)
    #
#
def qtf_run():
    #
    db=modname.get()
    if db=="":
        mbox.showerror("ERROR","Model name missed!")
        return
    #
    #
    if os.path.exists(os.getcwd()+"/db/" +db+"/nemoh.cal"):
        print("Nemoh.cal file ok")
    else:
        mbox.showerror("Error","Nemoh.cal file missed!")
        return
    #
    #
    if os.path.exists(os.getcwd()+"/db/" +db+"/QTFPreprocOut"):
        shutil.rmtree(os.getcwd()+"/db/" +db+"/QTFPreprocOut")
        os.mkdir(os.getcwd()+"/db/" +db+"/QTFPreprocOut")
        os.mkdir(os.getcwd()+"/db/" +db+"/results/QTF")
    else:
        os.mkdir(os.getcwd()+"/db/" +db+"/QTFPreprocOut")
        os.mkdir(os.getcwd()+"/db/" +db+"/results/QTF")
    #
    batchpath = os.getcwd()+"/db/" +db+"/runq.bat"
    filepath = os.getcwd()+"/db/" +db
    #
    prepath = os.getcwd()+"/bin/QTFpreProc.exe"
    solvepath = os.getcwd()+"/bin/QTFsolver.exe"
    postpath = os.getcwd()+"/bin/QTFpostProc.exe"
    #
    file = open(batchpath,'w')
    file.writelines("cd " + filepath + '\n')
    file.writelines(prepath + '\n')
    file.writelines(solvepath + '\n')
    file.writelines(postpath + '\n')
    file.close()
    #
    import run_nemoh as rn
    #
    rn.bars(batchpath,filepath,montyRunsta)
    #      
#
montyRun = ttk.LabelFrame(tab5, text = "Run Setting")
montyRun.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='N')
#
monty5 = ttk.LabelFrame(montyRun, text = "Calculation Setting")
monty5.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='NW')
#
ttk.Label(monty5, text="GQ surface integration").grid(column=0, row=0,sticky='NW')
GQ = tk.StringVar()
GQEntered = ttk.Entry(monty5, width=12, textvariable=GQ)
GQEntered.grid(column=0, row=1,sticky='N')
GQ.set(2)
Tips.createToolTip(GQEntered,'Gauss quadrature (GQ) surface integration, N^2 GQ Nodes, specify N(1,4)' )
#
ttk.Label(monty5, text="eps_zmin").grid(column=0, row=2,sticky='NW')
eps = tk.StringVar()
epsEntered = ttk.Entry(monty5, width=12, textvariable=eps)
epsEntered.grid(column=0, row=3,sticky='N')
eps.set(0.001)
Tips.createToolTip(epsEntered,'eps_zmin for determine minimum z of flow and source points of panel, zmin=eps_zmin*body_diameter' )
#
ttk.Label(monty5, text="Linear system solver").grid(column=0, row=4,sticky='NW')
solver = tk.StringVar()
solverEntered = ttk.Entry(monty5, width=12, textvariable=solver)
solverEntered.grid(column=0, row=5,sticky='N')
solver.set(0)
Tips.createToolTip(solverEntered,'0 GAUSS ELIM.; 1 LU DECOMP.: 2 GMRES' )
#
ttk.Label(monty5, text="GMRES parameter").grid(column=0, row=6,sticky='NW')
GMRES = tk.StringVar()
GMRESEntered = ttk.Entry(monty5, width=12, textvariable=GMRES)
GMRESEntered.grid(column=0, row=7,sticky='N')
GMRES.set(0)
Tips.createToolTip(GMRESEntered,'Additional input for GMRES: Restart parameter, Relative Tolerance, max iter -> ' )
#
#
monty52 = ttk.LabelFrame(montyRun, text = "Run BVP")
monty52.grid(column = 9, row = 0, padx = 4, pady = 2,sticky='N')
ttk.Label(monty52, text=" ").grid(column=0, row=3,sticky='NW')
runnemoh= ttk.Button(monty52, text="Run",command = intfile_run)
runnemoh.grid(column= 0, row=4,sticky="NW")
#
monty53 = ttk.LabelFrame(montyRun, text = "Run QTF")
monty53.grid(column = 10, row = 0, padx = 4, pady = 2,sticky='N')
ttk.Label(monty53, text=" ").grid(column=0, row=3,sticky='NW')
runnemoh= ttk.Button(monty53, text="Run",command = qtf_run)
runnemoh.grid(column= 0, row=4,sticky="NW")
#
#
montyRunsta = ttk.LabelFrame(tab5, text = "    Progress Monitor    ")
montyRunsta.grid(column = 0, row = 2, padx = 8, pady = 4,sticky='w')
ttk.Label(montyRunsta, text=" ").grid(column=0, row=3,sticky='NW')
#
#--------------------------------------------------
# tab6  results plot
#--------------------------------------------------
#
#  PLOT figures
#
forcepath=""
cmpath=""
capath=""
raopath=""
driftpath=""
indexpath=""
#
direcn=""
freqn=""
direc=""
freq=""
#
admass=np.zeros([1,6,6])
damp=np.zeros([1,6,6])
#
def read_in():  #read index file
    path=filedialog.askopenfilename()
    # rhos=rho.get()
    right=len(path)-path.rfind("/")
    t=len(path)-right
    path=path[0:t]
    #
    #定义结果路径
    #
    global modelpath,forcepath, cmpath,capath,raopath,driftpath,indexpath,direcn,freqn,direc,freq
    modelpath = path+'\\mesh\\Mesh.tec'
    forcepath = path+'\\results\\ExcitationForce.tec'
    cmpath = path+'\\results\\CA.dat'
    capath = path+'\\results\\CM.dat'
    raopath = path+'\\motion\\RAO.dat'
    # driftpath=path+'\\results\\Driftforce_far.tec'
    indexpath=path+'\\results\\index.dat'
    #
    direcn,freqn,direc,freq=ri.read_index(indexpath)
    #print(direcn,freqn,direc)
#
#
def read_r():   # readin radiation
    plt.figure(figsize=(8, 6.5))
    if direcn=="":
        mbox.showerror("Error!","Model file path not ben specified!")
        return
    admass=np.zeros([freqn,6,6])
    damp=np.zeros([freqn,6,6])
    admass,damp=rrd.read_radia(cmpath,capath,freqn)
    p=np.zeros([freqn])
    t=np.zeros([freqn])
    #
    for i in range(freqn):
        p[i]=2*pi/freq[i]
    #
    x=p
    #
    plt.subplot(2,1,1)
    plt.subplots_adjust(left=0.15, bottom=0.1, right=0.9, top=0.95, wspace=0.2, hspace=0.35)
    #
    for i in range(freqn):
        t[i]=format(admass[i,addmasslist.current(),addmass1list.current()],'.3E')
        ay=addmasslist.get() +" " +addmass1list.get() +" "
    y=t
    plt.plot(x,y,"ro--")
    plt.title('Addedmass of '+addmasslist.get()+" / "+addmass1list.get())
    plt.xlabel('Wave Period  s')
    if addmasslist.current()<=3:
        plt.ylabel('Added mass '+' kg')
    else:
        plt.ylabel('Added mass '+' kg*m^2')
    plt.grid()
    #
    #
    plt.subplot(2,1,2)
    for i in range(freqn):
        t[i]=format(damp[i,damplist.current(),damp1list.current()],".3E")
        ay=damplist.get() +" " +damp1list.get() +" "
    z=t
    plt.plot(x,z,"b+--")
    plt.title('Radiation damping of '+damplist.get()+" / "+damp1list.get())
    plt.xlabel('Wave Period  s')
    if damplist.current()<=3:
        plt.ylabel('Radiation damping '+' kg/s')
    else:
        plt.ylabel('Radiation damping '+' kg*m/s')
    plt.grid()
    plt.show()
#
def read_f():  # readin waveforce
    #
    plt.figure(figsize=(8, 6.5))
    if direcn=="":
        mbox.showerror("Error!","Model file path not ben specified!")
        return
    waveforce=np.zeros([direcn,freqn,6])
    wavephase=np.zeros([direcn,freqn,6])
    waveforce,wavephase=rfr.read_force_rao(forcepath,direcn,freqn)
    t=np.zeros([freqn])
    #
    plt.subplot(2,1,1)
    plt.subplots_adjust(left=0.15, bottom=0.1, right=0.9, top=0.95, wspace=0.2, hspace=0.35)
    #
    p=np.zeros([freqn])
    #
    for i in range(freqn):
        p[i]=2*pi/freq[i]
    #
    x=p
    for j in range(direcn):
        for i in range(freqn):
            t[i]=format(waveforce[j,i,force1list.current()],'.3E')
        y=t
        a=random.randint(1,17)
        plt.plot(x,y,label="Wave "+str(round(float(direc[j])))+"°",marker=cnames[a])
        plt.title('1st order wave force of :'+force1list.get())
        plt.xlabel('Wave Period  s')
        plt.legend(loc="upper right")
        if force1list.current()<=2:
            plt.ylabel('Wave Force '+' N')
        else:
            plt.ylabel('Wave Force '+' N*m')
    plt.grid()
    #
    #
    plt.subplot(2,1,2)
    for j in range(direcn):
        for i in range(freqn):
            t[i]=format(wavephase[j,i,phase1list.current()]*180/2/pi,".3E")
        z=t
        a=random.randint(1,17)
        plt.plot(x,z,label="Wave "+str(round(float(direc[j])))+"°",marker=cnames[a])
        plt.title('1st order wave force phase angel of :'+phase1list.get())
        plt.xlabel('Wave Period  s')
        plt.ylabel('Phase Angel '+' deg')
        plt.legend(loc="upper right")
    plt.grid()
    plt.show()
#
def read_rao():  # readin rao
    #
    plt.figure(figsize=(8, 6.5))
    if direcn=="":
        mbox.showerror("Error!","Model file path not ben specified!")
        return
    #
    if os.path.exists(raopath) == 0:
        mbox.showerror("ERROR","RAO file not exist!")
        return
    else:
        pass
    #
    rao_amp=np.zeros([direcn,freqn,6])
    rao_pha=np.zeros([direcn,freqn,6])
    rao_amp,rao_pha=rmr.read_motion_rao(raopath,direcn,freqn)
    t=np.zeros([freqn])
    #
    plt.subplot(2,1,1)
    plt.subplots_adjust(left=0.15, bottom=0.1, right=0.9, top=0.95, wspace=0.2, hspace=0.35)
    #
    p=np.zeros([freqn])
    #
    for i in range(freqn):
        p[i]=2*pi/freq[i]
    #
    x=p
    for j in range(direcn):
        for i in range(freqn):
            t[i]=format(rao_amp[j,i,raolist.current()],'.3E')
            if raolist.current()<=2:
                t[i]=t[i]
            else:
                t[i]=t[i]*180/pi
        y=t
        a=random.randint(1,17)
        plt.plot(x,y,label="Wave "+str(round(float(direc[j])))+"°",marker=cnames[a])
        plt.title('Motion RAOs of :'+raolist.get())
        plt.xlabel('Wave Period  s')
        plt.legend(loc="upper right")
        if raolist.current()<=2:
            plt.ylabel('Dementionless '+' m/m')
        else:
            plt.ylabel('Dementionless '+' °/m')
    plt.grid()
    #
    #
    plt.subplot(2,1,2)
    for j in range(direcn):
        for i in range(freqn):
            t[i]=format(rao_pha[j,i,phaselist.current()],".3E")
        z=t
        a=random.randint(1,17)
        plt.plot(x,z,label="Wave "+str(round(float(direc[j])))+"°",marker=cnames[a])
        plt.title('Motion RAOs phase angel of :'+phaselist.get())
        plt.xlabel('Wave Period  s')
        plt.ylabel('Phase Angel '+' deg')
        plt.legend(loc="upper right")
    plt.grid()
    plt.show()
#
#
def show_mesh():
    from mesh_view_heal import mesh_viewer_tec as mvt
    mvt(modelpath)
#
# read model path
#
montyPLOT = ttk.LabelFrame(tab6, text = "Results Plot")
montyPLOT.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='W')
#
monty90 = ttk.LabelFrame(montyPLOT, text = "Set path and view the mesh")
monty90.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='W')
#
monty91 = ttk.LabelFrame(monty90, text = "")
monty91.grid(column = 0, row = 0, padx = 8, pady = 4,sticky='W')
ttk.Label(monty91, text="Model File Path").grid(column=0, row=0,sticky='W')
openfile = ttk.Button(monty91, text="OPEN",command = read_in)
openfile.grid(column= 1, row=0,sticky="S")
#
# show mesh
#
monty92 = ttk.LabelFrame(monty90, text = "")
monty92.grid(column = 1, row = 0, padx = 8, pady = 4,sticky='W')
ttk.Label(monty92, text="Show Mesh").grid(column=0, row=0,sticky='W')
viewmesh = ttk.Button(monty92, text="OPEN",command = show_mesh)
viewmesh.grid(column= 1, row=0,sticky="S")
#
# added mass & radiantion damping
#
monty93 = ttk.LabelFrame(montyPLOT, text = "Added mass and radiation damping")
monty93.grid(column = 0, row = 1, padx = 8, pady = 4,sticky='W')
ttk.Label(monty93, text="Added Mass").grid(column=0, row=0,sticky='W')
addmass= tk.StringVar()
addmasslist=ttk.Combobox(monty93,textvariable=addmass,width =5)
addmasslist['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
addmasslist.grid(column=1, row=0)
addmass1= tk.StringVar()
addmass1list=ttk.Combobox(monty93,textvariable=addmass1,width =5)
addmass1list['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
addmass1list.grid(column=2, row=0)
ttk.Label(monty93, text="Radiation Damping               ").grid(column=0, row=1,sticky='W')
damp= tk.StringVar()
damplist=ttk.Combobox(monty93,textvariable=damp,width =5)
damplist['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
damplist.grid(column=1, row=1)
damp1= tk.StringVar()
damp1list=ttk.Combobox(monty93,textvariable=damp1,width =5)
damp1list['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
damp1list.grid(column=2, row=1)
add_dpoint = ttk.Button(monty93, text="Apply",command = read_r)
add_dpoint.grid(column= 3, row=1,sticky="S")
#
# wave force
#
monty94 = ttk.LabelFrame(montyPLOT, text = "Wave Force")
monty94.grid(column = 0, row = 5, padx = 8, pady = 4,sticky='W')
ttk.Label(monty94, text="1st order wave force").grid(column=0, row=0,sticky='W')
force1= tk.StringVar()
force1list=ttk.Combobox(monty94,textvariable=force1,width =5)
force1list['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
force1list.grid(column=1, row=0)
ttk.Label(monty94, text="1st order wave force phase angle        ").grid(column=0, row=1,sticky='W')
phase1= tk.StringVar()
phase1list=ttk.Combobox(monty94,textvariable=phase1,width =5)
phase1list['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
phase1list.grid(column=1, row=1)
add_fp1point = ttk.Button(monty94, text="Apply",command = read_f)
add_fp1point.grid(column= 2, row=1,sticky="S")
#
# Motion RAOs
#
monty95 = ttk.LabelFrame(montyPLOT, text = "Motion RAOs")
monty95.grid(column = 0, row = 8, padx = 8, pady = 4,sticky='W')
ttk.Label(monty95, text="Motion RAOs").grid(column=0, row=0,sticky='W')
rao= tk.StringVar()
raolist=ttk.Combobox(monty95,textvariable=rao,width =5)
raolist['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
raolist.grid(column=1, row=0)
ttk.Label(monty95, text="RAOs' phase angle                             ").grid(column=0, row=1,sticky='W')
phase= tk.StringVar()
phaselist=ttk.Combobox(monty95,textvariable=phase,width =5)
phaselist['values']=('Surge','Sway','Heave','Roll','Pitch','Yaw')
phaselist.grid(column=1, row=1)
add_raoppoint = ttk.Button(monty95, text="Apply",command = read_rao)
add_raoppoint.grid(column= 2, row=1,sticky="S")
#
win.mainloop()
#
