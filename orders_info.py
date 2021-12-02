from eth_utils import address
from web3 import Web3
from abis import gp_abi, be_abi
import requests
import pandas as pd
from datetime import datetime
from brownie import Wei
from tqdm import tqdm

# Connect to xDai archive node
print("Connecting to xDai archive node...")
w3 = Web3(Web3.HTTPProvider("https://xdai-archive.blockscout.com/"))
print("Done.\n")

# Setup GP relayer contract and the Batch Exchange contract (GPv1)
gp_relay = w3.eth.contract(
    address="0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46", abi=gp_abi
)
be = w3.eth.contract(address="0x25B06305CC4ec6AfCF3E7c0b673da1EF8ae26313", abi=be_abi)

# Pull all orders placed by GP relayer
orders = gp_relay.events.PlacedTrade.createFilter(fromBlock=0)
orders = orders.get_all_entries()

# Get and save latest ETH prices in a dictionary
print("Pulling latest ETH price data...")
req = requests.get(
    "https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=max&interval=daily"
)
prices = req.json()["prices"]
for i in prices:
    i[0] = datetime.fromtimestamp(i[0] / 1000).strftime("%d-%m-%Y")
prices = dict(prices)
print("Done.\n")

data = []

print("Retrieving order data on-chain...")
for order in tqdm(orders):
    _order_info = be.functions.orders(
        gp_relay.address, order["args"]["_gpOrderID"]
    ).call()
    t = w3.eth._get_block(order["blockNumber"])["timestamp"]
    t = str(datetime.fromtimestamp(t).strftime("%d-%m-%Y"))
    eth_price = prices[t]

    temp = [
        order["args"]["_gpOrderID"],
        t,
        Wei(order["args"]["tokenInAmount"]).to("ether"),
        order["args"]["tokenInAmount"] / order["args"]["expectedAmountMin"],
        _order_info[-1] / _order_info[-2],
        Wei(order["args"]["expectedAmountMin"]).to("ether"),
        Wei(
            order["args"]["tokenInAmount"] * (1 - _order_info[-1] / _order_info[-2])
        ).to("ether"),
        order["args"]["validUntil"],
        "https://blockscout.com/xdai/mainnet/tx/" + order["transactionHash"].hex(),
        eth_price,
        eth_price * order["args"]["tokenInAmount"] / order["args"]["expectedAmountMin"],
    ]
    data.append(temp)

cols = [
    "orderID",
    "executionDate",
    "WETHamount",
    "DXD/WETH",
    "fill",
    "minDXD",
    "WETHleft",
    "batchExpiry",
    "txsHash",
    "ethPrice",
    "dxdPrice",
]

# Save data to order_data.csv
df = pd.DataFrame(data, columns=cols)
df.to_csv("order_data.csv", index=False)

# Calculate actual amount of DXD bought. Sum of withdrawls + balance in be.
print("\nCalculating total amount of DXD bought...")
dxd_withdrawls = be.events.Withdraw.createFilter(
    fromBlock=0,
    argument_filters={
        "user": gp_relay.address,
        "token": "0xb90D6bec20993Be5d72A5ab353343f7a0281f158",
    },
)
dxd_withdrawls = dxd_withdrawls.get_all_entries()
dxd_withdrawn = Wei(sum([i["args"]["amount"] for i in dxd_withdrawls]))
dxd_balance = Wei(
    be.functions.getBalance(
        gp_relay.address, "0xb90D6bec20993Be5d72A5ab353343f7a0281f158"
    ).call()
)
total = dxd_withdrawn + dxd_balance
print(f"Total DXD bought: {total.to('ether')}")
