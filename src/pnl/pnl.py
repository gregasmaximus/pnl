# -*- coding: utf-8 -*-
"""
Trading Profit and Loss Calculations
Principles:
    - Use trade log to build / unbuild postions
    - Use FIFO method to match opening / closing trades
    - Maintain dataframes for open and closed trades


"""

import numpy as np
import pandas as pd

def update_trades(new_trades, open_trades, closed_trades):
    
    """
    Uses df of new trades to update tables of open and closed trades
    
    Algo:
        - New trades must be sorted in ascending order of "Exec Time"
        - For each new trade:
            while abs(qty) > 0:
            - Do we have an existing open trade to close?
                - Yes:
                    - Trade size >= open pos?
                        - create ct record with qty open pos size (watch sign)
                        - reduce nt.Qty by open pos size
                        - drop open pos
                      
                    - Trade size < open pos
                        - create ct record with qty trade size (watch sign)
                        - reduce open pos by trade size
                - No:
                    - Create new open trade
                    
    Notes:
        - Combination of Order ID + Symbols is not unique!
            - Trades with multiple fills create multiple trades
            - When dropping open trades (after closing), multiple trades 
              get dropped, instead of just one.
            - Need a unique index for each line - add it to ot
            - Revisit FIXME lines below
                    
    """
    
    # For debugging:
    dbugsym = 'ICSH'
    
    # Don't mangle the dataframes that we are passed.
    ct = closed_trades.copy()
    ot = open_trades.copy()

    for i, nt in new_trades.iterrows(): # for each new trade...
        while (abs(nt.Qty) > 0): # iterate until distribution of new trade done
            if nt.Symbol == dbugsym:
                dot = ot[ot.Symbol == dbugsym]
                dct = ct[ct.Symbol == dbugsym]
                print('\n*** Before:')
                print(f'New Tradel: {nt.Symbol}, Qty: {nt.Qty}')
                print(f"Open Trades in {dbugsym}: {dot.loc[:, ['Symbol', 'Qty', 'Time Opened', 'Opening Price']]}")
                print(f"Closed Trades in {dbugsym}: {dct.loc[:, ['Symbol', 'Qty', 'Time Closed', 'Closing Price']]}")
                
            # get open trades in this account and symbol
            pos = ot[ (ot['Account Code'] == nt['Account Code']) 
                    & (ot.Symbol == nt.Symbol) ]
            
            # If it is a closing trade
            if len(pos) > 0 and np.sign((pos.iloc[0].Qty * nt.Qty)) < 0: 
                p = pos.iloc[0] # get first open positon
                
                # if trade size >= position size
                if abs(nt.Qty) >= abs(p.Qty): 
                    # create record for closed trade    
                    ct = ct.append({ 
                            'Account Code': nt['Account Code'], 
                            'Symbol': nt['Symbol'], 
                            'Qty': p['Qty'],
                            'Time Opened': p['Time Opened'], 
                            'Opening Order': p['Opening Order'], 
                            'Opening Price': p['Opening Price'], 
                            'Time Closed': nt['Exec Time'],
                            'Closing Order': nt['Order ID'],
                            'Closing Price': nt['Price']}, ignore_index=True)
                    # Reduce qty of new trade by closed trade
                    nt.Qty += p.Qty 
                    
                    # drop trade from open trades - need to use both Order ID
                    #    and Smybol since spread orders have same Order ID
                    #    but different symbol for each leg
                    # FIXME: Line below inadvertantely drops multiple trades
                    # 'Opening Order' + Symbol is not unique!
                    ot = ot[ ~ ((ot['Opening Order'] == p['Opening Order']) 
                                & (ot.Symbol == p.Symbol))]
                    
                else: # trade size < positions size
                    # create record for closed trade    
                    ct = ct.append({ 
                            'Account Code': nt['Account Code'], 
                            'Symbol': nt['Symbol'], 
                            'Qty': -nt['Qty'],
                            'Time Opened': p['Time Opened'], 
                            'Opening Order': p['Opening Order'], 
                            'Opening Price': p['Opening Price'], 
                            'Time Closed': nt['Exec Time'],
                            'Closing Order': nt['Order ID'],
                            'Closing Price': nt['Price']}, ignore_index=True)
                    # Reduce qty of open position by closed trade
                    # FIXME: Line below may have unexpected effects
                    # 'Opening Order' + Symbol is not unique!
                    ot.loc[(ot['Opening Order'] == p['Opening Order']) 
                       & (ot.Symbol == p.Symbol), 'Qty'] += nt.Qty
                    nt.Qty = 0 # We have distributed the remaining quantity
                    
            else: # It's an opening trade
                ot = ot.append({ 'Account Code': nt['Account Code'], 
                             'Symbol': nt['Symbol'], 'Qty': nt['Qty'],
                             'Time Opened': nt['Exec Time'], 
                             'Opening Order': nt['Order ID'], 
                             'Opening Price': nt['Price']}, ignore_index=True)
                nt.Qty = 0 # We have distributed the remaining quantity
                
            # filter down to one symbol for debugging
            if nt.Symbol == dbugsym:
                dot = ot[ot.Symbol == dbugsym]
                dct = ct[ct.Symbol == dbugsym]
                print('\n*** After:')
                print(f'New Tradel: {nt.Symbol}, Qty: {nt.Qty}')
                print(f"Open Trades in {dbugsym}: {dot.loc[:, ['Symbol', 'Qty', 'Time Opened', 'Opening Price']]}")
                print(f"Closed Trades in {dbugsym}: {dct.loc[:, ['Symbol', 'Qty', 'Time Closed', 'Closing Price']]}")
                print('-'*50)
                print()
    return ot, ct    

def create_open_trade_df():
    """
    Creates an empty dataframe for open trades
    """
    
    return pd.DataFrame(columns=['Account Code', 'Symbol', 'Qty',
            'Time Opened', 'Opening Order', 'Opening Price'])

def create_closed_trade_df():
    """
    Creates an empty dataframe for closed trades
    """
    
    return pd.DataFrame(columns=['Account Code', 'Symbol', 'Qty',
            'Time Opened', 'Opening Order', 'Opening Price',
            'Time Closed', 'Closing Order', 'Closing Price'])



