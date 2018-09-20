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


import numpy as np
import pandas as pd
import tools as tl
import os
from arff2pandas import a2p
from scipy import stats
import json
import time
from sklearn import preprocessing
import matplotlib.pyplot as plt

t0 = time.clock()

print("define variable and load data")

path = '/Users/e31989/Desktop/e31989/Documents/sm_database/'

database_nml = path + 'normal.json'
database_int = path + 'internal.json'
database_op = path + 'opcode/opcodes_count/'

database_nml_np = path + 'normal_np.json'
database_int_np = path + 'internal_np.json'
database_op_np = path + 'opcode_np/opcode_count/bytecode_np/'

op = [[f[:-5] for f in os.listdir(database_op) if f[-5:] == '.json'],[f[:-5] for f in os.listdir(database_op_np) if f[-5:] == '.json']]
N = len(op[0])
N_np = len(op[1])

opcodes = ['SWAP8','DUP11','DUP14','SWAP10','DUP15','LOG2','INVALID','SWAP9','SWAP5','SWAP12','SWAP16',
           'DUP9','LOG1','DUP12','SWAP11','SWAP2','MSTORE8','SWAP14','DUP13','POP','DUP1','DUP8','DUP7',
           'DUP3','DUP4','MSTORE','SWAP3','CODECOPY','JUMP','DUP5','SWAP13','STOP','CALLDATACOPY','SWAP7',
           'SWAP1','SWAP6','RETURN','DUP6','SWAP4','REVERT','DUP2','SELFDESTRUCT','DUP10','DUP16','JUMPI',
           'SSTORE','PUSH','LOG3','LOG4','Missing','SWAP15']

J = 100000

tr_dico =[[],[]]
#if the raw database has been modified
#tr_dico = tl.open_data(opcodes)

with open(path + 'tr_dico_ponzi.json','rb') as f:
    tr_dico[0] = json.loads(f.read())
    
with open(path + 'tr_dico_nonponzi1.json','rb') as f:
   tr_dico[1]= json.loads(f.read())

with open(path + 'tr_dico_nonponzi2.json','rb') as f:
   tr_dico[1] += json.loads(f.read())
   
with open(path + 'tr_dico_nonponzi3.json','rb') as f:
   tr_dico[1] += json.loads(f.read())
   
size_info = []   
for i in op[0]:
    size_info.append(os.path.getsize(path + 'bytecode/'+ i + '.json'))   
for i in op[1]:
    size_info.append(os.path.getsize(path + 'bytecode_np/'+ i + '.json'))   
   
#print(tr_dico)

with open(path + 'op_freq.json','rb',) as f:
    op_freq = json.loads(f.read()) 

#print(op_freq)

t3 = tl.compute_time(t0)

"""
from dictionary to lists

normal : {
(0)'blockNumber': 'n',
(1)'timeStamp': 'n'
(2) 'hash': '0x..',
(3) 'nonce': 'n',
(4)'blockHash': '0x..e6',
(5)'transactionIndex': '1',
(6)'from': '0x..',
(7)'to': '0x..',
(8)'value': 'n',
(9)'gas': 'n',
(10)'gasPrice': 'n',
(11)'isError': '0',
(12)'txreceipt_status': '',
(13)'input': '0x..',
(14)'contractAddress': '0x..',
(15)'cumulativeGasUsed': 'n',
(16)'gasUsed': 'n,
(17)'confirmations': 'n'}

internal :{
(0)'blockNumber', 
(1)'timeStamp', 
(2)'hash', 
(3)'from', 
(4)'to', 
(5)'value', 
(6)'contractAddress', 
(7)'input', 
(8)'type', 
(9)'gas', 
(10)'gasUsed', 
(11)'traceId', 
(12)'isError', 
(13)'errCode'}

value = 10**18 ETH value
"""

print("computing features for ponzi...")   
    
ft_names = [
            #'addr',
            'ponzi',
            'nbr_tx_in',
            'nbr_tx_out', 
            'Tot_in', 
            'Tot_out',
            'mean_in',
            'mean_out',
            'sdev_in',
            'sdev_out',
            'gini_in',
            'gini_out',
            'avg_time_btw_tx',
            'gini_time_out',
            'lifetime',
            ]

#ideas: lifetime,number of active days, max/min/avg delay between in and out, max/min balance

n = len(ft_names)
ft = []

for i in range(N):
    val_in = []
    val_out = []
    time_in = []
    time_out = []
    
    birth = float(tr_dico[0][i][0][0]['timeStamp'])
    for tx in tr_dico[0][i][0]+tr_dico[0][i][1]:
        
        timestamp = float(tx['timeStamp'])
        
        if (timestamp-birth)/(60*60*24) <= J:

            if tx['from'] == '' or tx['from']== op[0][i]:
                val_out.append(float(tx['value']))
                time_out.append(timestamp)
            else:
                val_in.append(float(tx['value']))
                time_in.append(timestamp)
        
    
    val_in = np.asarray(val_in)
    val_out = np.asarray(val_out)
    time_in = np.asarray(time_in) 
    time_out = np.asarray(time_out)         
    
    #data[0].append(val_in,val_out,time_in,time_out)
    
    res = tl.basic_features("ponzi",val_in,val_out,time_in,time_out)  

    ft.append(np.concatenate((res,  np.asarray(op_freq[0][i],dtype = 'float32'))))

t4 = tl.compute_time(t3)

print("computing features for non ponzi...")   

            
for i in range(N_np):
    val_in = []
    val_out = []
    time_in = []
    time_out = []
    
    birth = float(tr_dico[1][i][0][0]['timeStamp'])
    for tx in tr_dico[1][i][0]+tr_dico[1][i][1]:
        
        timestamp = float(tx['timeStamp'])
        
        if (timestamp-birth)/(60*60*24) <= J:        
        
            
            if tx['from'] == '' or tx['from']== op[1][i]:
                val_out.append(float(tx['value']))
                time_out.append(float(tx['timeStamp']))
            else:
                val_in.append(float(tx['value']))
                time_in.append(float(tx['timeStamp']))     

    val_in = np.asarray(val_in)
    val_out = np.asarray(val_out)
    time_in = np.asarray(time_in) 
    time_out = np.asarray(time_out)         
    
    #data[0].append(val_in,val_out,time_in,time_out)
    
    res = tl.basic_features("non_ponzi",val_in,val_out,time_in,time_out)  

    ft.append(np.concatenate((res, np.asarray(op_freq[1][i],dtype = 'float32'))))
    


t6 = tl.compute_time(t4)


print("creating pandas dataframe...") 
   
columns = [s + '@NUMERIC' for s in ft_names+opcodes]  
columns[0] =   "ponzi@{ponzi,non_ponzi}"
    
df = pd.DataFrame(data = ft, columns = columns)

df['size_info@NUMERIC'] = size_info
#data.loc[:, data.columns != columns[0]] = data.loc[:, data.columns != columns[0]].astype(np.float64)

t7 = tl.compute_time(t6)



print("getting rid of outliers for the non ponzi instances")

min_max_scaler = preprocessing.StandardScaler()

#get rid of outliers
out_index = 3
"""
dum = df.drop(df[df[columns[0]] == 'ponzi'].index)
df_out = dum[(np.abs(stats.zscore(min_max_scaler.transform(dum.drop(labels=[columns[0]]+columns[n:],axis=1)))) < out_index).all(axis=1)]
df_out = df_out.append(df.drop(df[df[columns[0]] == 'non_ponzi'].index))

"""
dum = df.drop(df[df[columns[0]] == 'ponzi'].index)
df_out = dum[(np.abs(stats.zscore(np.asarray(dum.drop(labels=[columns[0]]+columns[n:],axis=1), dtype = 'float32'))) < out_index).all(axis=1)]
df_out = df_out.append(df.drop(df[df[columns[0]] == 'non_ponzi'].index))


t8 = tl.compute_time(t7)

print("dumping into arff files ...")

"""
with open(path + 'models/PONZI_'+ str(J) + '.arff','w') as f:
    a2p.dump(df,f)
    

with open(path + 'models/PONZI_out_'+ str(J) + '.arff','w') as f:
    a2p.dump(df_out,f)
    
    
t9 =tl.compute_time(t8)
"""

tl.compute_time(t0)

"""
plt.hist(df['avg_time_btw_tx@NUMERIC'][145:].astype('float32')/(60*60), bins = 15)
plt.hist(df['avg_time_btw_tx@NUMERIC'][:145].astype('float32')/(60*60), bins = 15)

plt.xlabel('Delay between transactions (hours)')
plt.ylabel('number of instances')
plt.title('Delay between transacstions histogram for non ponzi')
plt.savefig(path + 'delay_histo.png')
"""
