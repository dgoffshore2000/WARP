#
import meshmagick
from meshmagick import mmio
from meshmagick.mesh import Mesh, Plane
import os
#
def mesh_viewer(path): #模型显示
    #
    c,d=mmio.load_MAR(path)
    t2=Mesh(c,d)
    t2.show()
#
def mesh_viewer_tec(path): #模型显示
    #
    c,d=mmio.load_TEC(path)
    t2=Mesh(c,d)
    t2.show()
#
def mesh_healer(db,path):  #模型修复
    #
    c,d=mmio.load_MAR(path)
    t2=Mesh(c,d)
    Mesh.heal_mesh(t2)  #修复模型
    print("---------------------------")
    print("Mesh Quality of Old Model:")
    print("---------------------------")
    t2.print_quality()
    t2.quick_save(os.getcwd()+"/db/" +db+"/Mesh1.vtp")
    c1,d1=mmio.load_VTP(os.getcwd()+"/db/" +db+"/Mesh1.vtp")
    t3=Mesh(c1,d1)
    print("------------------------------")
    print("Mesh Quality of Healed Model:")
    print("------------------------------")
    t3.print_quality()
    mmio.write_MAR(path,c1,d1)
    t3.show()
#
def add_point():
    pass

#

