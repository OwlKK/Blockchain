import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
import base64

from argparse import ArgumentParser


class Blockchain:
    # Initialize the blockchain with an empty chain, no transactions, and an empty node set
    # Start the blockchain with the genesis block
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash="1", pow=100)

    # Register a new node (a peer) by adding its address to the node set
    # The address should be a full URL
    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # Validate the given blockchain by comparing hashes and proof of work
    # Check that the blocks are properly chained and proof of work conditions are satisfied
    def is_valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_pow(last_block['pow'], block['pow']):
                return False

            last_block = block
            current_index += 1

        return True

    # Resolve conflicts between nodes by comparing chains
    # Fetch the chain from all neighbors and update the local chain if a longer valid chain is found
    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    if length > max_length and self.is_valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.RequestException:
                continue

        if new_chain:
            self.chain = new_chain
            return True

        return False

    # Create a new block and add it to the blockchain
    # The block contains the current transactions, a proof of work, and a link to the previous block's hash
    def new_block(self, pow, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'pow': pow,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    # Add a new transaction to the list of current transactions
    # It requires a valid signature and returns the index of the block that will include this transaction
    def new_transaction(self, sender, recipient, amount, signature):
        if not self.verify_signature(sender, recipient, amount, signature):
            raise ValueError("Invalid signature")

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'signature': signature
        })
        return self.last_block['index'] + 1

    # Add a notarization transaction to the current transactions
    # Store the document hash, owner, and timestamp in the blockchain
    def notarize_document(self, document_hash, owner):
        self.current_transactions.append({
            'type': 'notarization',
            'document_hash': document_hash,
            'owner': owner,
            'timestamp': time()
        })
        return self.last_block['index'] + 1

    # Return the last block in the blockchain
    @property
    def last_block(self):
        return self.chain[-1]

    # Calculate the hash of a given block using SHA-256
    # Convert the block to a string and sort it to ensure consistent hash results
    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    # Solve the proof of work for a given last proof (previous block's pow)
    # Try different values until the hash meets the predefined condition of leading zeros
    def proof_of_work(self, last_pow):
        pow = 0
        while self.valid_proof(last_pow, pow) is False:
            pow += 1
        return pow

    # Verify if a given proof of work is valid by checking if the hash starts with four leading zeros
    @staticmethod
    def valid_proof(last_pow, pow):
        guess = f'{last_pow}{pow}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    # Verify the signature of a transaction using the sender's public key
    # Ensure that the signature matches the data (sender, recipient, amount) using RSA verification
    @staticmethod
    def verify_signature(sender, recipient, amount, signature):
        try:
            sender_key = serialization.load_pem_public_key(sender.encode())
            transaction_data = f'{sender}{recipient}{amount}'.encode()
            sender_key.verify(
                base64.b64decode(signature),
                transaction_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception as e:
            return False

    # Return the balance of a given wallet address by checking all transactions in the blockchain
    # Calculate the total balance by summing incoming and outgoing transactions for the address
    def get_balance(self, wallet_address):
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == wallet_address:
                    balance -= transaction['amount']
                if transaction['recipient'] == wallet_address:
                    balance += transaction['amount']
        return balance


# Generate a new RSA key pair (public and private keys)
# Return the private key and public key in PEM format
def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()

    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_key_pem, public_key_pem


# Sign transaction data using the sender's private key
# Sign the transaction data and return the base64-encoded signature
def sign_transaction(private_key_pem, sender, recipient, amount):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )
    transaction_data = f'{sender}{recipient}{amount}'.encode()
    signature = private_key.sign(
        transaction_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


# Generate a wallet address and possible recipient addresses for the user
# Use UUID to create random identifiers for the wallet and three possible recipient addresses
# Print the wallet address and the list of possible recipients for reference
def generate_and_print_addresses():
    """
    Generate the node identifier (wallet address) and print possible recipient addresses
    This function encapsulates the logic to avoid exposing it in the open
    """
    node_identifier = str(uuid4()).replace('-', '')
    # For now, just using the same method to generate random possible recipient addresses
    possible_recipients = [str(uuid4()).replace('-', '') for _ in range(3)]

    print(f"Your wallet address (node identifier): {node_identifier}")
    print(f"Possible recipient addresses: {', '.join(possible_recipients)}")

    return node_identifier, possible_recipients


# Flask application setup and entry point
def create_app():
    app = Flask(__name__)

    # Generate the node identifier (wallet address) and possible recipient addresses
    # Print the generated wallet address and possible recipient addresses for the user
    node_identifier, possible_recipients = generate_and_print_addresses()

    # Initialize the blockchain
    blockchain = Blockchain()

    @app.route('/')
    def home():
        return jsonify({
            'available_routes': {
                '/transactions/new': 'Create a new transaction (POST)',
                '/notarize': 'Notarize a document (POST)',
                '/verify_document': 'Verify if a document is notarized (POST)',
                '/balance': 'Check wallet balance (GET)',
                '/chain': 'Get the blockchain data (GET)',
                '/nodes/register': 'Register a new node (POST)',
                '/nodes/resolve': 'Resolve conflicts between nodes (POST)',
            }
        })

    # Define the route to create a new transaction
    @app.route('/transactions/new', methods=['POST'])
    def new_transaction():
        values = request.get_json()

        # Check if the required fields (sender, recipient, amount, signature) are present in the request
        required = ['sender', 'recipient', 'amount', 'signature']
        if not all(k in values for k in required):
            return 'Missing values', 400

        try:
            print(f"Sender's address: {values['sender']}")
            print(f"Possible recipient addresses: {', '.join(possible_recipients)}")

            # Create a new transaction and return the index of the block that will include it
            index = blockchain.new_transaction(
                values['sender'], values['recipient'], values['amount'], values['signature']
            )
        except ValueError as e:
            return str(e), 400

        response = {'message': f'Transaction will be added to block {index}'}
        return jsonify(response), 201

    # Define the route to retrieve the entire blockchain
    @app.route('/chain', methods=['GET'])
    def full_chain():
        # Return the entire blockchain and its length
        response = {
            'chain': blockchain.chain,
            'length': len(blockchain.chain),
        }
        return jsonify(response), 200

    # Define the route to notarize a document
    @app.route('/notarize', methods=['POST'])
    def notarize_document():
        values = request.get_json()

        # Check if the required fields (document_hash, owner) are present in the request
        required = ['document_hash', 'owner']
        if not all(k in values for k in required):
            return 'Missing values', 400

        # Add a notarization transaction and return the index of the block where it will be included
        index = blockchain.notarize_document(values['document_hash'], values['owner'])

        response = {'message': f'Document will be notarized in block {index}'}
        return jsonify(response), 201

    # Define the route to verify if a document is notarized
    @app.route('/verify_document', methods=['POST'])
    def verify_document():
        values = request.get_json()

        # Check if the required field (document_hash) is present in the request
        required = ['document_hash']
        if not all(k in values for k in required):
            return 'Missing values', 400

        # Search through the blockchain for notarized documents and verify ownership
        document_hash = values['document_hash']
        notarized = False
        for block in blockchain.chain:
            for transaction in block['transactions']:
                if transaction.get('type') == 'notarization' and transaction.get('document_hash') == document_hash:
                    notarized = True
                    owner = transaction['owner']
                    timestamp = transaction['timestamp']
                    break
            if notarized:
                break

        if notarized:
            response = {
                'message': 'Document is notarized',
                'owner': owner,
                'timestamp': timestamp
            }
        else:
            response = {'message': 'Document not found in the blockchain'}

        return jsonify(response), 200

    # Route to check the balance of a specific wallet address
    @app.route('/balance', methods=['GET'])
    def get_balance():
        # Get the wallet address from the request query parameters
        wallet_address = request.args.get('wallet_address')

        # Check if the wallet_address parameter is provided
        if not wallet_address:
            return 'Missing wallet_address parameter', 400

        print(f"Checking balance for wallet address: {wallet_address}")
        balance = blockchain.get_balance(wallet_address)

        response = {'wallet_address': wallet_address, 'balance': balance}
        return jsonify(response), 200

    # Define the route to register a new node in the blockchain network
    @app.route('/nodes/register', methods=['POST'])
    def register_node():
        # Get the node address from the incoming JSON request
        values = request.get_json()

        required = ['node']
        if not all(k in values for k in required):
            return 'Missing node parameter', 400

        node = values['node']
        blockchain.register_node(node)

        response = {
            'message': f'Node {node} has been registered',
            'nodes': list(blockchain.nodes)
        }
        return jsonify(response), 201

    # Resolve conflicts between nodes (i.e., synchronizing chains)
    @app.route('/nodes/resolve', methods=['POST'])
    def resolve():
        # Try to resolve conflicts and update the blockchain if a longer valid chain is found
        replaced = blockchain.resolve_conflicts()

        if replaced:
            response = {
                'message': 'Chain was replaced with the longest valid chain',
                'new_chain': blockchain.chain
            }
        else:
            response = {
                'message': 'Chain is up to date',
                'new_chain': blockchain.chain
            }

        return jsonify(response), 200

    return app


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()

    app = create_app()
    app.run(host='0.0.0.0', port=args.port)
