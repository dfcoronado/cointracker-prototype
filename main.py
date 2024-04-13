# main.py
from database import *
from blockchain_com_api import BlockChainAPI
from typing import List, Any

class BitcoinAddresses:
    """ 
    Requirement: Add/Remove bitcoin addresses
    Add and Remove Bitcoin Addresses given a BTC address
    """
    def __init__(self):
        self.btc_balances_db = BTCBalancesDB()
        self.btc_addresses_for_user = []
    
    def add_address(self, btc_address: str, username: str):
        """
        Add valid BTC address to BTCBalances DB

        Args:
            btc_address: valid BTC address
        """
        return self.btc_balances_db.add_item(btc_address, username)
        
    def remove_address(self, btc_address: str):
        """
        Remove valid BTC address to BTCBalances DB

        Args:
            btc_address: valid BTC address
        """
        return self.btc_balances_db.remove_item(btc_address)

    def get_btc_addresses_for_user(self, username: str):
        """
        Fetch all BTC address from BTCBalances DB for username
        """
        return self.btc_balances_db.get_btc_addresses_for_user(username)

class SynchronizeBitcoinAddress:
    """
    Requirement: Synchronize bitcoin wallet transactions for the addresses
    Show all BTC Address and their corresponding transaction real-time
    Show:
        * BTC transactions corresponding to each address (real-time)
        * BTC balance for each address (NOT REQUIRED)
        * Total balance for all addreses (NOT REQUIRED)
        * More?
    """
    def __init__(self):
        self.blockchain_api = BlockChainAPI()
        self.transactions_db = TransactionsDB()

    def add_transactions(self, username: str, btc_address: str) -> bool:
        """
        Add transactions to the TransactionsDB table.
        We only care for this purpose on timestamp, balance, and fee

        Args:
            username: the current logged in username
            btc_address: a valid btc address that the username owns
        
        Returns:
            True if adding transaction is sucessful else false
        """
        if self.blockchain_api.valid_btc_address(btc_address):
            data = self.blockchain_api.get_data(btc_address)
            if 'txs' in data:
                txs_data_len = len(data['txs'])
                num_of_transactions = 10 # We are only recording 10 transactions for testing purposes
                # TODO: if you want to see more/less transactions please refer to this logic
                print(f"Total length of transactions: {txs_data_len}")
                
                for i in range(min(num_of_transactions, txs_data_len)):
                    if 'time' in data['txs'][i] and 'balance' in data['txs'][i] and 'fee' in data['txs'][i]:
                        t_time = data['txs'][i]['time']
                        t_balance = data['txs'][i]['balance']
                        t_fee = data['txs'][i]['fee']
                        self.transactions_db.add_transaction(username, i+1, btc_address, t_time, t_fee, t_balance)
                    else:
                        print(f"Insufficient data at {i}th instance.")
                        break
            else:
                print(f"Insufficient data.")
                return False
        return True

    def get_transactions_table_for_btc_address(self, btc_address: str) -> List[Any]:
        """
        Get a list of transactions corresponding to the btc_address.

        Args:
            btc_address: a valid btc address string.
        
        Returns:
            A  list of transactions for the valid btc_address.
        """
        transactions_table = self.transactions_db.get_table(btc_address)
        transactions_list = []
        satoshi = float(100000000)
        for transaction in transactions_table:
            time = transaction['time']
            balance = transaction['balance']
            balance = round(int(balance)/satoshi, 10)
            fee = transaction['fee']
            fee = round(int(fee)/satoshi,10)
            transactions_list.append({'timestamp':time, 'balance': balance, 'fee': fee})
        return transactions_list

class RetrieveData():
    """
    Retrieve the current balances and transactions for each btc address
    """
    def __init__(self):
        self.blockchain_api = BlockChainAPI()
        self.sync = SynchronizeBitcoinAddress()
    
    def get_current_balance(self, btc_address: str) -> float:
        """
        Get current balance for the given btc_address.

        Args:
            btc_address: a valid btc address in string format.

        Returns:
            An amount in float format corresponding to the balance in BTC for the given address.
        """
        satoshi = 100000000
        current_balance = self.blockchain_api.get_balance(btc_address)
        return round(int(current_balance)/satoshi,10)
    
    def get_total_amount(self, btc_addresses: List[str]) -> float:
        """
        Get total amount of BTC owned between all wallets.
        """
        total_btc_owned = 0.0
        for btc_addr in btc_addresses:
            total_btc_owned += self.get_current_balance(btc_addr)
        return total_btc_owned
    
    def number_of_btc_addreses_owned(self, btc_addresses):
        """
        Get the number of BTC addresses own
        """
        return len(btc_addresses)
    
    def get_btc_and_balance_data(self, btc_addresses: List[str]) -> List[Any]:
        """
        Geta List of btc_address and corresponding balance for the btc address.
        """
        btc_addresses_data = []
        for btc_addr in btc_addresses:
            current_balance = self.get_current_balance(btc_addr)
            btc_addresses_data.append({'btc_address': btc_addr, 'current_balance': current_balance})
        return btc_addresses_data
    
    def get_btc_transactions(self, btc_addresses: List[str]) -> List[Any]:
        btc_transactions = []
        for btc_address in btc_addresses:
            transactions_for_btc_address = self.sync.get_transactions_table_for_btc_address(btc_address)
            for transaction in transactions_for_btc_address:
                btc_transactions.append({
                    'btc_address': btc_address,
                    'current_balance': transaction['balance'],
                    'fee': transaction['fee'],
                    'timestamp': transaction['timestamp']
                })
        # Sort transactions by timestamp (latest first)
        btc_transactions = sorted(btc_transactions, key=lambda x: x['timestamp'], reverse=True)
        return btc_transactions