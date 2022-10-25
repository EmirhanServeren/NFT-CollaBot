import pandas as pd
import numpy as np
# from matplotlib import pyplot as plt

import requests
import json
import re
import string
from io import StringIO

import streamlit as st

import random
import time
from datetime import *
import math
import contextlib         # for error handling

st.title('NFT CollaBot')
st_user_input=st.text_input('Please enter your Tezos Wallet Address/Domain or Twitter Username registered to your Tezos Profile:')

# objktcom api endpoint will be used for several times to evaluate queries
api_endpoint = 'https://data.objkt.com/v2/graphql'
# check for the new API endpoint launch time, activate new endpoint in case the time has come
def check_API_launch_datetime():
    new_API_launchTime = date(2023,1,20)    # assign the launch time
    current_date=date.today()
    if current_date<new_API_launchTime:     # if earlier than the launch time
        return api_endpoint
    else:
        return 'https://data.objkt.com/v3/graphql'

check_API_launch_datetime()

def findWalletAddress_byTwitter(twitter_address):
    creator_walletAddress_byTwitter_query="""query{
    tzd_domain(where: {token: {holders: {holder: {twitter: {_eq: "twitter_address"}}}}}) {
        owner
        }
    }"""
    evaluated_twitterAddress = f"https://twitter.com/{str(twitter_address)}"
    creator_walletAddress_byTwitter_query = creator_walletAddress_byTwitter_query.replace("twitter_address",evaluated_twitterAddress)

    creator_twitter = requests.post(api_endpoint, json={'query': creator_walletAddress_byTwitter_query})
    creator_twitter = json.loads(creator_twitter.text)
    creator_twitter = creator_twitter ['data']['tzd_domain']
    if creator_twitter != [] and creator_twitter[0]['owner'] != "null":
        return str(creator_twitter[0]['owner'])
    else:            # if query does not respond any name, then there is no wallet matched with the related twitter address
        return False

def findWalletAddress_byTezDomain(tezos_domain):
    creator_walletAddress_byDomain_query="""query findWallet_byDomainAddress {
    tzd_domain(where: {id: {_eq: "tez_domain"}}) {
    owner
        token {
        holders {
            holder {
            twitter
            }
        }
        }
    }
    }"""
    creator_walletAddress_byDomain_query = creator_walletAddress_byDomain_query.replace("tez_domain",tezos_domain)

    creator_tezDomain = requests.post(api_endpoint, json={'query': creator_walletAddress_byDomain_query})
    creator_tezDomain = json.loads(creator_tezDomain.text)
    creator_tezDomain = creator_tezDomain ['data']['tzd_domain']
    if creator_tezDomain != [] and creator_tezDomain[0]['owner'] != "null":
        return str(creator_tezDomain[0]['owner'])
    else:           # if query does not respond any name, then there is no wallet matched with the related tezos domain
        return False


#st.write(findWalletAddress_byTezDomain(tez_domain_input))

def isWalletAddress(wallet_address):
    account_data_url=f"https://api.tzkt.io/v1/accounts/{wallet_address}" # tzkt.io API endpoint
    response = requests.get(account_data_url)
    with contextlib.suppress(KeyError or json.decoder.JSONDecodeError):
        response=response.json()
        if response['type']=="empty":      # checking the responded data that user exists or not
            return False

def isAvailableWalletAddress(wallet_address):
    if isWalletAddress(wallet_address) is False:
        #print("No Tezos wallet address exists with this input")
        return False
    elif wallet_address is False:
        #print("No Tezos domain/Twitter address exists for this input")
        return False
    else: return True

def recognize_user_input(user_input):
    #user_input=str(input("Please enter your tezos wallet/domain or twitter address: "))
    if len(user_input) == 36 and user_input.startswith("tz"):
        return isWalletAddress(user_input)
    elif user_input.endswith(".tez"):
        return findWalletAddress_byTezDomain(user_input)
    elif user_input:
        return findWalletAddress_byTwitter(user_input)
    else: return False

st.write(recognize_user_input(st_user_input))

counter_N=[0]
def creator_allCreated_NFTs(wallet_address):
    if counter_N[0]>0:global nft_pk_val
    if counter_N[0]==0:nft_pk_val=0
    creator_allNFTs_pk_query="""query{
        listing(where: {token: {creators: {creator_address: {_eq: "wallet_address"}, token_pk: {_gt: "nft_pk_val"}}}}, distinct_on: token_pk) {
            token_pk
            timestamp
        }
    }"""
    creator_allNFTs_pk_query = creator_allNFTs_pk_query.replace("nft_pk_val",str(nft_pk_val))
    creator_allNFTs_pk_query = creator_allNFTs_pk_query.replace("wallet_address",str(wallet_address))

    creator_allNFTs_pk = requests.post(api_endpoint, json={'query': creator_allNFTs_pk_query})
    creator_allNFTs_pk = json.loads(creator_allNFTs_pk.text)
    creator_allNFTs_pk = creator_allNFTs_pk['data']['listing']

    # start the mechanism if there are 500 responses
    # otherwise, it is nonsense to wait executing all because one request is enough to get all data
    if len(creator_allNFTs_pk)==500:
        if counter_N[0]>0:
            global creators_allNFTs_pk_df
            global loop_of_allNFT_listings_df
        if counter_N[0]==0:
            creators_allNFTs_pk_df=pd.DataFrame()
            loop_of_allNFT_listings_df=pd.DataFrame()
        loop_of_allNFT_listings_df=pd.DataFrame(creator_allNFTs_pk)
        creators_allNFTs_pk_df=pd.concat([creators_allNFTs_pk_df,loop_of_allNFT_listings_df])
    else:creators_allNFTs_pk_df = pd.DataFrame(creator_allNFTs_pk)

    # there may be multiple listings on primary, so drop duplicates
    creators_allNFTs_pk_df = creators_allNFTs_pk_df.drop_duplicates()
    # convert timestamp attribute data type as date
    creators_allNFTs_pk_df['timestamp']=pd.to_datetime(creators_allNFTs_pk_df['timestamp']).dt.date
    creators_allNFTs_pk_df=creators_allNFTs_pk_df.sort_values(by='timestamp',ascending=True)
    # have to set index again after dropping and sorting operation
    creators_allNFTs_pk_df = creators_allNFTs_pk_df.reset_index()
    del creators_allNFTs_pk_df['index']

    counter_N[0]=+1  # increase counter after each iteration of the function
    if len(creators_allNFTs_pk_df)==500:
        nft_pk_val=str(creators_allNFTs_pk_df['token_pk'][499])
        return creator_allCreated_NFTs(wallet_address)
    else:
        counter_N[0]=0
        return creators_allNFTs_pk_df

def creator_availablePrimary_NFTs(wallet_address):
    if isAvailableWalletAddress(wallet_address) is not True:
        print("You entered unregistered input. Please enter an available wallet address, tezos domain or registered twitter address with your objkt.com profile.")
        return          # to prevent executing rest of the function
    if counter_N[0]>0:global nft_primaryKey_val
    if counter_N[0]==0:nft_primaryKey_val=0
    creator_nft_primaryNFT_info_query="""{
        listing(where: {seller_address: {_eq: "wallet_address"}, status: {_eq: "active"}, token: {creators: {creator_address: {_eq: "wallet_address"}, token_pk: {_gt: "nft_primaryKey_val"}}}}) {
            token_pk
        }
        }
        """
    creator_nft_primaryNFT_info_query = creator_nft_primaryNFT_info_query.replace("nft_primaryKey_val",str(nft_primaryKey_val))
    creator_nft_primaryNFT_info_query = creator_nft_primaryNFT_info_query.replace("wallet_address",str(wallet_address))

    creator_primary_nft_pk = requests.post(api_endpoint, json={'query': creator_nft_primaryNFT_info_query})
    creator_primary_nft_pk = json.loads(creator_primary_nft_pk.text)
    creator_primary_nft_pk = creator_primary_nft_pk['data']['listing']

    # start the mechanism if there are 500 responses
    # otherwise, it is nonsense to wait executing all because one request is enough to get all data
    if len(creator_primary_nft_pk)==500:
        if counter_N[0]>0:
            global creators_availablePrimaryNFTs_pk_df
            global loop_ofPrimary_NFT_listings_df
        if counter_N[0]==0:
            creators_availablePrimaryNFTs_pk_df=pd.DataFrame()
            loop_ofPrimary_NFT_listings_df=pd.DataFrame()
        loop_ofPrimary_NFT_listings_df=pd.DataFrame(creator_primary_nft_pk)
        creators_availablePrimaryNFTs_pk_df=pd.concat([creators_availablePrimaryNFTs_pk_df,loop_ofPrimary_NFT_listings_df])

    else:creators_availablePrimaryNFTs_pk_df = pd.DataFrame(creator_primary_nft_pk)

    # there may be multiple listings on primary, so delete duplicates
    creators_availablePrimaryNFTs_pk_df = creators_availablePrimaryNFTs_pk_df.drop_duplicates()
    creators_availablePrimaryNFTs_pk_df = creators_availablePrimaryNFTs_pk_df.reset_index()     # have to set index again after dropping operation
    del creators_availablePrimaryNFTs_pk_df['index']

    counter_N[0]=+1
    if len(creators_availablePrimaryNFTs_pk_df)==500:
        nft_primaryKey_val=str(creators_availablePrimaryNFTs_pk_df['token_pk'][499])
        return creator_availablePrimary_NFTs(wallet_address)
    else:
        counter_N[0]=0
        return creators_availablePrimaryNFTs_pk_df

def creator_all_NFT_sales(wallet_address):
    if isAvailableWalletAddress(wallet_address) is not True:
        print("You entered unregistered input. Please enter an available wallet address, tezos domain or registered twitter address with your objkt.com profile.")
        return          # to prevent executing rest of the function
    if counter_N[0]>0:global nft_timestamp_val
    if counter_N[0]==0:nft_timestamp_val="2000-01-01T00:00:00+00:00" # initialize the timestamp value
    creator_all_sales_query="""query{
    listing_sale(where: {token: {creators: {creator_address: {_eq: "wallet_address"}}}, timestamp: {_gt: "nft_timestamp_val"}}, distinct_on: timestamp) {
        token_pk
        timestamp
        }
    }"""
    creator_all_sales_query = creator_all_sales_query.replace("nft_timestamp_val",str(nft_timestamp_val))
    creator_all_sales_query = creator_all_sales_query.replace("wallet_address",str(wallet_address))
    creator_all_sales_response= requests.post(api_endpoint, json={'query': creator_all_sales_query})
    creator_all_sales_response = json.loads(creator_all_sales_response.text)
    creator_all_sales_response = creator_all_sales_response['data']['listing_sale']

    if counter_N[0]>0:
        global all_NFT_sales_df
        global loop_NFT_sales_df
    if counter_N[0]==0:
        all_NFT_sales_df=pd.DataFrame()
        loop_NFT_sales_df=pd.DataFrame()

    loop_NFT_sales_df = pd.DataFrame(creator_all_sales_response)
    loop_NFT_sales_df['token_pk']=loop_NFT_sales_df['token_pk'].astype(int)

    all_NFT_sales_df=pd.concat([ all_NFT_sales_df,loop_NFT_sales_df])
    counter_N[0]+=1

    # print(nft_timestamp_val)    # to check how it works

    if len(creator_all_sales_response)==500:  # max retrieves are 500, if less there are no more data to response from api
        nft_timestamp_val=str(loop_NFT_sales_df['timestamp'][499])
        return creator_all_NFT_sales(wallet_address)
    else:
        counter_N[0]=0                     # reset counter in the end
        all_NFT_sales_df=all_NFT_sales_df.reset_index()
        del all_NFT_sales_df['index']      # also reset index, sufficient for the multiple request cases
        return all_NFT_sales_df

def creator_primary_NFT_sales(wallet_address):
    if counter_N[0]>0:global nft_timestamp_val
    if counter_N[0]==0:nft_timestamp_val="2000-01-01T00:00:00+00:00" # initialize the timestamp value
    creator_all_sales_query="""{
    listing_sale(where: {token: {creators: {creator_address: {_eq: "wallet_address"}}}, timestamp: {_gt: "nft_timestamp_val"}, seller_address: {_eq: "wallet_address"}}, distinct_on: timestamp) {
        price
        token_pk
        buyer_address
        timestamp
        }
    }"""
    creator_all_sales_query = creator_all_sales_query.replace("nft_timestamp_val",str(nft_timestamp_val))
    creator_all_sales_query = creator_all_sales_query.replace("wallet_address",str(wallet_address))
    creator_all_sales_response= requests.post(api_endpoint, json={'query': creator_all_sales_query})
    creator_all_sales_response = json.loads(creator_all_sales_response.text)
    creator_all_sales_response = creator_all_sales_response['data']['listing_sale']

    if counter_N[0]>0:
        global all_NFT_sales_df
        global loop_NFT_sales_df
    if counter_N[0]==0:
        all_NFT_sales_df=pd.DataFrame()
        loop_NFT_sales_df=pd.DataFrame()

    loop_NFT_sales_df = pd.DataFrame(creator_all_sales_response)
    loop_NFT_sales_df['token_pk']=loop_NFT_sales_df['token_pk'].astype(int)

    all_NFT_sales_df=pd.concat([ all_NFT_sales_df,loop_NFT_sales_df])
    counter_N[0]+=1

    if len(creator_all_sales_response)==500:  # max retrieves are 500, if less there are no more data to response from api
        nft_timestamp_val=str(loop_NFT_sales_df['timestamp'][499])
        return creator_primary_NFT_sales(wallet_address)
    else:
        counter_N[0]=0                     # reset counter in the end
        #all_NFT_sales_df=all_NFT_sales_df.reset_index()
        #del all_NFT_sales_df['index']      # also reset index, sufficient for the multiple request cases
        return all_NFT_sales_df

def creator_primary_sales_df(wallet_address):
    creator_primary_sales_dataFrame=creator_primary_NFT_sales(wallet_address)

    # manipulating price column to calculate exact value [as tezos] of a token
    # dividing to 10^6
    creator_primary_sales_dataFrame['price']=pd.to_numeric(creator_primary_sales_dataFrame['price'],downcast="float")
    creator_primary_sales_dataFrame['price']=creator_primary_sales_dataFrame['price']/1000000
    # manipulate timestamp attribute data type as date
    creator_primary_sales_dataFrame['timestamp']=pd.to_datetime(creator_primary_sales_dataFrame['timestamp']).dt.date
    # convert all days to 1 for grouping by year-month
    # ...this line will enable to fill missing months on data frame
    creator_primary_sales_dataFrame['timestamp']=creator_primary_sales_dataFrame['timestamp'].apply(lambda dt: dt.replace(day=1))

    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.groupby('timestamp').sum()
    del creator_primary_sales_dataFrame['token_pk']

    # evaluating a solution to obtain missing month(s) between year and month
    firstMintDate_ofCreator=creator_allCreated_NFTs(wallet_address)        # assign data frame of all NFTs of the creator
    firstMintDate_ofCreator=firstMintDate_ofCreator.loc[0]['timestamp']    # then assign first NFT's time to the variable
    firstMintDate_ofCreator=firstMintDate_ofCreator.strftime('%Y-%m')      # drop day from the date
    # define a range to fill missing months in data frame
    sale_date_range = pd.date_range(
                            start=firstMintDate_ofCreator,                 # using the variable for calculating minting range
                            end=creator_primary_sales_dataFrame.index[len(creator_primary_sales_dataFrame)-1]).to_period('m')

    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.reset_index()           # convert to data frame from pivot table
    creator_primary_sales_dataFrame['timestamp'] = creator_primary_sales_dataFrame['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.set_index('timestamp')  # then set date as index

    #...there is missing part right here...
    #...fill the data frame with missing months in case they exist
    #...but this code fills all values
    #creator_primary_sales_dataFrame=creator_primary_sales_dataFrame.reindex(sale_date_range,fill_value=0)

    return creator_primary_sales_dataFrame                                             # return the data frame

st.write(creator_primary_sales_df(recognize_user_input(st_user_input)))

def visualized_creator_primary_sales(wallet_address):
    if isAvailableWalletAddress(wallet_address) is not True:
        print("You entered unregistered input. Please enter an available wallet address, tezos domain or registered twitter address with your objkt.com profile.")
        return         # to prevent executing rest of the function
    dataFrame_toPlot=creator_primary_sales_df(wallet_address)
    # use pandas data frame plot to visualize the data
    dataFrame_toPlot.plot(kind='bar',title=f"Revenue of the Artist {wallet_address} on Primary Market by Month",xlabel="Month",ylabel="Revenue (by Tezos)")
