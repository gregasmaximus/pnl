# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 13:20:57 2020

@author: gregas
"""

import csv
import numpy as np
import pandas as pd

def extract_df_from_stmt(file, header):
    """
    Extracts a sections of ToS statement export into a dataframe
    May need further processing to due differences between sections
    """
    found_start = False
    with open(file) as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            #print(i, row)
            if not found_start:
                if len(row) == 1  and row[0] == header:
                    found_start = True
                    start_line = i+1
                    #print('start_line: ', start_line)
            else:
                if len(row) == 0:
                    df = pd.read_csv(file, skiprows=start_line, 
                                           nrows=i-start_line-1)
                    return df

def extract_trades(file):
    
    trades = extract_df_from_stmt(file, 'Account Trade History')
    # Forward fill these fields for spreads
    trades['Account Code'].fillna(method='ffill', inplace=True)
    trades['Order ID'].fillna(method='ffill', inplace=True)
    trades['Account Code'] = trades['Account Code'].astype(np.int64)
    trades['Order ID'] = trades['Order ID'].astype(np.int64)
    trades['Exec Time'].fillna(method='ffill', inplace=True)
    trades['Exec Time'] = pd.to_datetime(trades['Exec Time'])
    trades['Spread'].fillna(method='ffill', inplace=True)
    trades['Order Type'].fillna(method='ffill', inplace=True)
    # For spreads, price is in first leg. Make price zero for other legs
    trades['Net Price'].replace('CREDIT', value=0., inplace=True)
    trades['Net Price'].replace('DEBIT', value=0., inplace=True)
    trades['Underlying'] = trades['Symbol'] 
    trades['Symbol'] = trades['Opra'].combine(trades['Symbol'], 
                        lambda opra, symbol: symbol if pd.isna(opra) else '.'+opra)
    trades.drop('Opra', axis=1, inplace=True)
    trades = trades[['Account Code', 'Order ID', 'Exec Time', 'Spread',  
                     'Type', 'Symbol', 'Underlying', 'Qty', 'Pos Effect', 
                     'Exp', 'Strike', 'Price', 'Net Price', 'Order Type']]
    trades.sort_values('Exec Time', inplace=True)
    
    return trades

def tos_to_float(s):
    # Clean out extraneous chars and convert to float
    s = s.replace('(', '-')
    s = s.replace(')', '')
    s = s.replace('$', '')
    s = s.replace('%', '')
    s = s.replace(',', '')
    return float(s)

def extract_options(file):
    options = extract_df_from_stmt(file, 'Options')[:-1]
    options['Exp'] = pd.to_datetime(options['Exp'])
    options['P/L Day'] = options['P/L Day'].apply(tos_to_float)
    options['P/L Open'] = options['P/L Open'].apply(tos_to_float)
    options['P/L %'] = options['P/L %'].apply(tos_to_float)
    options.set_index('Option Code', inplace=True)
    return options

def extract_equities(file):
    positions = extract_df_from_stmt(file, 'Equities')[:-1]
    positions['Mark Value'] = positions['Mark Value'].apply(tos_to_float)
    positions.set_index('Symbol', inplace=True)
    return positions

if __name__ == '__main__':
    stmt_file = '2020-04-23-AccountStatement.csv'
    x = extract_equities(stmt_file)
    x.head()