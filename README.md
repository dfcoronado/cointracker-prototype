# CoinTracker (prototype)

A prototype (web app) of CoinTacker with 3 main core functionalities:
- Add/Remove bitcoin addresses
- Synchronize bitcoin wallet transactions for the addresses
- Retrieve the current balances and transactions for each bitcoin address


## Project Structure:
- database.py: Contains classes to set up and use DynamoDB tables.
- app.py: Main Flask application for user interaction.
- blockchain_com_api.py: Module for interacting with the Blockchain.com API.
- main.py: Utility functions for managing Bitcoin addresses and transactions.
- test.py: Unit tests for database and API functionalities.

## Installation


Download repository to local machine:
```bash
git clone https://github.com/dfcoronado/cointracker-prototype/
```

## Setup Environment: AWS Account and Dependencies

- AWS account: Set up a free AWS account `https://aws.amazon.com` if you don't have any. Ensure you have the necessary permissions to create and manage AWS resources.

- Set up the appropriate credentials to use AWS. 
  - *After creating AWS account, sign into AWS Management Console `https://aws.amazon.com/console/`
  - *Navigate to IAM (Identitiy and Access Management) service
  - *Create an IAM user with programatic access. Ensure to save the `Access Key ID` and `Secret Access Key` securely.
  - *DynamoDB permissions: There exists a file `dynamodb_permisions.json` in the **resources** directory. You can simply copy and paste them for your user.
    - *In IAM console, select your IAM user, and attach this policy under ` "Permissions" -> "Add permissions" -> "Attach policies directly."
- Install AWS CLi and Configure:
```bash 
# For Linux/macOS
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```
- Configure AWS CLI with IAM user credentials
  - *in terminal `aws configure`
    - ```bash
          AWS Access Key ID: YOUR_ACCESS_KEY_ID
          AWS Secret Access Key: YOUR_SECRET_ACCESS_KEY 
          Default region name: YOUR_AWS_REGION #'us-east-1'
          Default output format: json

      ```
    - Save your config file.

- Install Dependencies: `requirement.txt`
```bash
pip install -r requirements.txt
```

## Usage

* Database Setup: 
Run the following command to set up the database tables (DynamoDB):

```bash
python database.py
```

## Running Application
Run the following command in the project directory to run the application:

```bash
python app.py
```

- The terminal should specify where the server is: ```http://127.0.0.1:5000```
- In the application interface you should be able to:
  - Register/Login
  - Add/Remove BTC addresses
  - Check transactions for your BTC addresses
  - Check BTC balances and all latest transactions

### Usage Instructions:
* Note these instructions are mainly to explain the code, you can use app interface to do everything non-programatically as long as the environment is set up correctly.
1. Adding Users:
Use the application interface to add new users by providing a username and password.
2. Managing Bitcoin Addresses:
Use `BitcoinAddresses` class methods (add_address, remove_address, get_btc_addresses_for_user) to manage Bitcoin addresses associated with users.
3. Synchronizing Bitcoin Transactions:
Use `SynchronizeBitcoinAddress` class methods (add_transactions, get_transactions_table_for_btc_address) to synchronize and retrieve Bitcoin transactions.
4. Retrieving Data:
Use `RetrieveData` class methods (get_current_balance, get_total_amount, number_of_btc_addreses_owned, get_btc_and_balance_data, get_btc_transactions) to retrieve and analyze Bitcoin data.

## Contact

Feel free to `dfecoronado@gmail.com` if you have any questions.