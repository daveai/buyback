import requests
from statistics import mean
import pyperclip
from datetime import datetime, timedelta, timezone
from web3 import Web3
from abis import gp_abi

bb_num = input("Buyback Number: ")

premium = 3

eth = "WETH"
token = "xDXD"
net = "xDai"
relayer = "https://blockscout.com/poa/xdai/address/0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46/transactions"
relayer_add = "0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46"
oracle = "https://blockscout.com/xdai/mainnet/address/0xFbAc9467FCcb14394860A9E280E2FBabCBbc8DD2/transactions"
tokenIn = "0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1"
tokenOut = "0xb90D6bec20993Be5d72A5ab353343f7a0281f158"
factory = "0x5D48C95AdfFD4B40c1AAADc4e08fc44117E02179"
startdate = int((datetime.now(timezone.utc) + timedelta(5)).timestamp())
deadline = int((datetime.now(timezone.utc) + timedelta(35)).timestamp())

eth_price = requests.get(
    "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
).json()["ethereum"]["usd"]
# AVG trading volume over 90 days. Assuming 20% is on-chain trade, and take 25% of that value.
# volume = requests.get("https://api.coingecko.com/api/v3/coins/dxdao/market_chart?vs_currency=usd&days=90&interval=daily")
volume = 141122  # mean([i[1] for i in volume.json()['total_volumes']])*.2
volume_link = "https://gateway.pinata.cloud/ipfs/QmS4XFgwiWrPZZriT6tsVDu9JH5533D7LPKWc7kqjbwdJe?preview=1"
usd_bb = volume * 0.25
eth_bb = round(usd_bb / eth_price, 2)


proposal = f"""{token} Buyback Order #{bb_num} for {eth_bb} {eth}

This proposal places a {eth}/{token} order on Gnosis Protocol v1 on {net}, using the [GP Relayer]({relayer}). This proposal uses funds in the GP Relayer. [According to the most recent on-chain data and estimates]({volume_link}), DXD has averaged ${int(volume/1000)}k over the last 3 months. This proposal places an order for {eth_bb} {eth} using a [${eth_price} ETH/USD price from Coingecko](https://www.coingecko.com/en/coins/ethereum) in line with the DXD Buyback Program proposal, which was originally passed on [Mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x40dd1973f7434d192946695919deb58176a192db0c37c8b9316202e006a88ba8) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0xc122e9ea5460917347538157501f7999d82bdd9b1b8d85bee373391c4b87aa45), and extended for another $1m to $3m total, through a further proposal which also passed on [Mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x134c17975ee0e486cdf4719c647c93f94b3bc991b9155193215807521cfce20d) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0x56c66f99d87a48d707475aa2466f0a58da13bd744475410957d6572b439cc5bf). The extension on the buyback program was discussed on [DAOtalk here](https://daotalk.org/t/extend-dxd-buyback-program-for-another-1m-draft-proposal/3319). 

This proposal would place a limit order on the Gnosis Protocol at a price that is {premium}% above the time-weighted average price of {token}/{eth} on Swapr when the proposal is executed and the [Oracle contract is called]({oracle}). The {premium}% slippage tolerance is under the parameters approved in the [DXD Buyback Program Parameters Update #1](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x58396cc329f5c33bfa29a2e264a05adcad53567a9dcf3e601392d65779dad153) proposal that passed on [mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x58396cc329f5c33bfa29a2e264a05adcad53567a9dcf3e601392d65779dad153) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0xd6c4bfd03d87c365432c073ff0f36578c3cba9da080b75de5058357319908039). The order requires 50 {eth} in the Swapr {token}/{eth} pool when the oracle checks and has a minimum amount of DXD accepted of 35 DXD. The order is live until {datetime.fromtimestamp(deadline).strftime("%a %b %d %Y %X GMT")}.

Further explanation of the [GP relayer can be found here](https://ipfs.io/ipfs/QmdGAjyrpjobow8Hv3fCPoLd5LYRYZPB9qnAWSaRc5krNP). 

Given [the DXD price](https://www.coingecko.com/en/coins/dxdao) and the value of ETH in [DXdao’s treasury](https://etherscan.io/tokenholdings?a=0x519b70055af55a007110b4ff99b0ea33071c720a), this proposal abides by the DXD Buyback Program, which was passed on [mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x40dd1973f7434d192946695919deb58176a192db0c37c8b9316202e006a88ba8) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0xc122e9ea5460917347538157501f7999d82bdd9b1b8d85bee373391c4b87aa45) and discussed on [DAOtalk here](https://daotalk.org/t/dxd-buyback-program-signal-proposal/2890)."""

pyperclip.copy(proposal)
print("PROPOSAL COPIED TO CLIPBOARD")

params = f"""
TokenIn: {tokenIn}
TokenOut: {tokenOut}
TokenInAmount: {int(eth_bb*10**18)}
MinTokenOutAmount: 35000000000000000000
PriceTolerance: {premium*10000}
MinReserve: 10000000000000000000
Startdate: {startdate}
Deadline: {deadline}
Factory: {factory}"""

w3 = Web3(Web3.HTTPProvider("https://xdai-archive.blockscout.com/"))
contract = w3.eth.contract(
    address="0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46", abi=gp_abi
)

call_data = contract.encodeABI(
    fn_name="orderTrade",
    args=[
        tokenIn,
        tokenOut,
        int(eth_bb * 10 ** 18),
        35000000000000000000,
        premium * 10000,
        10000000000000000000,
        startdate,
        deadline,
        factory,
    ],
)

print(params)

print(call_data)
