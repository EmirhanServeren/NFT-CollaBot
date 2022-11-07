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
    creator_walletAddress_byTwitter_query="""query MyQuery {
    token_creator(
        where: {holder: {twitter: {_eq: "twitter_address"}}}){
        holder {
        address
        }
        }
    }
    """
    evaluated_twitterAddress = f"https://twitter.com/{str(twitter_address)}"    # query requires full link of the address
    creator_walletAddress_byTwitter_query = creator_walletAddress_byTwitter_query.replace("twitter_address",evaluated_twitterAddress)

    creator_twitter = requests.post(api_endpoint, json={'query': creator_walletAddress_byTwitter_query})
    creator_twitter = json.loads(creator_twitter.text)
    creator_twitter = creator_twitter ['data']['token_creator']
    if creator_twitter == [] or creator_twitter[0]['holder'] == "null":
        st.write("There are no Tezos profiles registered with this username. Please enter an input again<3")
    twitter_username=creator_twitter[0]['holder']
    return list(twitter_username.values())[0]

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
    else: st.write("Unavailable Tezos Domain. Please enter an input again<3")

def isWalletAddress(wallet_address):
    account_data_url=f"https://api.tzkt.io/v1/accounts/{wallet_address}" # tzkt.io API endpoint
    response = requests.get(account_data_url)
    with contextlib.suppress(KeyError or json.decoder.JSONDecodeError):
        response=response.json()
        if response['type']!="empty":
            return wallet_address
        else: st.write("Unavailable tezos wallet address. Please enter an input again<3")

def recognize_user_input(user_input):
    if len(user_input) == 36 and user_input.startswith("tz"):
        return isWalletAddress(user_input)
    elif user_input.endswith(".tez"):
        return findWalletAddress_byTezDomain(user_input)
    elif user_input:
        return findWalletAddress_byTwitter(user_input)

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
    creator_primary_sales_query="""{
    listing_sale(where: {token: {creators: {creator_address: {_eq: "wallet_address"}}}, timestamp: {_gt: "nft_timestamp_val"}, seller_address: {_eq: "wallet_address"}}, distinct_on: timestamp) {
        price
        token_pk
        buyer_address
        timestamp
        }
    }"""
    creator_primary_sales_query = creator_primary_sales_query.replace("nft_timestamp_val",str(nft_timestamp_val))
    creator_primary_sales_query = creator_primary_sales_query.replace("wallet_address",str(wallet_address))
    creator_primary_sales_response= requests.post(api_endpoint, json={'query': creator_primary_sales_query})
    creator_primary_sales_response = json.loads(creator_primary_sales_response.text)
    creator_primary_sales_response = creator_primary_sales_response['data']['listing_sale']

    if counter_N[0]>0:
        global all_NFT_sales_df
        global loop_NFT_sales_df
    if counter_N[0]==0:
        all_NFT_sales_df=pd.DataFrame()
        loop_NFT_sales_df=pd.DataFrame()

    loop_NFT_sales_df = pd.DataFrame(creator_primary_sales_response)
    loop_NFT_sales_df['token_pk']=loop_NFT_sales_df['token_pk'].astype(int)

    all_NFT_sales_df=pd.concat([ all_NFT_sales_df,loop_NFT_sales_df])
    counter_N[0]+=1

    if len(creator_primary_sales_response)==500:  # max retrieves are 500, if less there are no more data to response from api
        nft_timestamp_val=str(loop_NFT_sales_df['timestamp'][499])
        return creator_primary_NFT_sales(wallet_address)
    else:
        counter_N[0]=0                # reset counter in the end
        return all_NFT_sales_df

# find the first mint date of a creator and return as year-month format
# will be using on multiple functions, creator_primary_sales_df() as well
def find_first_minting_date(wallet_address):
    firstMintDate_ofCreator=creator_allCreated_NFTs(wallet_address)        # assign data frame of all NFTs of the creator
    firstMintDate_ofCreator=firstMintDate_ofCreator.loc[0]['timestamp']    # then assign first NFT's time to the variable
    firstMintDate_ofCreator=firstMintDate_ofCreator.strftime('%Y-%m')      # drop day from the date
    return firstMintDate_ofCreator

# spotting the latest's date in year-month format
def find_last_sale_date(wallet_address):
    last_sale_date=creator_all_NFT_sales(wallet_address)
    last_sale_date=last_sale_date.apply(pd.to_datetime)
    last_sale_date=last_sale_date.loc[len(last_sale_date)-1]['timestamp']
    last_sale_date=last_sale_date.strftime('%Y-%m')
    return last_sale_date

def creator_primary_sales_df(wallet_address):
    creator_primary_sales_dataFrame=creator_primary_NFT_sales(wallet_address)

    # manipulating price column to calculate exact value [as tezos] of a token
    # dividing to 10^6
    creator_primary_sales_dataFrame['price']=pd.to_numeric(creator_primary_sales_dataFrame['price'],downcast="float")
    creator_primary_sales_dataFrame['price']=creator_primary_sales_dataFrame['price']/1000000
    # manipulate timestamp attribute data type as date
    creator_primary_sales_dataFrame['timestamp']=pd.to_datetime(creator_primary_sales_dataFrame['timestamp']).dt.date
    # convert all days to 1 for grouping by year-month pair
    creator_primary_sales_dataFrame['timestamp']=creator_primary_sales_dataFrame['timestamp'].apply(lambda dt: dt.replace(day=1))

    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.groupby('timestamp').sum()
    del creator_primary_sales_dataFrame['token_pk']

    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.reset_index()           # convert to data frame from pivot table
    creator_primary_sales_dataFrame['timestamp'] = creator_primary_sales_dataFrame['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.set_index('timestamp')  # then set date as index

    firstMintDate_ofCreator=find_first_minting_date(wallet_address)
    lastSaleDate_ofCreator=find_last_sale_date(wallet_address)
    def date_range_df(firstMintDate_ofCreator):
        # define a range to fill missing months -if exists- in data frame
        sale_date_range = pd.date_range(
                            start=firstMintDate_ofCreator,         # using the variable for calculating minting range
                            end=lastSaleDate_ofCreator).to_period('m')
        # create a data frame to save all of the months in the range
        sale_date_range=pd.DataFrame(sale_date_range)
        sale_date_range=sale_date_range.drop_duplicates(keep="first")
        sale_date_range['price']= 0
        sale_date_range=sale_date_range.rename(columns={0:'timestamp'})
        sale_date_range['timestamp'] = sale_date_range['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
        sale_date_range=sale_date_range.groupby('timestamp').sum()
        return sale_date_range

    creator_primary_sales=date_range_df(firstMintDate_ofCreator)    # assign the data frame returned from the function

    creator_primary_sales=creator_primary_sales.reset_index()       # then reset index before mapping
    creator_primary_sales_dataFrame=creator_primary_sales_dataFrame.reset_index()

    # use mapping to fill new data frame with values, keep NaN non-existing months on actual data frame
    creator_primary_sales['price']=creator_primary_sales['timestamp'].map(creator_primary_sales_dataFrame.set_index('timestamp')['price'])
    creator_primary_sales=creator_primary_sales.fillna(0)

    return creator_primary_sales.set_index('timestamp')

def creator_secondary_NFT_sales_tokens(wallet_address):
    if counter_N[0]>0:global nft_timestamp_val
    if counter_N[0]==0:nft_timestamp_val="2000-01-01T00:00:00+00:00" # initialize the timestamp value
    creator_secondary_sales_query="""{
    listing_sale(where: {token: {creators: {creator_address: {_eq: "wallet_address"}}}, timestamp: {_gt: "nft_timestamp_val"}, seller_address: {_neq: "wallet_address"}}, distinct_on: timestamp) {
        price
        token_pk
        buyer_address
        timestamp
        }
    }"""

    def send_request_sales(query_input):                 # the function is too complicated so wanted to minimize using a function
        query_input = query_input.replace("nft_timestamp_val",str(nft_timestamp_val))
        query_input = query_input.replace("wallet_address",str(wallet_address))

        global response          # avoid UnboundLocal Error
        response = requests.post(api_endpoint, json={'query': query_input})
        response = json.loads(response.text)
        response = response['data']['listing_sale']
        return response

    creator_secondary_sales_response=send_request_sales(creator_secondary_sales_query)

    if counter_N[0]>0:
        global all_secondaryNFT_sales_df
        global loop_secondaryNFT_sales_df
    if counter_N[0]==0:
        all_secondaryNFT_sales_df=pd.DataFrame()
        loop_secondaryNFT_sales_df=pd.DataFrame()

    loop_secondaryNFT_sales_df = pd.DataFrame(creator_secondary_sales_response)
    loop_secondaryNFT_sales_df['token_pk']=loop_secondaryNFT_sales_df['token_pk'].astype(int)
    loop_secondaryNFT_sales_df['price']=loop_secondaryNFT_sales_df['price'].astype(int)
    # loop data frame saves the data for each iteration of the recursive algorithm, it is temporary data source...
    # data frame starts with "all" includes all of the retrieved data, it is permanent data frame that loop data frame transports data
    all_secondaryNFT_sales_df=pd.concat([ all_secondaryNFT_sales_df,loop_secondaryNFT_sales_df])

    counter_N[0]+=1
    if len(creator_secondary_sales_response)==500:  # max retrieves are 500, if less there are no more data to response from api
        nft_timestamp_val=str(loop_secondaryNFT_sales_df['timestamp'][499])
        return creator_secondary_NFT_sales_tokens(wallet_address)
    else:
        counter_N[0]=0
        return all_secondaryNFT_sales_df

def creator_secondary_NFT_sales_royalties(wallet_address):
    if counter_N[0]>0:global nft_timestamp_val
    if counter_N[0]==0:nft_timestamp_val="2000-01-01T00:00:00+00:00" # initialize the timestamp value
    creator_secondary_sales_royalties_query="""{
    listing_sale(where: {token: {creators: {creator_address: {_eq: "wallet_address"}}}, timestamp: {_gt: "nft_timestamp_val"}, seller_address: {_neq: "wallet_address"}}, distinct_on: timestamp) {
        token {
        royalties {
            amount
            }
        }
        timestamp
    }
    }"""
    def send_request(query_input):                 # the function is too complicated so wanted to minimize using a function
        query_input = query_input.replace("nft_timestamp_val",str(nft_timestamp_val))
        query_input = query_input.replace("wallet_address",str(wallet_address))

        global response          # avoid UnboundLocal Error
        response = requests.post(api_endpoint, json={'query': query_input})
        response = json.loads(response.text)
        response = response['data']['listing_sale']
        return response

    response=send_request(creator_secondary_sales_royalties_query)

    if counter_N[0]>0:
        global all_secondaryNFT_sales_df
        global loop_secondaryNFT_sales_df
    if counter_N[0]==0:
        all_secondaryNFT_sales_df=pd.DataFrame()
        loop_secondaryNFT_sales_df=pd.DataFrame()

    loop_secondaryNFT_sales_df = pd.DataFrame(response)
    # loop data frame saves the data for each iteration of the recursive algorithm, it is temporary data source...
    # data frame starts with "all" includes all of the retrieved data, it is permanent data frame that loop data frame transports data
    all_secondaryNFT_sales_df=pd.concat([ all_secondaryNFT_sales_df,loop_secondaryNFT_sales_df])

    def clean_data(df):
        df['token'] = df['token'].astype(str)
        df['token'] = df['token'].str.replace(r"[a-zA-Z]",'')
        df['token'] = df['token'].str.replace(f'[{string.punctuation}]', '')
        # avoid errors in collaboration cases (in collabs there are multiple royalties. need only 1st)
        df['token'] = [x[:5] for x in df['token']]
        # available to convert numerical data type after necessary operations are implemented
        df['token'] = df['token'].astype(int)
        df['token'] = df['token']/10    # manipulate into exact value
        return df

    clean_data(all_secondaryNFT_sales_df)

    counter_N[0]+=1
    if len(response)==500:  # max retrieves are 500, if less there are no more data to response from api
        nft_timestamp_val=str(loop_secondaryNFT_sales_df['timestamp'][499])
        return creator_secondary_NFT_sales_royalties(wallet_address)
    else:
        counter_N[0]=0
        return all_secondaryNFT_sales_df

def creator_secondary_NFT_sales(wallet_address):
    royalties_df=creator_secondary_NFT_sales_royalties(wallet_address)
    tokens_df=creator_secondary_NFT_sales_tokens(wallet_address)

    secondary_sales_df = pd.concat([tokens_df,royalties_df], axis=1, join="inner")
    secondary_sales_df['artist_income'] = ""                                        # create a new column to save calculated value
    secondary_sales_df = secondary_sales_df.rename(columns={'token':'royalties'})   # rename to understand purpose of the attribute better
    secondary_sales_df['artist_income'] = (secondary_sales_df[["price", "royalties"]].product(axis=1))
    secondary_sales_df['artist_income'] = secondary_sales_df['artist_income']/100000000

    # drop duplicate 'timestamp' column from the data frame
    secondary_sales_df = secondary_sales_df.loc[:,~secondary_sales_df.T.duplicated(keep='last')]

    return secondary_sales_df

def creator_secondary_sales_df(wallet_address):
    secondary_sales_df=creator_secondary_NFT_sales(wallet_address)
    secondary_sales_df=secondary_sales_df[['timestamp','artist_income']]    # keep only these two columns

    # manipulate timestamp attribute data type as date
    secondary_sales_df['timestamp'] = pd.to_datetime(secondary_sales_df['timestamp']).dt.date
    secondary_sales_df['timestamp'] = secondary_sales_df['timestamp'].apply(lambda dt: dt.replace(day=1))
    secondary_sales_df['timestamp'] = secondary_sales_df['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
    secondary_sales_df = secondary_sales_df.groupby('timestamp').sum()

    firstMintDate_ofCreator=find_first_minting_date(wallet_address)
    lastSaleDate_ofCreator=find_last_sale_date(wallet_address)
    def date_range_df(firstMintDate_ofCreator):
        sale_date_range = pd.date_range(
                            start=firstMintDate_ofCreator,
                            end=lastSaleDate_ofCreator).to_period('m')
        sale_date_range=pd.DataFrame(sale_date_range)
        sale_date_range=sale_date_range.drop_duplicates(keep="first")
        sale_date_range['artist_income']= 0
        sale_date_range=sale_date_range.rename(columns={0:'timestamp'})
        sale_date_range['timestamp'] = sale_date_range['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
        sale_date_range=sale_date_range.groupby('timestamp').sum()
        return sale_date_range
    creator_secondary_sales=date_range_df(firstMintDate_ofCreator)    # assign the data frame returned from the function

    creator_secondary_sales = creator_secondary_sales.reset_index()   # then reset index before mapping
    secondary_sales_df = secondary_sales_df.reset_index()

    # use mapping to fill new data frame with values, keep NaN non-existing months on actual data frame
    creator_secondary_sales['artist_income'] = creator_secondary_sales['timestamp'].map(secondary_sales_df.set_index('timestamp')['artist_income'])
    creator_secondary_sales = creator_secondary_sales.fillna(0)

    return creator_secondary_sales.set_index('timestamp')

def creator_all_sales_df(wallet_address):
    primary_df = creator_primary_sales_df(wallet_address)
    secondary_df = creator_secondary_sales_df(wallet_address)

    primary_df=primary_df.rename(columns={'price':'primary_income'})
    secondary_df=secondary_df.rename(columns={'artist_income':'secondary_income'})

    return pd.concat([primary_df,secondary_df],axis=1)

def creator_primarySales_byEditions_df(wallet_address):
    creator_primary_sales_dataFrame=creator_primary_NFT_sales(wallet_address)

    # deleting unnecessary attributes from data frame
    del creator_primary_sales_dataFrame['buyer_address']
    del creator_primary_sales_dataFrame['price']

    # manipulate timestamp attribute data type as date
    creator_primary_sales_dataFrame['timestamp']=pd.to_datetime(creator_primary_sales_dataFrame['timestamp']).dt.date
    creator_primary_sales_dataFrame['timestamp']=creator_primary_sales_dataFrame['timestamp'].apply(lambda dt: dt.replace(day=1))
    creator_primary_sales_dataFrame['timestamp']=creator_primary_sales_dataFrame['timestamp'].apply(lambda x: x.strftime('%Y-%m'))

    creator_primary_sales_dataFrame = creator_primary_sales_dataFrame.groupby('timestamp').count()

    # implementing the same algorithm with the function above to fill missing months, in case they exist
    firstMintDate_ofCreator=creator_allCreated_NFTs(wallet_address)
    firstMintDate_ofCreator=firstMintDate_ofCreator.loc[0]['timestamp']
    firstMintDate_ofCreator=firstMintDate_ofCreator.strftime('%Y-%m')

    def date_range_df(firstMintDate_ofCreator):
        sale_date_range = pd.date_range(
                            start=firstMintDate_ofCreator,
                            end=creator_primary_sales_dataFrame.index[len(creator_primary_sales_dataFrame)-1]).to_period('m')
        sale_date_range=pd.DataFrame(sale_date_range)
        sale_date_range=sale_date_range.drop_duplicates(keep="first")
        sale_date_range['token_pk']= 0
        sale_date_range=sale_date_range.rename(columns={0:'timestamp'})
        sale_date_range['timestamp'] = sale_date_range['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
        sale_date_range=sale_date_range.groupby('timestamp').sum()
        return sale_date_range

    creator_primary_sales=date_range_df(firstMintDate_ofCreator)

    creator_primary_sales=creator_primary_sales.reset_index()
    creator_primary_sales_dataFrame=creator_primary_sales_dataFrame.reset_index()

    creator_primary_sales['token_pk']=creator_primary_sales['timestamp'].map(creator_primary_sales_dataFrame.set_index('timestamp')['token_pk'])
    creator_primary_sales=creator_primary_sales.fillna(0)

    creator_primary_sales['token_pk']=creator_primary_sales['token_pk'].astype(int)
    creator_primary_sales=creator_primary_sales.rename(columns={'token_pk':'sold_editions'})

    return creator_primary_sales

def creator_secondarySales_byEditions_df(wallet_address):
    creator_secondary_sales_dataFrame=creator_secondary_NFT_sales(wallet_address)

    # deleting unnecessary attributes from data frame
    del creator_secondary_sales_dataFrame['buyer_address']
    del creator_secondary_sales_dataFrame['price']

    # manipulate timestamp attribute data type as date
    creator_secondary_sales_dataFrame['timestamp'] = pd.to_datetime(creator_secondary_sales_dataFrame['timestamp']).dt.date
    creator_secondary_sales_dataFrame['timestamp'] = creator_secondary_sales_dataFrame['timestamp'].apply(lambda dt: dt.replace(day=1))
    creator_secondary_sales_dataFrame['timestamp'] = creator_secondary_sales_dataFrame['timestamp'].apply(lambda x: x.strftime('%Y-%m'))

    creator_secondary_sales_dataFrame = creator_secondary_sales_dataFrame.groupby('timestamp').count()

    # implementing the same algorithm with the function above to fill missing months, in case they exist
    firstMintDate_ofCreator=creator_allCreated_NFTs(wallet_address)
    firstMintDate_ofCreator=firstMintDate_ofCreator.loc[0]['timestamp']
    firstMintDate_ofCreator=firstMintDate_ofCreator.strftime('%Y-%m')

    def date_range_df(firstMintDate_ofCreator):
        sale_date_range = pd.date_range(
                            start=firstMintDate_ofCreator,
                        end=creator_secondary_sales_dataFrame.index[len(creator_secondary_sales_dataFrame)-1]).to_period('m')
        sale_date_range=pd.DataFrame(sale_date_range)
        sale_date_range=sale_date_range.drop_duplicates(keep="first")
        sale_date_range['token_pk']= 0
        sale_date_range=sale_date_range.rename(columns={0:'timestamp'})
        sale_date_range['timestamp'] = sale_date_range['timestamp'].apply(lambda x: x.strftime('%Y-%m'))
        sale_date_range=sale_date_range.groupby('timestamp').sum()
        return sale_date_range

    creator_secondary_sales=date_range_df(firstMintDate_ofCreator)

    creator_secondary_sales=creator_secondary_sales.reset_index()
    creator_secondary_sales_dataFrame=creator_secondary_sales_dataFrame.reset_index()

    creator_secondary_sales['token_pk']=creator_secondary_sales['timestamp'].map(creator_secondary_sales_dataFrame.set_index('timestamp')['token_pk'])
    creator_secondary_sales=creator_secondary_sales.fillna(0)

    creator_secondary_sales['token_pk']=creator_secondary_sales['token_pk'].astype(int)
    creator_secondary_sales=creator_secondary_sales.rename(columns={'token_pk':'sold_editions'})

    return creator_secondary_sales

def creator_all_sales_byEditions_df(wallet_address):
    primary_df = creator_primarySales_byEditions_df(wallet_address)
    secondary_df = creator_secondarySales_byEditions_df(wallet_address)

    primary_df=primary_df.set_index('timestamp')
    secondary_df=secondary_df.set_index('timestamp')

    primary_df=primary_df.rename(columns={'sold_editions':'sold_editions_onPrimary'})
    secondary_df=secondary_df.rename(columns={'sold_editions':'sold_editions_onSecondary'})

    all_sales_byEditions_df=pd.concat([primary_df,secondary_df],axis=1)
    # there may na values can occur after merging, so implement filling NA and astype modules
    all_sales_byEditions_df=all_sales_byEditions_df.fillna(0)
    all_sales_byEditions_df['sold_editions_onPrimary']=all_sales_byEditions_df['sold_editions_onPrimary'].astype(int)
    all_sales_byEditions_df['sold_editions_onSecondary']=all_sales_byEditions_df['sold_editions_onSecondary'].astype(int)

    return all_sales_byEditions_df

# create sidebar and other sub-page components here
st.sidebar.write("NFT CollaBot is a data-oriented project designed by the requirements of NFT ecosystem and aims to strengthen community.")
page_column_1,page_column_2=st.columns(2)

# the part where NFT CollaBot responds to user with an output
with contextlib.suppress(KeyError):
    if recognize_user_input(st_user_input) is False:
        recognize_user_input(st_user_input)
    else:
        page_column_1.bar_chart(creator_all_sales_df(recognize_user_input(st_user_input)))
        page_column_1.dataframe(creator_all_sales_df(recognize_user_input(st_user_input)))

        page_column_2.line_chart(creator_all_sales_byEditions_df(recognize_user_input(st_user_input)))
        page_column_2.dataframe(creator_all_sales_byEditions_df(recognize_user_input(st_user_input)))
