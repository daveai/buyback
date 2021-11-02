from eth_utils import address
from web3 import Web3
from abis import gp_abi, be_abi
import requests
import pandas as pd
from datetime import datetime
from brownie import Wei

w3 = Web3(Web3.HTTPProvider("https://xdai-archive.blockscout.com/"))

gp_relay = w3.eth.contract(address="0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46", abi=gp_abi)
be = w3.eth.contract(address='0x25B06305CC4ec6AfCF3E7c0b673da1EF8ae26313', abi=be_abi)

orders = gp_relay.events.PlacedTrade.createFilter(fromBlock=0)

orders = orders.get_all_entries()

data = []

for order in orders:
    _order_info = be.functions.orders(gp_relay.address, order['args']['_gpOrderID']).call()
    t = w3.eth._get_block(order['blockNumber'])['timestamp']
    t = str(datetime.fromtimestamp(t).strftime("%d-%m-%Y"))
    eth_price = requests.get(f"https://api.coingecko.com/api/v3/coins/ethereum/history?date={t}&localization=false").json()['market_data']['current_price']['usd']

    temp = [
        order['args']['_gpOrderID'],
        t,
        Wei(order['args']['tokenInAmount']).to('ether'),
        order['args']['tokenInAmount'] / order['args']['expectedAmountMin'],
        _order_info[-1] / _order_info[-2],
        Wei(order['args']['expectedAmountMin']).to('ether'),
        Wei(order['args']['tokenInAmount'] * (1 -_order_info[-1] / _order_info[-2])).to('ether'),
        order['args']['validUntil'],
        'https://blockscout.com/xdai/mainnet/tx/' + order['transactionHash'].hex(),
        eth_price,
        eth_price * order['args']['tokenInAmount'] / order['args']['expectedAmountMin'],
    ]
    data.append(temp)

cols = [
    'orderID',
    'executionDate',
    'WETHamount',
    'DXD/WETH',
    'fill',
    'minDXD',
    'WETHleft',
    'batchExpiry',
    'txsHash',
    'ethPrice',
    'dxdPrice'
]

df = pd.DataFrame(data, columns=cols)

df.to_csv('order_data.csv', index=False)