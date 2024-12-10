import hashlib
import datetime


class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, "0", datetime.datetime.now(), "Genesis Block",
                              self.calculate_hash(0, "0", datetime.datetime.now(), "Genesis Block"))

        self.chain.append(genesis_block)

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_index = previous_block.index + 1
        new_timestamp = datetime.datetime.now()
        new_hash = self.calculate_hash(new_index, previous_block.hash,
                                       new_timestamp, data)
        new_block = Block(new_index, previous_block.hash, new_timestamp, data,
                          new_hash)
        self.chain.append(new_block)

    def calculate_hash(self, index, previous_hash, timestamp, data):
        hash_data = str(index) + previous_hash + str(timestamp) + data

        return hashlib.sha256(hash_data.encode()).hexdigest()

    def print_chain(self):
        for block in self.chain:
            print(f"Block {block.index} - Timestamp: {block.timestamp} - Data:{block.data} - Hash: {block.hash}")


if __name__ == "__main__":
    # Create a blockchain
    blockchain = Blockchain()

    # Add blocks to the blockchain
    blockchain.add_block("Transaction 1")
    blockchain.add_block("Transaction 2")
    blockchain.add_block("Transaction 3")

    # Print the entire blockchain
    blockchain.print_chain()
