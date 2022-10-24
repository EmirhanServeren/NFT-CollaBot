# NFT-CollaBot

NFT CollaBot is a data-oriented project designed by the requirements of NFT ecosystem and aims to strengthen community. Targets to perform visual statistics for artists and collectors on Tezos ecosystem. Designed and evaluated by Emirhan Serveren and offered to every member of the ecosystem as an open-source project.

## OUTCOMES
* Requirement Analysis
* Glosarry for non-NFT audience
* How to Read Code?

## REQUIREMENT ANALYSIS

Data expertise is widely used solutions in digital age. Many decision-makers applies data-oriented solutions to optimize their business performance. As a data professional and NFT artist on Tezos ecosystem, noticed requirements of NFT artists. There are hundreds of NFT artists who make their living with this NFTs. They are consuming too much effort for keeping track of their sale performances. It is approximately impossible to chase data on rapid NFT ecosystem. Talented developer [@NFTBiker](http://nftbiker.xyz) has accurate solution for this case. In this sense, decided to bring a value to ecosystem like this generous people. To provide a value, proposed a design that contains visual charts for Tezos NFT community that describes the story behind their NFT Journey.

## GLOSARRY

There are many terms that thoough to identify their meanings and usage. Most of the terms are similar for NFT artists and collectors but not for the newbies on the community. Main goal is to document glosarry to evaluate a beginner guide for the newcomers of Tezos NFT ecosystem.

|Term|Description|API Meaning|
|--|--|--|
|Mint| | |
|List|NFT Creators mostly chooses to list their NFTs after minting to perform sales. They are enabled to define number of the editions to mint with an amount by Tezos. Also, all owners of a NFT have access to list the relevant NFT.|listing|
|Edition(s)|NFT Creators are able to mint their NFTs whether a single edition or multiple editions. This feature provides the opportunity of achieving multiple collectors in a single work or specializing it.|Supply|
|Sale|Selling a NFT is the key part of the business of NFT artists. The sale operation is performed as swapping a NFT with an amount of Tezos. Buyer side gives the tezos and owns the NFT. Seller side gains an amount as Tezos by swapping his/her NFT.|listing_sale|
|Primary|A sale can be performed in two ways: Primary or Secondary. Primary sale means the sale of a NFT from creators itself to a collector. If a NFT artist achieves a sale that he/she minted, then it is called as a primary sale.| owner_address,_eq|
|Secondary| Secondary sale is a term stands for sales from a non-creator seller to a buyer. If the seller side is not the creator of this NFT, then it is a secondary sale. | owner_address,_neq|
|Sold Out|This is a common word between NFT Creators to celebrate that they have sold all of the editions of a NFT in primary market. | |
|Gifting an NFT|||
|Burning Edition(s)|NFT Creators applies to burn an edition/multiple editions of a NFT for several cases. They mostly announce this operation on Twitter like *"Burning Remaining Editions on Saturday"*. They perform the burning operation on objkt.com with **Burn Token**. It is crucial to know that burning NFT editions are kind of *sending*  operation. You are sending burned edition(s) to *tz1burnburnburnburnburnburnburjAYjjX* to complete the operation after you are clicking *Burn Token*.| *tz1burnburnburnburnburnburnburjAYjjX* tezos address is shown on **holders**|
|Owners|NFTs are owned and collected by wallet adress(es). These are shown as **Owners** in the objkt.com UI. NFT Creator is automatically an owner of the NFT after a mint operation. Additionally, a NFT collector is able to own a NFT after buying it.|Holders|

## HOW TO READ CODE?



