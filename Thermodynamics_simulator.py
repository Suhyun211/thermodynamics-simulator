import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msg
from tkinter import simpledialog
import random
import numpy as np
from scipy.stats import maxwell

#상수 또는 처음에 결정하는 값
delta_t=0.01 #(시뮬레이션 기준)스텝 사이 시간 간격(s)
M=0.01       #실제 분자량(kg/mol)
R=8.314      #기체 상수(J/mol K)

modestr=''
class simboard:
    def __init__(self, frame):
        self.c1=tk.Canvas(frame, relief='solid', bg='white')
        self.c1.pack_propagate(False)
        self.c1.pack(fill='both', expand=tk.YES)
        self.c1['width']=600
        self.c1['height']=300
        
    def unpack(self, frame):
        frame.pack_forget()

    def const_vol_sim(self):    #T,P,W를 표시함
        self.num=particle_num.get()
        self.V=amountvolume.get()
        self.size=particle_size.get()
        self.n=self.num/100
        Mol.set(self.n)
        #화면에 표시하는 값
        temper_value.set(2*amountheat.get()/(3*self.n*R))#온도(K)
        pressure_value.set(0)          #압력(atm)
        work_value.set(0)          #기체가 한 일(J) (등적 과정이므로 항상 0)

        #프로그램 내부에서 사용하는 값
        self.v_rms=np.sqrt(3*R*temper_value.get()/M) #분자의 rms 속력
        self.m=self.n*M/self.num   #입자 질량(kg)
        #각 입자의 위치, 속도 저장
        self.p=[]
        self.pad=5
        self.c_width ,self.c_height=600, 300
        self.v_width, self.v_height=self.c_width/10*self.V, self.c_height
        self.c1.create_rectangle(self.v_width, 0, self.v_width+15, self.v_height, fill='black')
        self.c1.create_rectangle(self.v_width+15, self.v_height/2-7.5, 2000, self.v_height/2+7.5, fill='black')
        for i in range(self.num):
            #x1,y1은 입자의 왼쪽 위 좌표, x2,y2는 입자의 오른쪽 아래 좌표
            x1,y1=self.v_width*(random.random()*0.8+0.1),self.v_height*(random.random()*0.8+0.1)
            x2,y2=x1+self.size,y1+self.size
            r1=self.c1.create_oval(x1,y1,x2,y2,fill='black')
            #속도 벡터의 구면 좌표(theta, phi)
            theta=random.random()*np.pi
            phi=random.random()*2*np.pi
            #실제 속도, m/s단위
            vel=maxwell.rvs()/np.sqrt(3)*self.v_rms
            vel_x=vel *np.sin(theta) *np.cos(phi) 
            vel_y=vel *np.cos(theta)
            #delta_t(1스텝)동안 이동하는 pixel 수  #1m = 2339.214pixel
            v_x=vel_x*2339.214/1000/100
            v_y=vel_y*2339.214/1000/100
            self.p.append([x1,y1,x2,y2,r1,v_x,v_y])
        self.press=[]
        def particleMove():
            temper_value.set(2*amountheat.get()/(3*self.n*R))#온도(K)
            self.v_rms=np.sqrt(3*R*temper_value.get()/M) #분자의 rms 속력
            for i in range(self.num):                
                #실제 속도, m/s단위
                vel=maxwell.rvs()/np.sqrt(3)*self.v_rms
                vel_x=vel *np.sin(theta) *np.cos(phi) 
                vel_y=vel *np.cos(theta)
                #delta_t(1스텝)동안 이동하는 pixel 수  #1m = 2339.214pixel
                v_x=vel_x*2339.214/1000/100
                v_y=vel_y*2339.214/1000/100
                self.p[i][5]=self.p[i][5]/abs(self.p[i][5])*v_x
                self.p[i][6]=self.p[i][6]/abs(self.p[i][6])*v_y
            imp=0
            for i in range(self.num):
                #x1 범위 제한, 왼쪽 벽과 탄성 충돌
                if self.p[i][0]<=self.p[i][5]+self.pad:           
                    self.p[i][5]=abs(self.p[i][5])
                #x2 범위 제한, 오른쪽 벽(피스톤)과 탄성 충돌
                if self.p[i][2]>=self.v_width-self.p[i][5]+self.pad:   
                    self.p[i][5]=-abs(self.p[i][5])
                    #피스톤에 가해지는 충격량(kg m/s)
                    imp+=self.m*2*abs(self.p[i][5])/(2339.214/1000/100)
                #y1 범위 제한, 위쪽 벽과 탄성 충돌
                if self.p[i][1]<=self.p[i][6]+self.pad:           
                    self.p[i][6]=abs(self.p[i][6])
                #y2 범위 제한, 아래쪽 벽과 탄성 충돌
                if self.p[i][3]>=self.v_height-self.p[i][6]+self.pad:  
                    self.p[i][6]=-abs(self.p[i][6])
                self.c1.move(self.p[i][4], self.p[i][5], self.p[i][6])
                self.p[i][0]+=self.p[i][5]
                self.p[i][2]+=self.p[i][5]
                self.p[i][1]+=self.p[i][6]
                self.p[i][3]+=self.p[i][6]
                #피스톤을 뚫고 나간 입자(버그)는 다시 안으로 집어넣음
                if self.p[i][0]>=self.v_width+10 or self.p[i][0]<=-20:
                    x_new=self.v_width*(random.random()*0.8+0.1)
                    self.c1.move(self.p[i][4], x_new-self.p[i][0], 0)
                    self.p[i][0]=x_new
                    self.p[i][2]=self.p[i][0]+self.size
            self.press.append(imp)
            imp=0
            if len(self.press)==100:
                #충격량과 압력 사이 비례 상수
                k=0.02924018*0.01*0.001*101325 /1.5 #0.02924018 = 피스톤 단면적(m^2)
                #압력 계산(10스텝 평균 압력)
                pressure_value.set(sum(self.press)/100/k)
                self.press=[]
            self.c1.after(int(delta_t*1000), particleMove)
        particleMove()



    def const_tmp_sim(self):    #V,W를 표시함
        self.V=amountvolume.get()
        self.T=temper_value.get()
        self.num=particle_num.get()
        self.size=particle_size.get()
        self.n=self.num/100
        Mol.set(self.n)

        #화면에 표시하는 값
        amountvolume.set(0)          #부피(L)
        work_value.set(0)          #기체가 한 일(J)

        #프로그램 내부에서 사용하는 값
        self.v_rms=np.sqrt(3*R*self.T/M) #분자의 rms 속력
        m=self.n*M/self.num   #입자 질량(kg)
        self.pad=5
        self.c_width ,self.c_height=600, 300
        self.v_width, self.v_height=self.c_width/10*self.V, self.c_height
        self.piston=self.c1.create_rectangle(self.v_width, 0, self.v_width+15, self.v_height, fill='black')
        self.rod=self.c1.create_rectangle(self.v_width+15, self.v_height/2-7.5, 2000, self.v_height/2+7.5, fill='black')
        #각 입자의 위치, 속도 저장
        self.p=[]
        for i in range(self.num):
            #x1,y1은 입자의 왼쪽 위 좌표, x2,y2는 입자의 오른쪽 아래 좌표
            x1,y1=self.v_width*(random.random()*0.8+0.1),self.v_height*(random.random()*0.8+0.1)
            x2,y2=x1+self.size,y1+self.size
            r1=self.c1.create_oval(x1,y1,x2,y2,fill='black')
            #속도 벡터의 구면 좌표(theta, phi)
            theta=random.random()*np.pi
            phi=random.random()*2*np.pi
            #실제 속도, m/s단위
            vel=maxwell.rvs()/np.sqrt(3)*self.v_rms
            vel_x=vel *np.sin(theta) *np.cos(phi) 
            vel_y=vel *np.cos(theta)
            #delta_t(1스텝)동안 이동하는 pixel 수  #1m = 2339.214pixel
            v_x=vel_x*2339.214/1000/100
            v_y=vel_y*2339.214/1000/100
            self.p.append([x1,y1,x2,y2,r1,v_x,v_y])
            
        #충격량과 압력 사이 비례 상수
        k=0.02924018*0.01*0.001*101325  #0.02924018 = 피스톤 단면적(m^2)

        def pistonMove(imp):
            delta_x=(imp-pressure_value.get()*k)*5
            self.v_width+=delta_x
            if delta_x<0:
                work_value.set(work_value.get()+pressure_value.get()*(delta_x/800*10)*101.325)
            else:
                work_value.set(work_value.get()+(imp/k-pressure_value.get())*(delta_x/800*10)*101.325)
            self.c1.move(self.piston, delta_x, 0)
            self.c1.move(self.rod, delta_x, 0)

        def particleMove():
            imp=0
            for i in range(self.num):
                #x1 범위 제한, 왼쪽 벽과 탄성 충돌
                if self.p[i][0]<=self.p[i][5]+self.pad:           
                    self.p[i][5]=abs(self.p[i][5])
                #x2 범위 제한, 오른쪽 벽(피스톤)과 탄성 충돌
                if self.p[i][2]>=self.v_width-self.p[i][5]+self.pad:   
                    self.p[i][5]=-abs(self.p[i][5])
                    #피스톤에 가해지는 충격량(kg m/s)
                    imp+=m*2*abs(self.p[i][5])/(2339.214/1000/100)
                #y1 범위 제한, 위쪽 벽과 탄성 충돌
                if self.p[i][1]<=self.p[i][6]+self.pad:           
                    self.p[i][6]=abs(self.p[i][6])
                #y2 범위 제한, 아래쪽 벽과 탄성 충돌
                if self.p[i][3]>=self.v_height-self.p[i][6]+self.pad:  
                    self.p[i][6]=-abs(self.p[i][6])
                self.c1.move(self.p[i][4], self.p[i][5], self.p[i][6])
                self.p[i][0]+=self.p[i][5]
                self.p[i][2]+=self.p[i][5]
                self.p[i][1]+=self.p[i][6]
                self.p[i][3]+=self.p[i][6]
                #피스톤을 뚫고 나간 입자(버그)는 다시 안으로 집어넣음
                if self.p[i][0]>=self.v_width+10 or self.p[i][0]<=-20:
                    x_new=self.v_width*(random.random()*0.8+0.1)
                    self.c1.move(self.p[i][4], x_new-self.p[i][0], 0)
                    self.p[i][0]=x_new
                    self.p[i][2]=self.p[i][0]+self.size

            self.c1.after(int(delta_t*1000), particleMove)
            amountvolume.set(self.v_width/800*10)   #기체의 부피(L)계산
            pistonMove(imp)
        particleMove()


    def const_pressure_sim(self):
        self.num=particle_num.get()
        self.P=pressure_value.get()
        self.size=particle_size.get()
        self.n=self.num/100
        Mol.set(self.n)
        
        #화면에 표시하는 값
        temper_value.set(2*amountheat.get()/(5*self.n*R))#온도(K)
        work_value.set(0)          #기체가 한 일(J) (등적 과정이므로 항상 0)
        self.P=pressure_value.get()
        pressure_label.configure(text='부피')
        pressure_entry.configure(textvariable=amountvolume)
        pressure_label2.configure(text='L')


        #프로그램 내부에서 사용하는 값
        self.v_rms=np.sqrt(3*R*temper_value.get()/M) #분자의 rms 속력
        self.m=self.n*M/self.num   #입자 질량(kg)

        self.my_w = tk.Tk()
        self.my_w.title('등압 과정')
        self.c_width,self.c_height=600,300
        self.v_width,self.v_height=self.c_width-100,self.c_height
        self.piston = self.c1.create_rectangle(self.v_width, 0, self.v_width+15, self.v_height, fill='black')
        self.rod = self.c1.create_rectangle(self.v_width+15, self.v_height/2-7.5, 2000, self.v_height/2+7.5, fill='black')

        #각 입자의 위치, 속도 저장
        self.p=[]
        self.pad=5
        for i in range(self.num):
            #x1,y1은 입자의 왼쪽 위 좌표, x2,y2는 입자의 오른쪽 아래 좌표
            x1,y1=self.v_width*(random.random()*0.8+0.1),self.v_height*(random.random()*0.8+0.1)
            x2,y2=x1+self.size,y1+self.size
            r1=self.c1.create_oval(x1,y1,x2,y2,fill='black')
            #속도 벡터의 구면 좌표(theta, phi)
            theta=random.random()*np.pi
            phi=random.random()*2*np.pi
            #실제 속도, m/s단위
            vel=maxwell.rvs()/np.sqrt(3)*self.v_rms
            vel_x=vel *np.sin(theta) *np.cos(phi) 
            vel_y=vel *np.cos(theta)
            #delta_t(1스텝)동안 이동하는 pixel 수  #1m = 2339.214pixel
            v_x=vel_x*2339.214/1000/100
            v_y=vel_y*2339.214/1000/100
            self.p.append([x1,y1,x2,y2,r1,v_x,v_y])
            
        #충격량과 압력 사이 비례 상수
        k=0.02924018*0.01*0.001*101325 #0.02924018 = 피스톤 단면적(m^2)

        def pistonMove(imp):
            delta_x=(imp-self.P*k)*10
            self.v_width+=delta_x
            work_value.set(work_value.get()+self.P*(delta_x/800*10)*101.325)
            self.c1.move(self.piston, delta_x, 0)
            self.c1.move(self.rod, delta_x, 0)

        def particleMove():
            temper_value.set(2*amountheat.get()/(5*self.n*R))#온도(K)
            self.v_rms=np.sqrt(3*R*temper_value.get()/M) #분자의 rms 속력
            for i in range(self.num):                
                #실제 속도, m/s단위
                vel=maxwell.rvs()/np.sqrt(3)*self.v_rms
                vel_x=vel *np.sin(theta) *np.cos(phi) 
                vel_y=vel *np.cos(theta)
                #delta_t(1스텝)동안 이동하는 pixel 수  #1m = 2339.214pixel
                v_x=vel_x*2339.214/1000/100
                v_y=vel_y*2339.214/1000/100
                self.p[i][5]=self.p[i][5]/abs(self.p[i][5])*v_x
                self.p[i][6]=self.p[i][6]/abs(self.p[i][6])*v_y
            imp=0
            for i in range(self.num):
                #x1 범위 제한, 왼쪽 벽과 탄성 충돌
                if self.p[i][0]<=self.p[i][5]+self.pad:           
                    self.p[i][5]=abs(self.p[i][5])
                #x2 범위 제한, 오른쪽 벽(피스톤)과 탄성 충돌
                if self.p[i][2]>=self.v_width-self.p[i][5]+self.pad:   
                    self.p[i][5]=-abs(self.p[i][5])
                    #피스톤에 가해지는 충격량(kg m/s)
                    imp+=self.m*2*abs(self.p[i][5])/(2339.214/1000/100)
                #y1 범위 제한, 위쪽 벽과 탄성 충돌
                if self.p[i][1]<=self.p[i][6]+self.pad:           
                    self.p[i][6]=abs(self.p[i][6])
                #y2 범위 제한, 아래쪽 벽과 탄성 충돌
                if self.p[i][3]>=self.v_height-self.p[i][6]+self.pad:  
                    self.p[i][6]=-abs(self.p[i][6])
                self.c1.move(self.p[i][4], self.p[i][5], self.p[i][6])
                self.p[i][0]+=self.p[i][5]
                self.p[i][2]+=self.p[i][5]
                self.p[i][1]+=self.p[i][6]
                self.p[i][3]+=self.p[i][6]
                #피스톤을 뚫고 나간 입자(버그)는 다시 안으로 집어넣음
                if self.p[i][0]>=self.v_width+10 or self.p[i][0]<=-20:
                    x_new=self.v_width*(random.random()*0.8+0.1)
                    self.c1.move(self.p[i][4], x_new-self.p[i][0], 0)
                    self.p[i][0]=x_new
                    self.p[i][2]=self.p[i][0]+self.size
            self.c1.after(int(delta_t*1000), particleMove)
            amountvolume.set(self.v_width/800*10)
            pistonMove(imp)

        particleMove()

    def simulation_start(self):
        global modestr
        #mode: 0: 등적, 1: 등압, 2: 등온, 3: 단열
        mode=simtype.get()
        if mode==0:
            modestr='등적과정(부피 일정)'
            amountvolume.set(const_volume.get())
            self.const_vol_sim()
            amountvolume_slider['state']='disabled'
        if mode==1:
            modestr='등압과정(압력 일정)'
            pressure_value.set(const_pressure.get())
            self.const_pressure_sim()
        if mode==2:
            temper_value.set(const_temp.get())            
            modestr='등온과정(온도 일정, 압력 조절)'
            self.const_tmp_sim()
            amountheat_slider['state']='disabled'
        whatmodeisit.set(modestr)

def simulation_type():
    if sim is not None:
        sim.disabled = True
    menuwindow.deiconify()       # 새 게임 대화상자를 화면에 표시, 게임판 비활성화

sim=None

def quitmenu():
    if sim is not None:
        sim.disabled = False
    menuwindow.withdraw()

def quitmain():
    if msg.askokcancel('열역학 시뮬레이터', '프로그램을 종료하시겠습니까?'):
        mainwindow.destroy()        # 게임종료 대화상자를 표시, 게임종료   

def simuStart(frame):
    num=simpledialog.askinteger("particle_num", "입자의 개수를 입력하세요")
    particle_num.set(num)
    ss=simpledialog.askinteger("particle_size", "입자의 크기를 입력하세요(5~30)")
    particle_size.set(ss)
    menuwindow.withdraw()
    global sim
    if sim is not None:
        sim.unpack(mainFrame)
    sim= simboard(frame)
    sim.disabled = False
    sim.simulation_start()

# root
mainwindow = tk.Tk()
# mainwindow.geometry('430x200')
mainwindow.title('main')
mainwindow.geometry('1000x500+100+100')

menuwindow=tk.Toplevel(mainwindow)
menuwindow.wm_attributes("-topmost", 1)      # 새 게임 대화상자 윈도우를 생성, 초기설정
menuwindow.geometry('+100+100')
menuwindow.protocol("WM_DELETE_WINDOW", quitmenu)       # 창 닫기 버튼 클릭 시 quitGame 함수 호출


# 열역학 과정 선택 대화상자의 GUI 구성
title_frm=tk.Frame(menuwindow)
title_frm.grid(row=0, column=0, columnspan=4)
levelLabel = tk.Label(title_frm, text='열역학 과정의 종류를 선택해주세요!')
levelLabel.pack(fill='both')

# 라디오 버튼 생성
radio_frame=tk.Frame(menuwindow)
radio_frame.grid(row=1, column=0)
simtype = tk.IntVar()   
isovolumetric = tk.Radiobutton(radio_frame, text='등적과정', variable=simtype, value=0)
isobaric = tk.Radiobutton(radio_frame, text='등압과정', variable=simtype, value=1)
isothermal = tk.Radiobutton(radio_frame, text='등온과정', variable=simtype, value=2)

# 라디오 버튼 배치
isovolumetric.grid(row=0, padx=15)
isobaric.grid(row=1, padx=15)
isothermal.grid(row=2, padx=15)

const_frm=tk.Frame(menuwindow)
const_frm.grid(row=1, column=1, columnspan=3)
# 위젯 클릭시 등장할 entry
const_volume=tk.IntVar(const_frm)
isovolumetric_label1=tk.Label(const_frm, text='부피:')
isovolumetric_label1.grid(row=0, column=0)
isovolumetric_entry=tk.Entry(const_frm, textvariable=const_volume)
isovolumetric_entry.grid(row=0, column=1)
isovolumetric_label2=tk.Label(const_frm, text='L')
isovolumetric_label2.grid(row=0, column=2)

const_pressure=tk.IntVar()
isobaric_label1=tk.Label(const_frm, text='압력:')
isobaric_label1.grid(row=1, column=0)
isobaric_entry=tk.Entry(const_frm, textvariable=const_pressure)
isobaric_entry.grid(row=1, column=1)
isobaric_label2=tk.Label(const_frm, text='atm')
isobaric_label2.grid(row=1, column=2)

const_temp=tk.IntVar()
isothermal_label1=tk.Label(const_frm, text='온도:')
isothermal_label1.grid(row=2, column=0)
isothermal_entry=tk.Entry(const_frm, textvariable=const_temp)
isothermal_entry.grid(row=2, column=1)
isothermal_label2=tk.Label(const_frm, text='K')
isothermal_label2.grid(row=2, column=2)
bin_label=tk.Label(const_frm)
bin_label.grid(row=3, column=0, columnspan=3)

btn_frame=tk.Frame(menuwindow)
btn_frame.grid(row=2, column=0, columnspan=4)
mainFrame=tk.Frame(mainwindow)
startBtn = tk.Button(btn_frame, text='확인', command=(lambda: simuStart(frm_canvas)))
startBtn.pack(fill='both')

#mainwindow 위젯 배치

mainFrame.grid_propagate(False)     # 게임이 들어갈 mainFrame 생성
whatmodeisit=tk.StringVar()
particle_num=tk.IntVar()
particle_size=tk.IntVar()
particle_size.set(20)
amountheat=tk.IntVar()
amountheat.set(6000)
amountvolume=tk.IntVar()
temper_value=tk.IntVar()
pressure_value=tk.IntVar()
work_value=tk.IntVar()
Mol=tk.IntVar()
#Mol.set(mol)

frm1=tk.Frame(mainwindow)
frm2=tk.Frame(mainwindow)
frm3=tk.Frame(mainwindow)
frm4=tk.Frame(mainwindow)
frm5=tk.Frame(mainwindow)
frm6=tk.Frame(mainwindow)
frm_canvas=tk.Frame(mainwindow)
frm1.grid(row=0, column=0, rowspan=2, columnspan=2)
frm2.grid(row=0, column=2, rowspan=2, columnspan=2)
frm3.grid(row=0, column=4, rowspan=2, columnspan=3)
frm4.grid(row=3, column=0, rowspan=1, columnspan=7)
frm5.grid(row=4, column=0, rowspan=1, columnspan=5)
frm6.grid(row=4, column=5, rowspan=7, columnspan=3)
frm_canvas.grid(row=5, column=0, rowspan=6, columnspan=4)

#frm1
particle_num_label=tk.Label(frm1, text='입자 수: ')
particle_num_entry=tk.Entry(frm1, textvariable=particle_num)
particle_num_label.grid(row=0, column=0)
particle_num_entry.grid(row=0, column=1)
whatmode=tk.Label(frm1, textvariable=whatmodeisit)
whatmode.grid(row=1, column=0, columnspan=2)

#frm2
particle_size_label=tk.Label(frm2, text='입자 크기: ')
particle_size_slider = ttk.Scale(frm2, from_=10, to=50, orient='horizontal', variable=particle_size, length=100, state='disabled') ####################
newSimBtn=tk.Button(frm2, text='새로운 시뮬레이션', command=simulation_type)
particle_size_label.grid(row=0, column=0)
particle_size_slider.grid(row=0, column=1)
newSimBtn.grid(row=1, column=0, columnspan=2)

#frm3
def resetwork():
    work_value.set(0)
actual_mol_label=tk.Label(frm3, text='실제 몰 수: ')
actual_mol_entry=tk.Entry(frm3, textvariable=Mol)
actual_mol_label2=tk.Label(frm3, text='mol')
resetwork_button=tk.Button(frm3, text='기체가 한 일 초기화', command=resetwork)
quitGameBtn = tk.Button(frm3, text=' X ', command=quitmain, foreground='red')
actual_mol_label.grid(row=0, column=0)
actual_mol_entry.grid(row=0, column=1)
actual_mol_label2.grid(row=0, column=3)
resetwork_button.grid(row=1, column=0, columnspan=2)
quitGameBtn.grid(row=1, column=3)

#frm4
amountheat_label=tk.Label(frm4, text='가한 열')
amountheat_slider = ttk.Scale(frm4, from_=100, to=30000, orient='horizontal', variable=amountheat, length=500) ####################
amountheat_label.grid(row=0, column=0)
amountheat_slider.grid(row=0, column=1)

#frm5
amountvolume_label=tk.Label(frm5, text='부피')
amountvolume_slider = ttk.Scale(frm5, from_=1, to=10, orient='horizontal', variable=amountvolume, length=300) ####################
amountvolume_label.grid(row=0, column=0, sticky='w')
amountvolume_slider.grid(row=0, column=1, sticky='w')

#frm6
temper_label=tk.Label(frm6, text='온도:')
temper_entry=tk.Entry(frm6, textvariable=temper_value)
temper_label2=tk.Label(frm6, text='K')
pressure_label=tk.Label(frm6, text='압력:')
pressure_entry=tk.Entry(frm6, textvariable=pressure_value)
pressure_label2=tk.Label(frm6, text='atm')
work_label=tk.Label(frm6, text='한 일:')
work_entry=tk.Entry(frm6, textvariable=work_value)
work_label2=tk.Label(frm6, text='J')
temper_label.grid(row=0,column=0)
temper_entry.grid(row=0,column=1)
temper_label2.grid(row=0,column=2)
pressure_label.grid(row=1,column=0)
pressure_entry.grid(row=1,column=1)
pressure_label2.grid(row=1,column=2)
work_label.grid(row=2,column=0)
work_entry.grid(row=2,column=1)
work_label2.grid(row=2,column=2)


mainwindow.mainloop()

