import unittest
from unittest.mock import patch
from blockchain_com_api import BlockChainAPI
from database import UsersDB, BTCBalancesDB, TransactionsDB
from main import BitcoinAddresses, SynchronizeBitcoinAddress, RetrieveData

# ---------------- #
# datbase.py TESTS #
# ---------------- #
class TestUsersDB(unittest.TestCase):
    def test_add_user(self):
        # Test adding a user
        username = "daniel"
        password = "cointracker_pw"
        users_db = UsersDB()
        result = users_db.add_user(username, password)
        self.assertTrue(result)

    def test_get_user(self):
        # Test getting a user
        username = "daniel"
        users_db = UsersDB()
        user_info = users_db.get_user(username)
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], username)

class TestBTCBalancesDB(unittest.TestCase):
    def test_add_item(self):
        # Test adding items to BTCBalancesDB
        btc_balances_db = BTCBalancesDB()

        btc_address1 = "Randomaddresses"  # Random non valid address
        btc_address2 = "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo"  # Binance's address
        btc_address3 = "1NhJGUJu8rrTwPS4vopsdTqqcK4nAwdLwJ"  # Random address - call it satoshi's

        # Add items
        result1 = btc_balances_db.add_item(btc_address1, "satoshi")
        result2 = btc_balances_db.add_item(btc_address2, "binance")
        result3 = btc_balances_db.add_item(btc_address3, "satoshi")

        self.assertFalse(result1)
        self.assertTrue(result2)
        self.assertTrue(result3)

    def test_get_btc_addresses_for_user(self):
        # Test getting BTC addresses for a user
        btc_balances_db = BTCBalancesDB()
        addresses = btc_balances_db.get_btc_addresses_for_user("satoshi")
        self.assertIsInstance(addresses, set)

    def test_remove_item(self):
        # Test removing an item from BTCBalancesDB
        btc_balances_db = BTCBalancesDB()
        btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Satoshi's address

        # Add an item first
        btc_balances_db.add_item(btc_address, "satoshi")

        # Remove the item
        result = btc_balances_db.remove_item(btc_address)
        self.assertTrue(result)

class TestTransactionsDB(unittest.TestCase):
    def test_add_transaction(self):
        # Test adding transactions to TransactionsDB
        transactions_db = TransactionsDB()
        blockchain_api = BlockChainAPI()

        btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"  # Satoshi's address
        username = "daniel"

        # Get blockchain data
        data = blockchain_api.get_data(btc_address)

        if 'txs' in data:
            # Add transactions
            for i, tx in enumerate(data['txs']):
                if 'time' in tx and 'balance' in tx and 'fee' in tx:
                    t_time = tx['time']
                    t_balance = tx['balance']
                    t_fee = tx['fee']
                    transactions_db.add_transaction(username, i + 1, btc_address, t_time, t_fee, t_balance)
                else:
                    print(f"Insufficient data at {i}th instance.")
                    break
        else:
            print(f"Insufficient data for address '{btc_address}'.")

        # Retrieve transactions and check
        transactions = transactions_db.get_table(btc_address=btc_address)
        self.assertTrue(len(transactions) > 0)

# ---------------#
# main.py TESTS  #
# ---------------#
class TestBitcoinAddresses(unittest.TestCase):
    def setUp(self):
        # Initialize test objects
        self.bitcoin_addresses = BitcoinAddresses()
        self.btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        self.username = "satoshi"

    def test_add_address(self):
        # Test adding a BTC address
        result = self.bitcoin_addresses.add_address(self.btc_address, self.username)
        self.assertTrue(result)

    def test_remove_address(self):
        # Test removing a BTC address
        # first added then remove it
        self.bitcoin_addresses.add_address(self.btc_address, self.username)
        result = self.bitcoin_addresses.remove_address(self.btc_address)
        self.assertTrue(result)

    def test_get_btc_addresses_for_user(self):
        # Test getting BTC addresses for a user
        addresses = self.bitcoin_addresses.get_btc_addresses_for_user(self.username)
        self.assertIsInstance(addresses, set)

class TestSynchronizeBitcoinAddress(unittest.TestCase):
    def setUp(self):
        # Initialize test objects
        self.sync_btc_address = SynchronizeBitcoinAddress()
        self.btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        self.username = "satoshi"

    def test_add_transactions(self):
        # Test adding transactions
        result = self.sync_btc_address.add_transactions(self.username, self.btc_address)
        self.assertTrue(result)

    def test_get_transactions_table_for_btc_address(self):
        # Test getting transactions table for a BTC address
        transactions = self.sync_btc_address.get_transactions_table_for_btc_address(self.btc_address)
        self.assertIsInstance(transactions, list)

class TestRetrieveData(unittest.TestCase):
    def setUp(self):
        # Initialize test objects
        self.retrieve_data = RetrieveData()
        self.btc_addresses = ["1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo"]

    def test_get_current_balance(self):
        # Test getting current balance for a BTC address
        current_balance = self.retrieve_data.get_current_balance(self.btc_addresses[0])
        self.assertIsInstance(current_balance, float)

    def test_get_total_amount(self):
        # Test getting total amount of BTC owned across addresses
        total_amount = self.retrieve_data.get_total_amount(self.btc_addresses)
        self.assertIsInstance(total_amount, float)

    def test_number_of_btc_addresses_owned(self):
        # Test getting the number of BTC addresses owned
        num_addresses = self.retrieve_data.number_of_btc_addreses_owned(self.btc_addresses)
        self.assertIsInstance(num_addresses, int)

    def test_get_btc_and_balance_data(self):
        # Test getting BTC addresses and corresponding balances
        btc_data = self.retrieve_data.get_btc_and_balance_data(self.btc_addresses)
        self.assertIsInstance(btc_data, list)
        self.assertEqual(len(btc_data), len(self.btc_addresses))

    def test_get_btc_transactions(self):
        # Test getting BTC transactions
        btc_transactions = self.retrieve_data.get_btc_transactions(self.btc_addresses)
        self.assertIsInstance(btc_transactions, list)

# --------------------------- #
# blockchain_com_api.py TESTS #
# --------------------------- #
class TestBlockChainAPI(unittest.TestCase):
    def setUp(self):
        self.blockchain_api = BlockChainAPI()

    def test_valid_btc_address_valid(self):
        btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        self.assertTrue(self.blockchain_api.valid_btc_address(btc_address))

    def test_valid_btc_address_invalid(self):
        non_valid_btc_address = "invalidaddress"
        self.assertFalse(self.blockchain_api.valid_btc_address(non_valid_btc_address))

    @patch('blockchain_com_api.BlockChainAPI.get_data')
    def test_get_balance(self, mock_get_data):
        btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        mock_get_data.return_value = {'final_balance': 100000000}  # Mock data for testing

        expected_balance = 100000000 # 100000000 Satoshi = 1 BTC
        actual_balance = self.blockchain_api.get_balance(btc_address)
        self.assertEqual(actual_balance, expected_balance)

    def test_get_balance_exception(self):
        btc_address = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"
        # Simulate exception when retrieving data
        with patch('blockchain_com_api.BlockChainAPI.get_data', side_effect=Exception('Mocked exception')):
            balance = self.blockchain_api.get_balance(btc_address)

        self.assertIsNone(balance)

if __name__ == '__main__':
    unittest.main()