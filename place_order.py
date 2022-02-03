#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 12:31:56 2021

@author: mark
"""

import json
import datetime
from pyserum.connection import conn
from pyserum.enums import OrderType, Side
from pyserum.market import Market
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.types import TxOpts
from spl.token.client import Token
from spl.token.constants import TOKEN_PROGRAM_ID
import base58
from solana.keypair import Keypair

# For a given ccy pair, get the market and the token mint
from pyserum.connection import get_live_markets, get_token_mints
pair = "SOL/USDC"
side = Side.SELL

pair_mkt = {}
for mkt in get_live_markets():
    pair_mkt.update({mkt.name:mkt.address})
print("Market Address is: {}".format(pair_mkt[pair]))

quote_ccy = pair.split("/")[0]
quote_ccy_mint = {}
for mkt in get_token_mints():
    quote_ccy_mint.update({mkt.name:mkt.address})
print("Token Mint is: {}".format(quote_ccy_mint[quote_ccy]))


# Get private key and use that the create a new account
#pubkey = "GKksmU6hSJ2X7zz1mcE3Qhr7DDEpvxqbygzb17SxygUD"
f = open('./my-solana-wallet/my-keypair.json')
private_key = json.load(f)
mid = len(private_key)//2
private_key = private_key[:mid] # to 32 bytes 
payer = Account(private_key) # Your account to pay fees
k=payer.keypair()
b = k
b=b.decode('utf-8')
print("Public Key is: {}".format(payer.public_key()))



# print(b) # Your account to pay fees
print("Public Key is: {}".format(payer.public_key()))

def get_keypair(private_key):
    byte_array = base58.b58decode(private_key)
    return byte_array
owner_key_pair = get_keypair(b)
# print(owner_key_pair)

cc = conn("https://solana-api.projectserum.com")

quote_token = Token(
    cc,
    pubkey=PublicKey(quote_ccy_mint[quote_ccy]), # mint address of token
    program_id=TOKEN_PROGRAM_ID,
    payer=Keypair(owner_key_pair[:32]),
)

quote_wallet = quote_token.create_account(
  payer.public_key(),
  skip_confirmation=False)  # Make sure you send tokens to this address
print("quote wallet: ", str(quote_wallet))

market_address = PublicKey(pair_mkt[pair]) 
market = Market.load(cc, market_address)

tx_sig = market.place_order(
    payer=quote_wallet, #PublicKey(pubkey), # My public key
    owner=Keypair(owner_key_pair[:32]),
    side=side,
    order_type=OrderType.LIMIT,
    limit_price=100,
    max_quantity=0.1,
    opts = TxOpts(skip_preflight=False)
)
print(tx_sig)

summary = {"mkt_add": pair_mkt[pair],
           "token_mint": quote_ccy_mint[quote_ccy],
           "public_key": str(payer.public_key()),
           "quote_wallet":str(quote_wallet),
           "tx_sig":tx_sig}
with open('tx_{}'.format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")), 'w') as f:
    json.dump(summary, f, indent=4)
    