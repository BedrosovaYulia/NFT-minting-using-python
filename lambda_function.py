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


def get_secret(secret_name):

    #secret_name = "solana"
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        print(get_secret_value_response)
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            return decoded_binary_secret 
            
    


def lambda_handler(event, context):
    
    divinity_json_file = "https://arweave.net/KMqr5IowiHhfxhd_Yo1y6tnF2cc6sryeD3cU9IIxpFk"

    if (divinity_json_file):

        secret = json.loads(get_secret("solana"))['solana_key'];
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
    
        # requires a JSON file with metadata. best to publish on Arweave
        print(divinity_json_file)
        # deploy a contract. will return a contract key.
        
        #print(api.wallet())
        print("Deploy:")
        result = api.deploy(api_endpoint, "Test NFT deploy 2", "TNF", fees=300)
        print("Deploy completed. Result: %s",result)
    
        print("Load contract key:")
        contract_key = json.loads(result).get('contract')
        print("Contract key loaded. Conract key: %s", contract_key)
        print("Mint:")
        # conduct a mint, and send to a recipient, e.g. wallet_2
        mint_res = api.mint(api_endpoint, contract_key, keypair.public_key, divinity_json_file)
        print("Mint completed. Result: %s", mint_res)

    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
