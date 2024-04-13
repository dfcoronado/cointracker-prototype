# database.py
from typing import List, Any
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timezone
from blockchain_com_api import BlockChainAPI
from decimal import Decimal
import hashlib

# Create Tables
class DDBTable:
    def __init__(self, table_name: str, partition_key: str):
        self.client = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_name = table_name
        self.partition_key = partition_key

        if not self.table_exists(self.table_name):
            self.create_table(self.table_name, self.partition_key)
        else:
            print(f"Table '{self.table_name}' already exists.")

    def table_exists(self, table_name: str) -> bool:
        """
        Check if a DynamoDB table already exists.

        Args:
            table_name: Name of the table to check.

        Returns:
            True if the table exists, False otherwise.
        """
        try:
            self.client.Table(table_name).load()
            return True
        except self.client.meta.client.exceptions.ResourceNotFoundException:
            return False

    def create_table(self, table_name: str, partition_key: str) -> None:
        """
        Create DDB table.

        Args:
            table_name: name of the new table.
            partition_key: partition key for the new table.
        Returns:
            Create new table in DynamoDB.
        """
        try:
            response = self.client.create_table(
                TableName=table_name,
                KeySchema=[
                    {
                        'AttributeName': partition_key,
                        'KeyType': 'HASH' # Partition key
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': partition_key,
                        'AttributeType': 'S' # string
                    },
                    # 
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 10,  # Adjust based on your read requirements
                    'WriteCapacityUnits': 10  # Adjust based on your write requirements
                }
            )
            print(f"Table {self.table_name} created successfully!")
        except Exception as e:
            print(f"Error creating table: {e}")


# UsersDB
class UsersDB(DDBTable):
    def __init__(self):
        self.client = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_name = 'users'
        self.table = self.client.Table(self.table_name)
        print(f"DDB table '{self.table_name}' succesfully initialized.")

    def add_user(self, username: str, password: str) -> bool:
        """
        Adds a new username if it does not exist.
        Args:
            username: a new username in str format.
            password: a password corresponding to the username.

        Returns:
            True if add_user operation succesful else False.
        """
        created_time_utc = datetime.now(timezone.utc).isoformat()
        try:
            encrypted_password = password.encode('utf-8')
            encrypted_password = hashlib.sha256(encrypted_password).hexdigest()

            self.table.put_item(
                Item={
                    'username': username,
                    'password': password,
                    'encrypted_password': encrypted_password,
                    'time_registered': created_time_utc,
                }
            )
            print(f"User '{username}' succesfully added to the database.")
            return True
        except Exception as e:
            print(f"Failed to add user '{username}': {e}")
            return False
    
    def get_user(self, username: str) -> dict:  
        """
        Retrieve user information from the database by username
        Args:
            username: input in str format
        Returns:
            dictionary with username information
        """     
        try:
            response = self.table.get_item(
                Key={
                    'username': username
                }
            )
            if 'Item' in response:
                return response['Item']
            else:
                return None
        except Exception as e:
            print(f"Error attempting to retrieve username '{username}: {e}")
            return None

# BTCBalancesDB 
class BTCBalancesDB:
    def __init__(self):
        self.client = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_name = 'btc_balances'
        self.table = self.client.Table(self.table_name)
        print(f"BTC database table '{self.table_name}' succesfully initialized.")
        self.blockchain_api = BlockChainAPI()
        
    # TODO: Finish this table
    def get_table(self) -> List[dict]:
        """
        Get BTC DynamoDB Table.
        Returns:
            A list of dictionary containing elements in the BTC table.
        """
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            return items
            # while 'LastEvaluatedKey' in response:
            #     response = self.table.scan(ExclusveStartKey=response['LastEvaluatedKey'])
            #     items = response.get('Items', [])
            #     for item in items:
            #         print(item)
        except Exception as e:
            print(f"Failed to obtain table {self.table.name}: {e}")

    def add_item(self, btc_address: str, username: str) -> bool:
        """
        Adds an entry to the BTC Balances table.

        Args:
            btc_address: a valid bitcoin address in str format.
            username: a valid username in int format.

        Returns:
            True if operation succesful else False.
        """
        created_time_utc = datetime.now(timezone.utc).isoformat()
        try:
            if self.blockchain_api.valid_btc_address(btc_address): # check that it is a valid BTC address
                btc_balance = self.blockchain_api.get_balance(btc_address)
                if not btc_balance: btc_balance = 0
                self.table.put_item(
                    Item={
                        'btc_address': btc_address,
                        'username': username,
                        'time_added': created_time_utc,
                        'btc_balance': btc_balance, #Decimal(btc_balance),
                    }
                )
                print(f"Item with btc_address '{btc_address}' added succesfully to the '{self.table_name}' DB.")
                return True
        except Exception as e:
            print(f"Failed to add btc_address '{btc_address}': {e}")
            return False

    def remove_item(self, btc_address: str) -> bool:
        """
        Removes an entry to the BTCBalances table.
        
        Args:
            btc_address: a valid bitcoin address in str format.

        Returns:
            True if operation succesful else False.
        """
        try:
            if self.blockchain_api.valid_btc_address(btc_address):
                response = self.table.delete_item(
                    Key={
                        'btc_address':btc_address
                    }
                )

                if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                    print(f"Item with btc_address '{btc_address}' removed successfully from '{self.table_name}' DB.")
                    return True
                else: 
                    print(f"Failed to remove item with btc_address '{btc_address}'. Unexpected response.")
                    return False
        except Exception as e:
            print("Failed to remove item with btc_address '{btc_address}' : {e}")
            return False
        
    def get_btc_addresses_for_user(self, username: int) -> set:
        """Fetches BTC Addresses linked with a user id
        
        Args:
            username: a valid username in int format

        Returns:
            A set of all the BTC addresses linked to the username input.
        """
        try:
            response = self.table.scan()
            btc_addreses = set()
            for item in response['Items']:
                if 'username' in item and item['username'] == username:
                    btc_addr = item['btc_address']
                    btc_addreses.add(btc_addr)
            print(f"All btc_address associated with username '{username}': \n '{btc_addreses}'")
            return btc_addreses
        except Exception as e:
            print(f"Failed to retrieve btc addresses for username '{username}': {e}")
            return []


# TransactionsDB
class TransactionsDB:
    def __init__(self):
        self.client = boto3.resource('dynamodb', region_name='us-east-1')
        self.table_name = 'transactions'
        self.table = self.client.Table(self.table_name)
        print(f"Transactions database table '{self.table_name}' succesfully initialized.")
        self.blockchain_api = BlockChainAPI()

    def add_transaction(self, username: str, ith: int, btc_address: str, timestamp: int, fee: int, balance: int) -> bool:
        """Adds an entry to the BTC table.

        Args:
            btc_address: a valid bitcoin address in str format.
            username: a valid username in int format.

        Returns:
            True if operation succesful else False.
        """
        try:
            # unique identifier - partition key
            modified_btc_address = username + str(ith) + btc_address
            print(f"Modified btc address: '{modified_btc_address}'.")

            # modify time
            utc_datetime = datetime.utcfromtimestamp(timestamp)
            utc_datetime_str = utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
            
            self.table.put_item(
                Item={
                    'modified_btc_address': modified_btc_address,
                    'btc_address': btc_address,
                    'time': utc_datetime_str,
                    'balance': balance,
                    'fee': fee,
                }
            )
            print(f"Item with btc_address '{btc_address}' added succesfully to '{self.table_name}' DB.")
            return True
        except Exception as e:
            print(f"Failed to add transaction btc_address {btc_address}: {e}")
            return False
        
    def get_table(self, btc_address: str, num_of_items:int = 20) -> List[dict] :
        """Get BTC DynamoDB Table
        Returns:
            A list of dictionary containing elements in the BTC table.
        """
        try:
            response = self.table.scan(
                FilterExpression=Key('btc_address').eq(btc_address)
            )
            items = response.get('Items', [])
            len_items = len(items)
            print(len_items)       
            len_items = min(len_items, num_of_items)
            print(len_items)
            return items[:len_items]
        except Exception as e:
            print(f"Failed to obtain table {self.table_name}: {e}")
            return []
        
def main():
    # ---------------------------------------------------- #
    #   Create Tables                                      #
    # ---------------------------------------------------- #
    # Create 'users' DDB table
    table_name = 'users'
    partition_key = 'username'
    print("\n")
    print(DDBTable(table_name, partition_key))
    print("\n")

    # Create 'btc_balances' DDB table
    table_name = 'btc_balances'
    partition_key = 'btc_address'
    print("\n")
    print(DDBTable(table_name, partition_key))
    print("\n")

    # Create 'transactions' DDB table
    table_name = 'transactions'
    partition_key = 'modified_btc_address'
    print("\n")
    print(DDBTable(table_name, partition_key))
    print("\n")

if __name__ == "__main__":
    main()