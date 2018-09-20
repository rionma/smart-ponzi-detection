#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
 --------------------------------------------------------------------------------
 SPADE - Support for Provenance Auditing in Distributed Environments.
 Copyright (C) 2015 SRI International
 This program is free software: you can redistribute it and/or
 modify it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.
 --------------------------------------------------------------------------------

"""

import ast
import numpy as np
import pandas as pd
from web3.auto import w3
import tools as tl
import os
from arff2pandas import a2p
from scipy import stats
import json

import time

def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    """ gini(array) = 1 corresponds to the worst case scenario, e.g inequality"""
    # based on bottom eq:
    # http://www.statsdirect.com/help/generatedimages/equations/equation154.svg
    # from:
    # http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    # All values are treated equally, arrays must be 1d:
    array = np.asarray(array).flatten()
    if array.size ==0:
        return 0
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    # Values cannot be 0:
    array += 0.0000001
    # Values must be sorted:
    array = np.sort(array)
    # Index per array element:
    index = np.arange(1,array.shape[0]+1)
    # Number of array elements:
    n = array.shape[0]
    # Gini coefficient:
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


def compute_time(t0):
    
    print("computation done in " + str(time.clock() - t0) +"s")
    
    return time.clock()


def mean(tab, s):
    if s>0:
        return np.mean(tab)
    else :
        return s
    
def std(tab,s):
    if s>0:
        return np.std(tab)
    else:
        return s

def maxi(tab):
    if len(tab)>0:
        return np.max(tab)
    else:
        return 0
        
def basic_features(ponzi, val_in,val_out,time_in,time_out):
    N_in =int(val_in.size)
    N_out = int(val_out.size)
    times = np.concatenate((time_in, time_out))


    res = np.asarray([
            ponzi,
            N_in,
            N_out,
            np.sum(val_in),
            np.sum(val_out),
            mean(val_in, N_in), 
            mean(val_out, N_out),
            std(val_in,N_in),
            std(val_out,N_out),
            gini(val_in),
            gini(val_out),
            (np.max(times)-np.min(times))/(N_in +N_out),
            gini(time_out),
            np.max(times)-np.min(times),
            ])
    return res



def open_data(opcodes):

    t0 = time.clock()
    
    print("tools.opend_data: define variables...")
    
    path = '/Users/e31989/Desktop/e31989/Documents/sm_database/'
    
    database_nml = path + 'normal.json'
    database_int = path + 'internal.json'
    database_op = path + 'opcode/opcodes_count/'
    
    database_nml_np = path + 'normal_np.json'
    database_int_np = path + 'internal_np.json'
    database_op_np = path + 'opcode_np/opcode_count/bytecode_np/'
  
    
    t1 = tl.compute_time(t0)
    
    #Open databases to access info
    
    print("tools.open_data: open databases...")
    #ponzi instances
    with open(database_nml, 'r') as f:
        raw_nml= f.readlines()
        
    with open(database_int, 'r') as f:
        raw_int= f.readlines()
        
    op = [[f[:-5] for f in os.listdir(database_op) if f[-5:] == '.json'],[f[:-5] for f in os.listdir(database_op_np) if f[-5:] == '.json']]
    
    op_freq = [[],[]]
    for add in op[0]:    
        with open(database_op + add + '.json', 'r') as f:
            raw = f.readlines()
            res = [0 for i in range(len(opcodes))]
            if len(raw) > 1 :
                tot = 0
                for opcode in raw:
                    count = float(opcode[3])
                    tot += count
                    res[opcodes.index(opcode[5:-1])] = count
            else:
                tot = 1
            res = [x/tot for x in res]
            op_freq[0].append(res)
            
    #non ponzi instances
    with open(database_nml_np, 'r') as f:
        raw_nml_np= f.readlines()
        
    with open(database_int_np, 'r') as f:
        raw_int_np= f.readlines()
           
    for add in op[1]:    
        with open(database_op_np + add + '.json', 'r') as f:
            raw = f.readlines()
            res = [0 for i in range(len(opcodes))]
            if len(raw) > 1 :
                tot = 0
                for opcode in raw:
                    count = float(opcode[3])
                    tot += count
                    res[opcodes.index(opcode[5:-1])] = count
            else:
                tot = 1
            
            res =[x/tot for x in res]
            op_freq[1].append(res)        
    
    t2 = tl.compute_time(t1)
    
    with open(path + 'op_freq.json', 'w') as outfile:
        outfile.write(json.dumps(op_freq))
        print('op_freq serialized')
        
        #tr_dico is a list of which the size is the number of SM, each element is a list of which the size 
        #is the number of transactions, each element is a dictionnary containing data about a specific transacton.
    print("tools.open_data: create dictionnaries...")
    #ponzi instances    
    addr = [raw_nml[2*i][:-1] for i in range(len(raw_nml)//2)]
    addr_int = [raw_int[2*i][:-1] for i in range(len(raw_int)//2)]
    
    addr_np = [raw_nml_np[2*i][:-1] for i in range(len(raw_nml_np)//2)]
    addr_int_np = [raw_int_np[2*i][:-1] for i in range(len(raw_int_np)//2)]
    
    N = len(op[0])
    N_np = len(op[1])
        
    tr_dico = [
            #ponzi
            [[ast.literal_eval(raw_nml[2*addr.index(op[0][i])+1][:-1]),ast.literal_eval(raw_int[2*addr_int.index(op[0][i])+1][:-1])] for i in range(N)],
            #non ponzi
            [[ast.literal_eval(raw_nml_np[2*addr_np.index(op[1][i])+1][:-1]),ast.literal_eval(raw_int_np[2*addr_int_np.index(op[1][i])+1][:-1])] for i in range(N_np)]
            ]        
    
                
    tl.compute_time(t2)
    temp = int(N_np/3)
    
    #saved in three different files, because os.write and os.read doesn't support file with size superior to 2GB, ours is 4.2Gb.

    with open(path + 'tr_dico_nonponzi1.json','w') as f:
        f.write(json.dumps(tr_dico[1][:temp]))
    
    print('serialized half tr_dico')
        
    with open(path + 'tr_dico_nonponzi2.json','w') as f:
        f.write(json.dumps(tr_dico[1][temp:2*temp]))
   
    with open(path + 'tr_dico_nonponzi3.json','w') as f:
        f.write(json.dumps(tr_dico[1][2*temp:]))    
    print('everything has been serialized')
    
    return tr_dico


def reset(tab):
    if len(tab)>0:
        return tab - tab[0]
    else:
        return tab

def features_evol(ponzi, val_in,val_out,time_in,time_out):
    N_in =int(val_in.size)
    N_out = int(val_out.size)
    times = np.concatenate((time_in, time_out))

    res = [
            ponzi,
            N_in,
            N_out,
            np.sum(val_in),
            np.sum(val_out),
            mean(val_in, N_in), 
            mean(val_out, N_out),
            std(val_in,N_in),
            std(val_out,N_out),
            gini(val_in),
            gini(val_out),
            (np.max(times)-np.min(times))/(N_in +N_out),
            gini(time_out),
            np.max(times)-np.min(times),
            reset(time_in),
            reset(time_out),
            ]
    tr = []
    gini_in = []
    for i in range(N_in):
        tr.append(val_in[i])
        gini_in.append(gini(tr))
        
    tr = []
    gini_out = []
    for i in range(N_out):
        tr.append(val_out[i])
        gini_out.append(gini(tr))
        
        
    res.append(gini_in)
    res.append(gini_out)
    
    return res        

"""
def avg(attr, df):   
    res = [np.mean(df[attr][:145].astype('float32'), np.mean(df[attr][145:].astype('float32'))]
    return res
"""