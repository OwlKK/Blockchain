import hashlib
import time
import random


class Transaction:
    def __init__(self, sender, recipient, amount, timestamp=None, fee=0, message=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp or time.time()
        self.fee = fee
        self.message = message  # User-defined message
        self.transaction_hash = self.compute_transaction_hash()

    def compute_transaction_hash(self):
        return hashlib.sha256(
            f"{self.sender}{self.recipient}{self.amount}{self.timestamp}{self.fee}{self.message}".encode()).hexdigest()


class Block:
    def __init__(self, previous_hash, transactions, proof, timestamp=None, creator=None):
        self.timestamp = timestamp or time.time()
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.proof = proof
        self.creator = creator


class SmartContract:
    def __init__(self, condition, action):
        self.condition = condition
        self.action = action

    def execute(self, transaction):
        if self.condition(transaction):
            self.action(transaction)


class Node:
    def __init__(self, node_id, balance=100):
        self.node_id = node_id
        self.balance = balance
        self.address = hashlib.sha256(str(node_id).encode()).hexdigest()


def hash(block):
    return hashlib.sha256(str(block.__dict__).encode()).hexdigest()


class EthereumBlockchain:
    def __init__(self, block_size_limit=5, transaction_fee_rate=0.1,
                 stake_multiplier=0.1, default_stake=50):
        self.chain = []
        self.pending_transactions = []
        self.smart_contracts = []
        self.block_size_limit = block_size_limit
        self.transaction_fee_rate = transaction_fee_rate
        self.stake_multiplier = stake_multiplier
        self.default_stake = default_stake
        self.nodes = []
        self.seen_transactions = set()  # Set to track already seen transactions

    def create_genesis_block(self):
        genesis_block = Block(previous_hash="1", transactions=[], proof=0, creator="Genesis Node")
        self.chain.append(genesis_block)

    def create_block(self, proof, previous_hash=None):
        block = Block(previous_hash or hash(self.chain[-1]),
                      self.pending_transactions, proof, creator="Miner")
        self.pending_transactions = []
        self.chain.append(block)
        return block

    def create_transaction(self, sender, recipient, amount):
        if amount > sender.balance:
            print("Transaction failed: Insufficient funds.")
            return
        transaction = Transaction(sender.address, recipient.address, amount,
                                  fee=self.calculate_transaction_fee(amount))

        # Prevent double spending
        if transaction.transaction_hash in self.seen_transactions:
            print(f"Transaction {transaction.transaction_hash} already processed (Double Spending detected).")
            return

        self.pending_transactions.append(transaction)
        self.seen_transactions.add(transaction.transaction_hash)  # Add transaction hash to seen set

        sender.balance -= amount + transaction.fee
        recipient.balance += amount
        return transaction

    def mine_block(self, consensus="pow"):
        if consensus == "pow":
            last_block = self.chain[-1]
            last_proof = last_block.proof
            proof = self.proof_of_work(last_proof)
            block = self.create_block(proof)
            print(f"Block mined with Proof-of-Work: {block.__dict__}")
            return block
        elif consensus == "pos":
            creator = self.select_block_creator()
            last_block = self.chain[-1]
            last_proof = hash(last_block)
            proof = self.proof_of_stake(last_proof, creator)
            block = self.create_block(proof)
            print(f"Block mined with Proof-of-Stake: {block.__dict__}")
            return block

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def proof_of_stake(self, last_proof, creator):
        selected_node = self.get_node_by_id(creator)
        if selected_node is not None:
            proof = random.uniform(0, 1) * self.stake_multiplier * selected_node.balance
            return proof
        else:
            print(f"Node with ID {creator} not found. Using a default stake.")
            return random.uniform(0, 1) * self.stake_multiplier * self.default_stake

    def select_block_creator(self):
        total_stake = sum(node.balance for node in self.get_all_nodes())
        random_stake = random.uniform(0, total_stake)
        current_sum = 0
        for node in self.get_all_nodes():
            current_sum += node.balance
            if current_sum >= random_stake:
                return node.node_id

    def get_all_nodes(self):
        return [node for node in self.nodes]

    def get_node_by_id(self, node_id):
        # Get the node by node_id
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def calculate_transaction_fee(self, amount):
        return amount * self.transaction_fee_rate  # Transaction fee calculation


# Smart Contract Example for Fee Threshold
def fee_threshold_condition(transaction):
    return transaction.fee > 10  # Example condition: fee exceeds 10


def fee_threshold_action(transaction):
    print(f"Warning: High transaction fee detected! Fee: {transaction.fee}")


# New Smart Contract Example for Transaction Amount Threshold
def amount_threshold_condition(transaction):
    return transaction.amount > 100  # Example condition: amount exceeds 100


def amount_threshold_action(transaction):
    print(f"Warning: Large transaction amount detected! Amount: {transaction.amount}")


# Example Usage:
ethereum = EthereumBlockchain()
ethereum.create_genesis_block()

# Create Nodes
alice = Node("Alice", balance=200)
bob = Node("Bob", balance=150)

# Add nodes to the blockchain
ethereum.nodes.extend([alice, bob])

# Transactions
tx1 = ethereum.create_transaction(alice, bob, 50)
tx2 = ethereum.create_transaction(bob, alice, 30)
tx3 = ethereum.create_transaction(alice, bob, 150)  # Large transaction to trigger smart contract

# Create and execute smart contracts for high fee and large transaction amount
high_fee_contract = SmartContract(fee_threshold_condition, fee_threshold_action)
high_fee_contract.execute(tx1)

large_amount_contract = SmartContract(amount_threshold_condition, amount_threshold_action)
large_amount_contract.execute(tx3)

# Mine a Block using Proof-of-Work
ethereum.mine_block(consensus="pow")


# Viewing Wallet Balances
def view_wallet_balances(blockchain):
    for node in blockchain.get_all_nodes():
        print(f"Node {node.node_id} ({node.address}) balance: {node.balance}")


# Viewing wallet balances
view_wallet_balances(ethereum)


# Block Explorer
def block_explorer(blockchain):
    for i, block in enumerate(blockchain.chain):
        print(f"\nBlock {i}: {block.__dict__}")


# Explore Blockchain
block_explorer(ethereum)
