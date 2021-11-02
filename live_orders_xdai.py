from web3 import Web3
from brownie import Wei
import pandas as pd
from abis import be_abi

w3 = Web3(Web3.HTTPProvider("https://xdai-archive.blockscout.com"))
# Connect to BatchExchange
be = w3.eth.contract(address='0x25B06305CC4ec6AfCF3E7c0b673da1EF8ae26313', abi=be_abi)

# Get current batch
current_batch = be.functions.getCurrentBatchId().call()

orderPlacements = be.events.OrderPlacement.createFilter(fromBlock=0).get_all_entries()
#orderCancellations = be.events.OrderCancellation.createFilter(fromBlock=0).get_all_entries()
#trades = be.events.Trade.createFilter(fromBlock=0).get_all_entries()

#cancellations = [i['args'] for i in orderCancellations]

orders = [i['args'] for i in orderPlacements if i['args']['buyToken'] in [1,16]]
orders = [i for i in orders if i['sellToken'] in [1,16]]
orders = [i for i in orders if i['validUntil'] > current_batch]

live_orders = []

# loop over order state to delete filled orders
# something like this:
for order in orders:
    data = be.functions.orders(order['owner'], order['index']).call()
    if data[-2] == 0:
        continue
    elif data[-1] / data[-2] < 0.98:
        live_orders.append(order)