# NFT-CollaBot

NFT CollaBot is a data-oriented project designed by the requirements of NFT ecosystem and aims to strengthen community. Targets to perform visual statistics for artists and collectors on Tezos ecosystem. Designed and evaluated by Emirhan Serveren and offered to every member of the ecosystem as an open-source project.

## OUTCOMES
* Requirement Analysis
* Glosarry for non-NFT audience
* How to Read Code?

## REQUIREMENT ANALYSIS

Data expertise is widely used solutions in digital age. Many decision-makers applies data-oriented solutions to optimize their business performance. As a data professional and NFT artist on Tezos ecosystem, noticed requirements of NFT artists. There are hundreds of NFT artists who make their living with this NFTs. They are consuming too much effort for keeping track of their sale performances. It is approximately impossible to chase data on rapid NFT ecosystem. Talented developer [@NFTBiker](http://nftbiker.xyz) has accurate solution for this case. In this sense, decided to bring a value to ecosystem like this generous people. To provide a value, proposed a design that contains visual charts for Tezos NFT community that describes the story behind their NFT Journey.

## GLOSARRY

There are many terms that thoough to identify their meanings and usage if yuo are not familiar with NFT Community before. Most of the terms are similar for NFT artists and collectors but not for the newbies on the community. Main goal is to document glosarry to evaluate a beginner guide for the newcomers of Tezos NFT ecosystem.

|Term|Description|API Meaning|
|--|--|--|
|Mint| | |
|List|NFT Creators mostly chooses to list their NFTs after minting to perform sales. They are enabled to define number of the editions to mint with an amount by Tezos. Also, all owners of a NFT have access to list the relevant NFT.|listing|
|Edition(s)|NFT Creators are able to mint their NFTs whether a single edition or multiple editions. This feature provides the opportunity of achieving multiple collectors in a single work or specializing it.|Supply|
|Sale|Selling a NFT is the key part of the business of NFT artists. The sale operation is performed as swapping a NFT with an amount of Tezos. Buyer side gives the tezos and owns the NFT. Seller side gains an amount as Tezos by swapping his/her NFT.|listing_sale|
|Primary|A sale can be performed in two ways: Primary or Secondary. Primary sale means the sale of a NFT from creators itself to a collector. If a NFT artist achieves a sale that he/she minted, then it is called as a primary sale.| seller_address,_eq|
|Secondary| Secondary sale is a term stands for sales from a non-creator seller to a buyer. If the seller side is not the creator of this NFT, then it is a secondary sale. | seller_address,_neq|
|Sold Out|This is a common word between NFT Creators to celebrate that they have sold all of the editions of a NFT in primary market. | |
|Burning Edition(s)|NFT Creators applies to burn an edition/multiple editions of a NFT for several cases. They mostly announce this operation on Twitter like *"Burning Remaining Editions on Saturday"*. They perform the burning operation on objkt.com with **Burn Token**. It is crucial to know that burning NFT editions are kind of *sending*  operation. You are sending burned edition(s) to *tz1burnburnburnburnburnburnburjAYjjX* to complete the operation after you are clicking *Burn Token*.| *tz1burnburnburnburnburnburnburjAYjjX* tezos address is shown on **holders**|
|Owners|NFTs are owned and collected by wallet adress(es). These are shown as **Owners** in the objkt.com UI. NFT Creator is automatically an owner of the NFT after a mint operation. Additionally, a NFT collector is able to own a NFT after buying it.|Holders|

## MILESTONES

There are many achievements of NFT CollaBot. To accomplish, it is inevitable to approach with an agile strategy. I have spotted milestones to complete objectives step by step. Objectives as:

>Completed
* Understanding objkt.com API *-Glosarry on Readme File*
* Creating Modules to Extract and Analyze Data *-Jupyter Notebook*
>In Progress
* Deploying on [Streamlit](https://emirhanserveren-nft-collabot-deploy-mml6j8.streamlitapp.com/) *-deploy.py script*
>Future Objective
* Deploying on Discord 
* Deploying on Twitter

## HOW NFT COLLABOT WORKS?

It is significant to percieve how NFT CollaBot interacts with the users. NFT CollaBot has designed as an initial-term user interaction. The software product that provides statistics as a result of an input.

> **HOW STREAMLIT WORKS?**

In Streamlit, NFT CollaBot only contains an input component that asks for the user's Tezos wallet address/domain or registered Twitter username to give an output.

TezosDomainAsInput
    participant NFT CollaBot
    participant User
    NFT CollaBot->>User: Please enter your Tezos Wallet Address/Domain or Twitter Username registered to your Tezos Profile:
    User-->>NFT CollaBot: mytezosdomain.tez
    Alice-)John: **data table about mydomain.tez primary sales over months**

## HOW TO READ CODE?

There are two files that constructs the development:
* main.ipynb : contains all of the modules with their descriptions, *kind of test environment*. Most comprehensive file about the development phase.
* deploy.py : contains the script that live on streamlit, *kind of prod environment*

### deploy.py

The script is constructed with function method. There are functions that invoked depending on each other. It is impossible to get insight into the code without understanding how functions work.

|**function name**|**technical description**|**dependent function(s)**|**category**|**user-level explanation**|
|:-:|--|--|:-:|--|
|check_API_launch_datetime()| NFT Marketplace objkt.com's API is going to move on version 3 endpoint on 30-Jan-2023 <br /> the script checks for the current API endpoint |- | API-Related | - |
|findWalletAddress_byTwitter(twitter_address)|  | | Input Handling | Enables users to ask their statistics by using their twitter username registered to their tezos profile as an input |
|findWalletAddress_byTezDomain(tezos_domain)| | | Input Handling | Enables users to ask their statistics by using their tezos domain as an input |
|isWalletAddress(wallet_address)| Requests to [tzkt.io](https://tzkt.io/) API endpoint using the user input and checks is there any wallet address matches on Tezos ecosystem with this input | - | Input Handling |The platform warns the users for the wrong inputs|
|isAvailableWalletAddress(wallet_address) | | isWalletAddress()| Input Handling | |
|recognize_user_input(user_input) | | isWalletAddress(), findWalletAddress_byTwitter(), findWalletAddress_byTezDomain()| Input Handling |Identifies user's input type|
|creator_all_NFT_sales(wallet_address)| | |  Token Trade | |
|creator_availablePrimary_NFTs(wallet_address)| |  |Token Mint | |
|creator_primary_NFT_sales(wallet_address) | Requests data from API <br /> related to primary sales of the questioned NFT creator. The NFT Creator's wallet address informations is passed as an argument on the function. | |  Token Trade |  |
|creator_primary_sales_df(wallet_address) | Performs data cleaning and analysis in the function for evaluating an output. |creator_primary_NFT_sales() | Token Trade | |










