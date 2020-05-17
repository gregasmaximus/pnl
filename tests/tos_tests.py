# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:23:53 2020

@author: gregas
"""

#----- Module setup
import os
import sys
sys.path[0] = os.path.abspath(os.path.join(__file__,'../../src'))
import pnl.tos as tos
#----- Setup Complete

# Get trades from example ToS statement
statement = '../data/2020-05-08-AccountStatement.csv'
trades = tos.extract_trades(statement)
print('# of trades:', len(trades))
print('First trade date: ',  trades['Exec Time'].min())
print('First trade date: ',  trades['Exec Time'].max())