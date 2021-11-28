import json
import base58
from solana.keypair import Keypair
from solana.rpc.api import Client
from metaplex.metadata import get_metadata
from cryptography.fernet import Fernet
import api.metaplex_api as metaplex_api
import argparse


def parse_commandline_arguments():

    global divinity_json_file

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     description='Specify the json file')

    parser.add_argument("-j", "--jsonf", dest="jsonf",
                        type=str, help="Specify the json file from https://arweave.net")
    
    args = parser.parse_args()
    divinity_json_file = str(args.jsonf)

if __name__ == '__main__':
    parse_commandline_arguments()

    if (divinity_json_file):

        text_file = open("/Users/BedrosovaYulia/.config/solana/id.json", "r")
        lines = text_file.read()[1:-1].split(',')
        key_from_file = [int(x) for x in lines]

        keypair = Keypair(key_from_file[:32])
        print(keypair.public_key)
        cfg = {
                "PRIVATE_KEY": base58.b58encode(keypair.seed).decode("ascii"),
                "PUBLIC_KEY": str(keypair.public_key),
                "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
            }
        api = metaplex_api.MetaplexAPI(cfg)

        api_endpoint = "https://api.devnet.solana.com/"

        # requires a JSON file with metadata. best to publish on Arweave
        #divinity_json_file = "https://arweave.net/KMqr5IowiHhfxhd_Yo1y6tnF2cc6sryeD3cU9IIxpFk"
        print(divinity_json_file)
        # deploy a contract. will return a contract key.
    
        #print(api.wallet())
        print("Deploy:")
        result = api.deploy(api_endpoint, "Test NFT deploy", "TNF", fees=300)
        print("Deploy completed. Result: %s",result)

        print("Load contract key:")
        contract_key = json.loads(result).get('contract')
        print("Contract key loaded. Conract key: %s", contract_key)
        print("Mint:")
        # conduct a mint, and send to a recipient, e.g. wallet_2
        mint_res = api.mint(api_endpoint, contract_key, keypair.public_key, divinity_json_file)
        print("Mint completed. Result: %s", mint_res)

    else:
        print("Specify the json file from https://arweave.net")
