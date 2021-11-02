import requests
from statistics import mean
import pyperclip
from datetime import datetime, timedelta, timezone
from web3 import Web3
from abis import gp_abi

bb_num = input("Buyback Number: ")
net = int(input("Please type 1 for mainnet, or 2 for xDai: "))

if net == 1:
    eth = "ETH"
    token = "DXD"
    net = "mainnet"
    relayer = "https://etherscan.io/address/0xce0BB1a5e9c723fe189D9Bf5457DEd9b21E40f9E"
    relayer_add = "0xce0BB1a5e9c723fe189D9Bf5457DEd9b21E40f9E"
    oracle = "https://etherscan.io/address/0x0e5443a2c6f71e18b9f4f191f52f2d572ccb5a54"
    tokenIn = "0x0000000000000000000000000000000000000000"
    tokenOut = "0xa1d65e8fb6e87b60feccbc582f7f97804b725521"
    factory = "0xd34971bab6e5e356fd250715f5de0492bb070452"
    startdate = int((datetime.now(timezone.utc) + timedelta(8)).timestamp())
    deadline = int((datetime.now(timezone.utc) + timedelta(38)).timestamp())
elif net == 2:
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

eth_price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd").json()['ethereum']['usd']
# AVG trading volume over 90 days. Assuming 20% is on-chain trade, and take 25% of that value.
#volume = requests.get("https://api.coingecko.com/api/v3/coins/dxdao/market_chart?vs_currency=usd&days=90&interval=daily")
volume = 146000#mean([i[1] for i in volume.json()['total_volumes']])*.2
usd_bb = volume*.25
eth_bb = round(usd_bb / eth_price, 2)


proposal_1 = f"""Send {eth_bb} {eth} to GP Relayer for {token} buyback #{bb_num}

This proposal sends {eth_bb} {eth} to the [GP Relayer]({relayer}) intended to be used to place an order to purchase {token} in line with the DXD Buyback Program proposal, which was originally passed on [Mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x40dd1973f7434d192946695919deb58176a192db0c37c8b9316202e006a88ba8) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0xc122e9ea5460917347538157501f7999d82bdd9b1b8d85bee373391c4b87aa45), and extended for another $1m to $3m total, through a further proposal which also passed on [Mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x134c17975ee0e486cdf4719c647c93f94b3bc991b9155193215807521cfce20d) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0x56c66f99d87a48d707475aa2466f0a58da13bd744475410957d6572b439cc5bf). The extension on the buyback program was discussed on [DAOtalk here](https://daotalk.org/t/extend-dxd-buyback-program-for-another-1m-draft-proposal/3319). This funding proposal and the subsequent trade proposal use an updated version of the GP Relayer than the one referenced in the DXD Buyback Program Signal Proposal in order to add Swapr to the GP Relayer’s exchangeFactoryWhitelist.

The DXD Buyback Program Signal proposal stipulates that the purchase amount should be based on the DXD Average Daily Trading Volume (ADTV). [According to the most recent on-chain data and estimates](https://gateway.pinata.cloud/ipfs/QmU1gB6iJbEgxK2BF9ugmH4LSzmwqSA934jb8Y3aieTwtk), DXD has averaged ${int(volume/1000)}k over the last 3 months, so this proposal sends {eth_bb} {eth} to the GP relayer on {net}, identified as `{relayer_add}`, using a [${eth_price} ETH/USD price from Coingecko](https://www.coingecko.com/en/coins/ethereum). Further explanation of the [GP relayer can be found here](https://ipfs.io/ipfs/Qmd8TCEr6syKxAnmuBH3hsyvxfSgRJgANLTTorp3JGZY77). 

This proposal falls under the DXD Buyback Program, because the value of the DXD circulating supply is less than the value in the ETH in DXdao’s treasury, [according to Coingecko](https://www.coingecko.com/en/coins/dxdao) and [Etherscan](https://etherscan.io/token/0xa1d65E8fB6e87b60FECCBc582F7f97804B725521).

This proposal sends funds to the GP Relayer. A separate proposal with the order parameters must also be submitted to place the order. That proposal must be executed _after_ this proposal or else it will fail."""

pyperclip.copy(proposal_1)
print("PROPOSAL COPIED TO CLIPBOARD")

print(tokenIn, int(eth_bb*10**18))

first_proposal = input("Paste link to first proposal, when available:")

proposal_2 = f"""{token} Buyback Order #{bb_num}

This proposal places a {eth}/{token} order on Gnosis Protocol v1 on {net}, using the [GP Relayer]({relayer}). This proposal uses funds from “[Send {eth_bb} {eth} to GP Relayer for {token} buyback #{bb_num}]({first_proposal})”. That proposal must be executed before this one. This proposal and the corresponding trade proposal use an updated version of the GP Relayer than the one referenced in the DXD Buyback Program Signal Proposal in order to add Swapr to the GP Relayer’s exchangeFactoryWhitelist.

This proposal would place a limit order on the Gnosis Protocol at a price that is 4% above the time-weighted average price of {token}/{eth} on Swapr when the proposal is executed and the [Oracle contract is called]({oracle}). The 4% slippage tolerance is under the parameters approved in the [DXD Buyback Program Parameters Update #1](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x58396cc329f5c33bfa29a2e264a05adcad53567a9dcf3e601392d65779dad153) proposal that passed on [mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x58396cc329f5c33bfa29a2e264a05adcad53567a9dcf3e601392d65779dad153) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0xd6c4bfd03d87c365432c073ff0f36578c3cba9da080b75de5058357319908039). The order requires 50 {eth} in the Swapr {token}/{eth} pool when the oracle checks and has a minimum amount of DXD accepted of 35 DXD. The order is live until {datetime.fromtimestamp(deadline).strftime("%a %b %d %Y %X GMT")}.

Further explanation of the [GP relayer can be found here](https://ipfs.io/ipfs/QmdGAjyrpjobow8Hv3fCPoLd5LYRYZPB9qnAWSaRc5krNP). 

Given [the DXD price](https://www.coingecko.com/en/coins/dxdao) and the value of ETH in [DXdao’s treasury](https://etherscan.io/tokenholdings?a=0x519b70055af55a007110b4ff99b0ea33071c720a), this proposal abides by the DXD Buyback Program, which was passed on [mainnet](https://alchemy.daostack.io/dao/0x519b70055af55a007110b4ff99b0ea33071c720a/proposal/0x40dd1973f7434d192946695919deb58176a192db0c37c8b9316202e006a88ba8) and [xDai](https://alchemy.daostack.io/dao/0xe716ec63c5673b3a4732d22909b38d779fa47c3f/proposal/0xc122e9ea5460917347538157501f7999d82bdd9b1b8d85bee373391c4b87aa45) and discussed on [DAOtalk here](https://daotalk.org/t/dxd-buyback-program-signal-proposal/2890)."""

pyperclip.copy(proposal_2)
print("PROPOSAL COPIED TO CLIPBOARD")

params = f"""
TokenIn: {tokenIn}
TokenOut: {tokenOut}
TokenInAmount: {int(eth_bb*10**18)}
MinTokenOutAmount: 35000000000000000000
PriceTolerance: 40000
MinReserve: 10000000000000000000
Startdate: {startdate}
Deadline: {deadline}
Factory: {factory}"""

w3 = Web3(Web3.HTTPProvider('https://xdai-archive.blockscout.com/'))
contract = w3.eth.contract(address='0xA369a0b81ee984a470EA0acf41EF9DdcDB5f7B46', abi=gp_abi)

call_data = contract.encodeABI(fn_name='orderTrade', args=[tokenIn, tokenOut, int(eth_bb*10**18), 35000000000000000000, 40000, 10000000000000000000, startdate, deadline, factory])

print(params)

print(call_data)