#coding:utf-8
__author__ = 'GT'
import tkinter as tk
from tkinter import messagebox
import subprocess
import time
from threading import Thread
#
class MyThread(Thread):
    def __init__(self,func,args=()):
        super(MyThread,self).__init__()
        self.func = func
        self.args = args
    def run(self):
        self.result = self.func(*self.args)
    def get_result(self):
        try:
            return self.result
        except Exception:
            return None
#
def _magboxinfo():
    messagebox.showinfo('Info','Finish nomally.')

def _magboxerro():
    messagebox.showerror('Erro','Run Fail,check log file.')

#
def bars(batchpath, filepath, monty):
    # 创建运行状态标签组件
    status_frame = tk.Frame(monty)
    status_frame.grid(column=2, row=0, columnspan=3, sticky='W')
    
    # 状态指示器
    status_indicator = tk.Label(status_frame, text="●", fg="orange")
    status_indicator.pack(side=tk.LEFT)
    
    # 动态进度文本
    status_text = tk.StringVar()
    status_label = tk.Label(status_frame, textvariable=status_text)
    status_label.pack(side=tk.LEFT)
    status_text.set("Initializing...")

    # 创建并启动工作线程
    runt = MyThread(run_n, args=(batchpath, filepath))
    runt.start()

    # 获取根窗口引用
    root = tk._default_root
    
    def update_progress(dots=0):
        """动态进度动画"""
        animation = "Running" + "." * (dots % 4)
        status_text.set(animation)
        return dots + 1  # 返回下一帧的点数

    def check_thread(dots=0):
        if runt.is_alive():
            # 更新状态指示器
            status_indicator.config(fg="orange" if dots%2 else "dark orange")
            
            # 触发进度动画
            new_dots = update_progress(dots)
            
            # 继续轮询
            root.after(200, check_thread, new_dots)
        else:
            # 最终状态更新
            res = runt.get_result()
            status_indicator.config(fg="green" if res ==1 else "red")
            status_text.set("Completed!" if res ==1 else "Failed!")
            
            # 3秒后自动清除状态
            root.after(3000, status_frame.destroy)
            
            # 弹窗提示
            _magboxinfo() if res ==1 else _magboxerro()

    # 首次启动状态检查
    root.after(100, check_thread)

#
def run_n(batchpath,filepath):
        #
        p=subprocess.Popen("cmd.exe /c" + batchpath,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        curline=p.stdout.readline()
        #logpath=filepath+"/logrun.txt"
        #logfile=open(logpath,'w')
        #logfile.writelines("Start at :"+ time.asctime()+'\n')
        while curline!=b'':
            curline=p.stdout.readline()
            log=str(curline) 
            log=log[3:-5]
            print(log)
            
            
            
 
            #if len(curline)<2:
            #    pass
            #else: 
            #    log=str(curline) 
            #    if log[4:10] == "Problem": 
            #        print(log + "\n") 
            #    else: 
            #        log=log[4:-5] 
            #        print(log)
        #        if log[1:8] == "Problem":
        #            bvp_1 = float(log[9:14])
        #            bvp_n = float(log[17:22])
        #            perc = (bvp_1/bvp_n)*100
        #            percent = str(round(perc,1))
        #            print(" Running BVP"+ '{:>10s}'.format(percent)+"%")
                    # ttk.Label(monty53, text= ' ...'+'{:>6s}'.format(percent)+"%",width = 10).grid(column=1, row=0,sticky='W')
                    # ttk.Label(monty53, text= '',width = int(0.5*perc),background='green',foreground = 'white',borderwidth=20,relief = "raised").grid(column=2, row=0,sticky='W')
        #        logfile.writelines(log + '\n')
        #
        #logfile.writelines("Finish at :" +time.asctime() + '\n')
        #logfile.close()
        p.wait()
        if p.poll()==0:
        #    print ('Success')
            #ttk.Label(monty53, text= " ",background='green',relief = "raised").grid(column=0, row=0,sticky='W')
            #ttk.Label(monty53, text= " Finish    ",width = 10).grid(column=1, row=0,sticky='W')
            #ttk.Label(monty53, text= " ",width = 50).grid(column=2, row=0,sticky='W')
        #    messagebox.showinfo('NOTE','Run finish')
            return 1
        else:
        #    print ('failed')
            #ttk.Label(monty53, text= " ",background='red',relief = "raised").grid(column=0, row=0,sticky='W')
            #ttk.Label(monty53, text= " Error  ",width = 10).grid(column=1, row=0,sticky='W')
            #ttk.Label(monty53, text= " ",width = 50).grid(column=2, row=0,sticky='W')
        #    messagebox.showerror('ERROR','Run Failed')
            return 0





  