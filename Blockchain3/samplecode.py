import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash="1", proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes.
        :param address: Address of the node (e.g., 'http://127.0.0.1:5000')
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # Determine if a given blockchain is valid by verifying the hashes and proof of work.
    def is_valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is the consensus algorithm. It resolves conflicts by replacing
        the chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        # Only look for chains longer than current
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in the network
        for node in neighbours:
            try:
                response = requests.get(f'http://{node}/chain')

                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']

                    # Check if the length is longer and the chain is valid
                    if length > max_length and self.is_valid_chain(chain):
                        max_length = length
                        new_chain = chain
            except requests.RequestException:
                continue

        # Replace current chain if new and valid chain is longer than current
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash=None):
        # Create a new block in the blockchain
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        # Create a new transaction to go into the next mined block
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        # Return the last block in the chain
        return self.chain[-1]

    @staticmethod
    def hash(block):
        # Hash a block
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        # Find a number p' such that hash(pp') contains 0000____
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        # Check if the hash of the proof contains 0000___
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


app = Flask(__name__)

# Generate a unique address for this node
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # Reward for finding the proof
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)

    # Create a new block
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New block forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


# Calculate the balance of a specific wallet by summing up all transactions
# involving the address across the blockchain.
@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = 0

    # Move through all blocks and their transactions
    for block in blockchain.chain:
        for transaction in block['transactions']:
            if transaction['recipient'] == address:
                balance += transaction['amount']
            if transaction['sender'] == address:
                balance -= transaction['amount']

    response = {
        'address': address,
        'balance': balance,
    }
    return jsonify(response), 200


'''Invoke-RestMethod -Uri http://127.0.0.1:5000/nodes/register -Method POST -Body (@{nodes=@("http://127.0.0.1:5001", 
 "http://127.0.0.1:5002")} | ConvertTo-Json) -ContentType "application/json" 

 
 Outputs:
 
 message                   total_nodes
-------                   -----------
New nodes have been added {127.0.0.1:5002, 127.0.0.1:5001}
'''


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='0.0.0.0', port=port)
