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


"""

Run using cmd: scrapy runspider code/Cimport_data.py 
With file 'Smart_Contract_Addresses.list' containing the blockchain addresses of each smart contracts

Returns: json files containing all the transactions info of each smart contract

"""

import scrapy
from scrapy.contrib.spiders import CrawlSpider as Spider
import csv
import ast



path = '/Users/e31989/Desktop/e31989/Documents/'
database_nml = path + 'sm_database/normal_np.json'
database_int = path + 'sm_database/internal_np.json'

#sm_file = 'Smart_Contract_Addresses.list'
sm_file = 'sm_add_nponzi.csv'

with open(path + sm_file,'rt') as f:
    truc = csv.reader(f)
    add = list(truc)
    

addresses = [pk[:42] for pklist in add for pk in pklist] 

#create files
nml = open(database_nml,'w')
nml.close()
#fired = open(database_int, 'w')
#fired.close()



  
#print(addresses)

urls_nml = ['http://api.etherscan.io/api?module=account&action=txlist&address='+ pk + '&startblock=0&endblock=99999999&sort=asc&apikey=APIbirthday' for pk in addresses]

class ethCrawler_normalTr(Spider):
    name = "Crawler_nml"
    start_urls =urls_nml
    
    
    def parse(self, response):
        with open(database_nml, 'a') as f:
            f.write(response.url.split('=')[3].split('&')[0] +"\n")
            f.write(response.body[38:-1].decode('utf-8') + '\n')

            f.close
"""

urls_int = ['http://api.etherscan.io/api?module=account&action=txlistinternal&address=' + pk +'&startblock=0&endblock=9999999&sort=asc&apikey=APIbirthday' for pk in addresses]        
class ethCrawler_internalTr(Spider):
    name = "Crawler_int"
    start_urls =urls_int

    def parse(self, response):
        with open(database_int, 'a') as f:
            f.write(response.url.split('=')[3].split('&')[0] +"\n")
            #print(response.body.decode('utf-8'))
            if response.body[25:27].decode('utf-8') == 'OK':
                f.write(response.body[38:-1].decode('utf-8') + '\n')
            else:
                f.write('[]\n')
            f.close


"""

    