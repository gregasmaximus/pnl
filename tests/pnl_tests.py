# -*- coding: utf-8 -*-
"""
Created on Fri May  8 09:23:53 2020

@author: gregas
"""

#----- Module setup
import os
import sys
sys.path[0] = os.path.abspath(os.path.join(__file__,'../../src'))
#from datetime import datetime as dt
#import pandas as pd
#import numpy as np
import pnl
import pnl.tos as tos
#----- Setup Complete

# Get trades from example ToS statement
statement = '../data/2020-05-17-AccountStatement.csv'

#df = tos.extract_df_from_stmt(statement, 'Account Trade History')

new_trades = tos.extract_trades(statement)
open_trades = pnl.create_open_trade_df()
closed_trades = pnl.create_closed_trade_df()

ot, ct = pnl.update_trades(new_trades, open_trades, closed_trades)

