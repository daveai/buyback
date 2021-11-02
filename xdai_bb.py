from web3 import Web3
from brownie import Wei
import pandas as pd
from abis import gp_abi

w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

contract = w3.eth.contract(address='0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46', abi=gp_abi)

trades = contract.events.PlacedTrade.createFilter(fromBlock=0)

trade_events = trades.get_all_entries()

trade_data = []

for trade in trade_events:
    info = [
        trade['event'],
        trade['transactionHash'].hex(),
        trade['blockNumber'],
        trade['args']['_gpOrderID'],
        trade['args']['buyToken'],
        trade['args']['sellToken'],
        Wei(trade['args']['tokenInAmount']),
        Wei(trade['args']['expectedAmountMin'])
    ]

    trade_data.append(info)

df_columns = ['event', 'txHash', 'blockNum', 'orderID', 'buyToken', 'sellToken', 'tokenIn', 'expectedOut']

df = pd.DataFrame(trade_data, columns=df_columns)

df['tokenPrice'] = df['tokenIn'] / df['expectedOut']