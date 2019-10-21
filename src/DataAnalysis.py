#!/usr/bin/env python
# coding: utf-8

# In[1]:





# In[20]:


import numpy as np
import scipy as sp
import math
routeData = np.load("out/out_numpy.npy", allow_pickle=True)
# routeData = np.load("E:\学习\iGEM\建模\Celltrack191017\out\out_numpy.npy")

# param
VERBOSE = True
cell_cnt = len(routeData)

if VERBOSE:
    print("cell_cnt={}".format(cell_cnt))

# Find x_ends, y_ends and d_accu
routeAccu = np.array([])
x_ends = np.array([])
y_ends = np.array([])
for i in np.arange(0,cell_cnt,1):
    routeRowVal = 0
    for j in np.arange(1,len(routeData[i]),1):
        routeRowVal += np.sqrt(np.sum(np.square(routeData[i][j]-routeData[i][j-1])))
        if j == len(routeData[i])-1:
            x_ends = np.append(x_ends, routeData[i][j][0])
            y_ends = np.append(y_ends, routeData[i][j][1])
    routeAccu = np.append(routeAccu, routeRowVal)
if VERBOSE:
    print("routeAccu = {}".format(routeAccu))
    print("x_ends = {}".format(x_ends))
    print("y_ends = {}".format(y_ends))

# calculate FMI_para and FMI_verticle
FMI_para = (np.sum(x_ends/routeAccu))/cell_cnt
FMI_vert = (np.sum(y_ends/routeAccu))/cell_cnt
if VERBOSE:
    print("FMI_para = {}".format(FMI_para))
    print("FMI_vert = {}".format(FMI_vert))
    
# Center of Mass
x_com = np.sum(x_ends)/cell_cnt
y_com = np.sum(y_ends)/cell_cnt
pt_com = (x_com, y_com)
if VERBOSE:
    print("Center of Mass --> {}".format(pt_com))
    
# Directness
d_euclid = np.sqrt(np.square(x_ends)+np.square(y_ends))
D = np.sum(d_euclid/routeAccu)/cell_cnt
if VERBOSE:
    print("Directness = {}".format(D))
