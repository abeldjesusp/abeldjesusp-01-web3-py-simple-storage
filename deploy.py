from solcx import compile_standard, install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()


# Compile Our Solidity
install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        'language': 'Solidity',
        'sources': { 'SimpleStorage.sol': { 'content': simple_storage_file } },
        'settings': {
            'outputSelection': {
                '*': {
                    '*': [ 'abi', 'metadata', 'evm.bytecode', 'evm.sourceMap' ]
                }
            }
        }
    },
    solc_version='0.6.0'
)

with open('compiled_code.json', 'w') as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['evm']['bytecode']['object']

# get abi
abi = compiled_sol['contracts']['SimpleStorage.sol']['SimpleStorage']['abi']

# for connecting to Rinkeby
w3 = Web3(Web3.HTTPProvider('https://rinkeby.infura.io/v3/09df4ed93a474d61b148592ca42f3254'))
chain_id = 4
my_address = '0xB1248FB3b43F46921b7F8c222D27e8309D803B0F'
private_key =  os.getenv('PRIVATE_KEY') # in python private keys must start with 0x

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the lastest transacction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
transaction = SimpleStorage.constructor().buildTransaction({
    "gasPrice": w3.eth.gas_price, 
    'chainId': chain_id,
    'from': my_address,
    'nonce': nonce
})

# 2. Sign a transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

# 3. Send a transaction
print('(+) Deploying contract...')
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print('(+) Deployed!')

# Working with the contract, you always need 
# Contract address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())
print('(+) Updating contract...')
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "gasPrice": w3.eth.gas_price,
    'chainId': chain_id,
    'from': my_address,
    'nonce': nonce + 1
})
signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction);
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print('(+) Updated!')
print(simple_storage.functions.retrieve().call())