# NFT-minting-using-python
Minting Solana NFT using candy-machine-cli is quite expensive, so I searched and I have found a cheaper option: it is 20% cheaper!!!

Using:

arweave deploy --key-file /Users/BedrosovaYulia/Documents/Projects/metaplex-api/python-api/arweave-keyfile-rpLKsmy-xTFUyFezwRi3vQWuHghA96cuWbAkLhpRtbY.json /Users/BedrosovaYulia/Documents/Projects/metaplex-api/python-api/images/bedrosova1.png

arweave deploy --key-file /Users/BedrosovaYulia/Documents/Projects/metaplex-api/python-api/arweave-keyfile-rpLKsmy-xTFUyFezwRi3vQWuHghA96cuWbAkLhpRtbY.json /Users/BedrosovaYulia/Documents/Projects/metaplex-api/python-api/images/bedrosova-test-nft-1.json

python3 mint.py -j 'https://arweave.net/S0Eo5QsC2yS9svD7denUaYa36JvSxYFAG9D4DwxUWGE'

You can put these commands in the pipeline and use them for your NFT batch generation.
