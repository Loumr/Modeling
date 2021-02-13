# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 14:04:23 2021

@author: loumo
"""

import numpy as np
import weakref
from scipy.integrate import quad 


class wind: #defined by its direction and speed
    def __init__(self):
        self.direction=0 #angle with the road in radian
        self.speed=0


class vehicle_class: #defined by its name
    
    _instances=set()
    
    def __init__(self):
        self.name='type'
        self._instances.add(weakref.ref(self))
 
    @classmethod
    def getinstances(cls):
        dead=set()
        for ref in cls._instances:
            obj=ref()
            if obj is not None:
                yield obj
            else:
                dead.add(ref)
        cls._instances -=dead

class road: #defined by its length, a list of points, a number of segments and a list of segments
    def __init__(self):
        self.length=0
        self.points=[[0,0]]  #list
        self.Ns=0
        self.l=0 #length of segments
        self.segments=[[[0,0],[0,0]]] #list of segments;1 segment= 2 points

class pollutant: #defined by its name
    def __init__(self):
        self.name='pollutant_name'
        
class flow_channel:
    def __init__(self):
        self.j=0 #number of channel flow
        self.H=0
        self.L=0
        self.W=0 #to get the width of the channels the roads must be more than segments
        self.X=0
        self.Li_array=np.zeros(len(road.segments))#length of intersection with the channel flow for each segment


##segments

def set_Ns_l(road): #sets Ns and l with Ns as small as possible for l to be <=500m
    L=road.length
    Ns=1
    while L/Ns > 500:
        Ns+=1
    road.Ns=Ns
    road.l=L/Ns
    
def points(road):
    points=np.zeros((road.Ns+1,2))
    points[0,0]=0
    points[0,1]=0
    for i in range(1,road.Ns+1):
        points[i,0]=points[i-1,0]+road.l #along x-axis
    road.points=points    
    
def segments(road):
    segments=np.zeros((road.Ns,2,2))
    segments[0,0]=np.array([0,0])
    segments[0,1]=np.array([road.l,0])
    
    for i in range (1,road.Ns):
        segments[i,0]=np.array(segments[i-1,1])
        segments[i,1]=np.array(segments[i,0])
        segments[i,1,0]=segments[i,1,0]+road.l
    road.segments=segments
    

## channel flows

def width_channelj(wind): #wind is a class wind object
    if np.cos(wind.direction)==0:
        return l
    else:
        return l/(np.cos(wind.direction))
    
def dist(p1,p2):
    return np.sqrt((p1[1]-p2[1])**2+(p1[0]-p2[0])**2)

def scalar_product_2(u,v):
    return u[0]*v[0]+u[1]*v[1]

def between_segment(point,segment):
    [p1,p2]=segment
    u=[p2[0]-p1[0],p2[1]-p1[1]]  #u,v vectors
    v=[point[0]-p1[0],point[1]-p1[1]]
    if scalar_product_2(u,v)>=0 and scalar_product_2(u,v)<= scalar_product_2(u,u):
        return True
    else:
        return False

def what_segment(point,segments):
    for i in len(segments):
        if between_segment(point,segments[i]):
            return i
        else:
            return None 
            
def lengths_segments(Lold,Lnew,segments,flow_channel):
    p0=[Lold,0]  #works because the road is considered to be along x-axis
    p1=[Lnew,0]
    i0=what_segment(p0,segments)
    i1=what_segment(p1,segments)
    diff=i1-i0
    if diff==0:
        flow_channel.Li_array[i0]=Lnew-Lold
    else:
        L_temp=segments[i0][1][0]
        flow_channel.Li_array[i0]=L_temp-Lold
        Lold=L_temp
        #segments[i0][1][0]=x-coordinate of second point of segment[i0] \
        #because segments are along x-axis
        return lengths_segments(Lold,Lnew,segments,flow_channel)
    

def flow_channels(road,wind,D): #wind is a class wind object or an array of class wind objects
 #D is the distance from the road to the inhabited area(supposed here to be behind a line perpendicular to the route)
    j=0
    S_L=0 #sum of Lj
    L=[]
    X=[]
    #we could define H and W too if they were different along the road
    L_old=0
    L_new=0
    f=[]
    segments=road.segments
    while S_L<road.length:
        L_old=L_new
        L_new=L_new+width_channelj(wind) #if wind is the same along the road
        l_temp=L_new-L_old
        L.append(l_temp)
        X.append(l_temp*D/l)
        #flow channel
        f_temp=flow_channel()
        f_temp.j=j
        f_temp.L=l_temp
        f_temp.X=l_temp*D/l
        lengths_segments(L_old,L_new,segments,f_temp)
        
        f.append(f_temp)
        
        S_L+=l_temp
        j+=1
        
    Nb=len(f)
    f_temp=f[Nb]
    f_temp.L=f_temp.L-(S_L-road.length)
    f[Nb]=f_temp
    
    return f #list of flow_channels
     
##tests

road=road()
road.length=5881 
road.points=[[0,0],[road.length,0]]

L=road.length
Ns=road.Ns
set_Ns_l(road)
segments(road)
l=road.l

wind1=wind()
wind1.direction=np.pi/3
D=100

flow_channels(road,wind1,D)
