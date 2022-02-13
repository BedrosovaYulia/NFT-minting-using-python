import json
import base58
from solana.keypair import Keypair
from solana.rpc.api import Client
from metaplex.metadata import get_metadata
from cryptography.fernet import Fernet
import api.metaplex_api as metaplex_api

import boto3
import base64
from botocore.exceptions import ClientError
import datetime
import time



def get_secret(secret_name,region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        print("Can't find solana secret key")
        raise e
    else:
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret 
            
    


def lambda_handler(event, context):
    
    key=event['Records'][0]['s3']['object']['key']
    
    if (key):

        secret = json.loads(get_secret("solana","us-east-1"))['solana_key'];
        #print(secret)
        
        lines = secret.split(',')
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
    
        
        # deploy a contract. will return a contract key.
        
        now = datetime.datetime.now()
        
        json_file_template={
            "name": "Bedrosova"+now.strftime("%H-%M-%S"),
            "description": "Yuliya Bedrosova Test NFT from AWS Lambda",
            "seller_fee_basis_points": 500,
            "image": "https://solana-nft-minter.s3.amazonaws.com/"+str(key),
            "collection": {
                "name": "Bedrosova Test NFT from AWS Lambda",
                "family": "Bedrosova Test NFT"
            },
            "properties": {
                "files": [
                    {
                        "uri": "https://solana-nft-minter.s3.amazonaws.com/"+str(key),
                        "type": "image/jpg"
                    }
                ],
                "category": "image",
                "creators": [
                    {
                        "address": str(keypair.public_key),
                        "share": 100
                    }
                ]
            }
        }
        
        s3_client = boto3.client('s3')
        bucket_name = "solana-nft-minter"
    
        
        response = s3_client.put_object(
            ACL='public-read',
            Body=json.dumps(json_file_template, indent=2),
            ContentType='application/json',
            Bucket=bucket_name,
            Key="json/test-nft-"+now.strftime("%d-%m-%Y-%H-%M-%S")+".json",
        )

        if(response):
            print("Deploy:")
            result = api.deploy(api_endpoint, "TestNFT", "TNF", fees=300)
            print("Deploy completed. Result: %s",result)
            print("Load contract key:")
            contract_key = json.loads(result).get('contract')
            print("Contract key loaded. Conract key: %s", contract_key)
            print("Mint:")
            # conduct a mint, and send to a recipient, e.g. wallet_2
            divinity_json_file="https://solana-nft-minter.s3.amazonaws.com/json/test-nft-"+now.strftime("%d-%m-%Y-%H-%M-%S")+".json"
            print(api_endpoint, contract_key, keypair.public_key,divinity_json_file)
            
            try:
                mint_res = api.mint(api_endpoint, contract_key, keypair.public_key,divinity_json_file)
                print("Mint completed. Result: %s", mint_res)
            except:
                print("try to mint another time:")
                #time.sleep(60)
                mint_res = api.mint(api_endpoint, contract_key, keypair.public_key,divinity_json_file)
                print("Mint completed. Result: %s", mint_res)

    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
