from web3 import Web3
from brownie import Wei
import pandas as pd
from abis import be_abi

w3 = Web3(Web3.HTTPProvider('http://localhost:8545'))

contract = w3.eth.contract(address='0x25B06305CC4ec6AfCF3E7c0b673da1EF8ae26313', abi=be_abi)

trades = contract.events.Trade.createFilter(fromBlock=0)

trade_events = trades.get_all_entries()
