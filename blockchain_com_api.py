import requests
from typing import List, Any

class BlockChainAPI:
    """BlockChain Data API documentation:
    https://www.blockchain.com/explorer/api/blockchain_api

    Single Block:
        {
        "hash": "0000000000000bae09a7a393a8acded75aa67e46cb81f7acaa5ad94f9eacd103",
        "ver": 1,
        "prev_block": "00000000000007d0f98d9edca880a6c124e25095712df8952e0439ac7409738a",
        "mrkl_root": "935aa0ed2e29a4b81e0c995c39e06995ecce7ddbebb26ed32d550a72e8200bf5",
        "time": 1322131230,
        "bits": 437129626,
        "nonce": 2964215930,
        "n_tx": 22,
        "size": 9195,
        "block_index": 818044,
        "main_chain": true,
        "height": 154595,
        "received_time": 1322131301,
        "relayed_by": "108.60.208.156",
        "tx": [
            "--Array of Transactions--"
        ]
        }
    """
    def __init__(self):
        pass

    def valid_btc_address(self, btc_address: str) -> bool:
        url = f'https://blockchain.info/rawaddr/{btc_address}'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"Successfully validated BTC address '{btc_address}'")
                return True
            else:
                print(f"Received non-200 status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Could not make request to validate BTC address: {e}")
            return False

    def get_data(self, btc_address: str) -> List[Any]:
        url = f'https://blockchain.info/rawaddr/{btc_address}'
        try:
            response = requests.get(url)
            data = response.json()
            return data
        except Exception as e:
            print(f"Could not get data: {e}")
    
    def get_balance(self, btc_address: str) -> float:
        """
        Given a BTC address, get balance

        Returns:
            BTC address balance in float format
        """
        try:
            #balance = data['final_balance'] / 100000000 # Conversion of Satoshi into 
            data = self.get_data(btc_address)
            balance = data['final_balance']
            print(f"Final balance for address '{btc_address}': {balance} BTC")
            return balance
        except Exception as e:
            print(f"Failed to get balance for btc_address '{btc_address}': \n {e}")